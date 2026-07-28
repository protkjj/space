# Sensor-derived terrain perception

## Implemented pipeline

The current prototype uses only the simulated RGB-D measurements:

```text
/camera/points (camera_link)
  → terrain_pointcloud_filter_node
  → /terrain/filtered_points (odom)
  → local_elevation_map_node
  ├── /terrain/elevation_points (odom)
  └── /terrain/elevation_markers (odom)
  → terrain_feature_node
  └── /terrain/features and feature markers (odom)
  → terrain_traversability_node
  └── /terrain/traversability and compact markers (odom)
```

The arena STL is not opened or read by either node. CAD dimensions are used
only after runtime as validation ground truth.

## Filtering

The filter processes at most 5 Hz and uses the cloud timestamp for TF. It
performs one `camera_link → odom` lookup and one `odom → base_footprint`
lookup, then uses vectorized NumPy operations to:

1. remove NaN and infinite XYZ values;
2. keep sensor ranges from 0.15 through 4.0 m;
3. transform valid points into `odom`;
4. apply a `base_footprint`-relative crop:
   X 0.10…3.60 m, Y −2.0…2.0 m, Z −0.60…1.20 m;
5. exclude the configured rover-body box; and
6. produce deterministic 0.03 m voxel centroids.

No output is fabricated when input or TF is unavailable. TF warnings are
limited to once per five seconds. The simulator publishes the point cloud in
X-forward/Y-left/Z-up `camera_link` coordinates. A standard
`camera_optical_frame` also exists, but it does not label this Gazebo cloud.

## Local elevation grid

The grid is rover-centred, 4 × 4 m, has 0.05 m cells, and remains aligned with
`odom`. Points are assigned to global odom-aligned integer cells. Cells with
fewer than two measured points are rejected. Valid cells contain:

- median measured elevation;
- population variance of measured elevation;
- measured point count.

Measurements are retained for two seconds and only while inside the moving
local extent. Unknown cells are not filled or published. Each output update
uses one compact `CUBE_LIST` and begins its MarkerArray with `DELETEALL`,
preventing marker accumulation.
Marker color is a display-only mapping between configured visualization
heights 0 and 0.55 m; it is not a terrain score.

`/terrain/elevation_points` fields are:

| Field | Type | Offset |
| --- | --- | ---: |
| `x` | FLOAT32 | 0 |
| `y` | FLOAT32 | 4 |
| `z` | FLOAT32 | 8 |
| `variance` | FLOAT32 | 12 |
| `point_count` | UINT32 | 16 |

## Parameters and diagnostics

Defaults are installed in
`space_perception/config/terrain_perception.yaml`. Both nodes publish status
records on `/terrain/diagnostics`, including input/TF state, point and cell
counts, processing time, and effective rate.

The initial stationary elevation-only run measured:

- 307,200 raw points per cloud;
- 133,431 finite in-range points;
- approximately 2,455 filtered voxel points;
- approximately 484 valid elevation cells;
- filter processing commonly 46–64 ms;
- elevation processing commonly 24–105 ms including Marker construction;
- sustained effective rates around 3–3.6 Hz under combined Gazebo, bridge,
  perception, and validation load.

A synthetic 500-cell benchmark reduced elevation marker construction from
15.35 ms to 3.11 ms by replacing one marker per cell with a `CUBE_LIST`.
Feature definitions and current feature runtime measurements are documented in
[`terrain_features.md`](terrain_features.md).

The configured ceiling is 5 Hz. Intermittent millisecond-scale TF
extrapolation misses are skipped safely and reduce the measured rate.

## Arena validation

The rover followed the arena’s lower Y-side slope using conservative
0.08 m/s commands:

| Observation | Rover XYZ (m) | Pitch (rad) | Cells | Elevation min/median/max (m) |
| --- | --- | ---: | ---: | --- |
| Lower section, looking toward slope | −1.200, −1.600, 0.105 | 0.000 | 484 | 0.100 / 0.169 / 0.237 |
| Slope beginning | −0.805, −1.600, 0.111 | −0.042 | 461 | 0.100 / 0.220 / 0.302 |
| Higher slope section | −0.253, −1.600, 0.153 | −0.087 | 446 | 0.207 / 0.240 / 0.286 |

The observed elevation range is plausible within the CAD’s 0…0.55 m global
range. The progressive median increase is consistent with the visible slope.
This is engineering validation, not a claim of millimetre accuracy.

The simulation now publishes 3D odometry so `odom → base_footprint` retains
the measured rover height and attitude. Without that, transformed terrain
heights were incorrectly offset as the rover climbed.

## Running

```bash
source /opt/ros/jazzy/setup.bash
cd ros2_ws
source install/setup.bash
ros2 launch space_bringup simulation.launch.py
```

The terrain nodes can be launched without Gazebo when a compatible cloud and
TF tree already exist:

```bash
ros2 launch space_perception terrain_perception.launch.py
```

## Current limitations

- Exact-time TF can occasionally lag a cloud by a few milliseconds; that cloud
  is skipped instead of being transformed with the wrong pose.
- The local grid retains recent measured cells but performs no interpolation.
- A provisional continuous traversability model is implemented downstream.
  No guaranteed safety classification, hazard decision, marker
  recommendation, Nav2 terrain cost, ArduPilot, or RoboClaw behavior is
  implemented.
- Gazebo and RViz appearance still requires user visual confirmation.

The feature layer consumes elevation, variance, and point count without
changing this measured-data contract.
