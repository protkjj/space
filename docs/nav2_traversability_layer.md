# Nav2 traversability layer

## Scope and ownership

`space_perception::TraversabilityLayer` is a C++ `nav2_costmap_2d::CostmapLayer`
plugin owned by the existing `space_perception` package. That package is now a
mixed `ament_cmake`/`ament_cmake_python` package: CMake builds and exports the
plugin, `ament_cmake_python` installs the existing Python module, and explicit
wrappers preserve all six previous `ros2 run space_perception ...` executables.
No seventh ROS package was created.

The plugin affects only the rolling local costmap. The global costmap remains
unchanged. This is soft local trajectory information, not a terrain safety
classification and not global terrain planning.

## Input contract

The BEST_EFFORT, KEEP_LAST, depth-1 subscription reads
`/terrain/traversability` as `sensor_msgs/msg/PointCloud2`. It requires the
fields `x`, `y`, `z`, `traversability`, `slope_penalty`,
`roughness_penalty`, `step_penalty`, `uncertainty_penalty`, `confidence`,
`valid`, and `limiting_factor` with the production datatypes.

Malformed clouds are rejected with throttled warnings. Duplicate stamps are
skipped. Inputs older than `maximum_input_age` are rejected when
`drop_stale_input` is true. Invalid cells (`valid=0`, NaN score, limiting
factor 255), non-finite coordinates, and out-of-map points produce no
terrain-layer contribution. That neutral state means **no terrain-layer
contribution**, not terrain confirmed free.

The cloud frame is compared with the costmap global frame. If different, one
timestamped transform is acquired for the complete cloud and applied to all
points. The plugin never substitutes the latest transform and never performs
one lookup per cell.

## Score-to-cost mapping

For a valid score `t`, the provisional simulation mapping is:

```text
penalty = clamp(1 - t, 0, 1)
normalized = penalty ^ cost_exponent
cost = round(cost_min + normalized * (cost_max - cost_min))
```

The initial parameters are `cost_min=1`, `cost_max=180`, and
`cost_exponent=1.0`. Thus score 1 maps to 1 and score 0 maps to 180.
All outputs are below Nav2's inscribed (253), lethal (254), and unknown (255)
values. `minimum_traversability=0.0` is inert because its gate defaults false;
enabling the gate skips lower scores and does not make them lethal.

When multiple points enter one cell, the highest cost wins deterministically.
The internal grid is reset for every replacement cloud, resize, and rolling
origin rebuild. Stale data clears the grid when `clear_on_stale=true`, so the
layer stores no history and leaves no rover-motion trail.

## Combination and plugin order

The local order is:

1. `static_layer`
2. `obstacle_layer`
3. `traversability_layer`
4. `inflation_layer`

Combination method 1 uses Nav2 max combination. Terrain cannot reduce an
existing obstacle or inflation cost. Inflation remains last and can expand
obstacle costs normally. Method 2 additionally avoids replacing an unknown
master cell. Overwrite and additive modes are intentionally unsupported.

## Parameters

All values are provisional simulation tuning.

| Parameter | Default | Meaning |
| --- | ---: | --- |
| `enabled` | true | Enable contribution without rebuilding |
| `input_topic` | `/terrain/traversability` | Input cloud |
| `maximum_input_age` | 1.0 s | Freshness limit |
| `drop_stale_input` | true | Reject stale callbacks |
| `cost_min` | 1 | Lowest soft raw cost |
| `cost_max` | 180 | Highest soft raw cost |
| `cost_exponent` | 1.0 | Continuous response shape |
| `minimum_traversability` | 0.0 | Optional skip threshold |
| `use_minimum_traversability_gate` | false | Enable the skip threshold |
| `combination_method` | 1 | Max combination |
| `transform_tolerance` | 0.2 s | Timestamped TF wait |
| `clear_on_stale` | true | Remove expired contributions |
| `publish_debug_grid` | false | Publish inspection-only grid |

`simulation.launch.py` exposes `use_traversability_layer`; false restores the
previous local-costmap contribution behavior. Hardware launch does not start
Nav2 and does not force this plugin.

## Inspection and diagnostics

When enabled, `/terrain/nav2_costs` is a debug `OccupancyGrid` in the local
costmap frame and geometry. `-1` is no contribution. It is not the integration
path and publication defaults off. `/terrain/nav2_cost_diagnostics` reports
input age, callback/update durations, processed/written cells, and duplicate,
stale, malformed, and TF failure counters.

RViz includes the local costmap, optional debug grid, traversability markers,
footprint, global path, and local plan. Display configuration was validated
programmatically; colours, layering, and trajectory appearance still require
human visual confirmation.

## Validation

At the normal spawn, the plugin processed 483 cells and wrote 194. Measured
durations were 0.017 ms callback, 0.007 ms `updateBounds`, and 0.005 ms
`updateCosts`, far below the 200 ms update period. Full local costmap
publication measured about 1.67 Hz under combined Gazebo/Nav2 load against a
configured 2 Hz; traversability input measured about 3.05 Hz. No queue growth
was observed.

Representative live comparisons follow. “Raw terrain” is the internal Nav2
cost before OccupancyGrid's standard 0–100 display translation.

| Coordinate (odom) | Score / valid | Limiter | Raw terrain | Final display |
| --- | --- | ---: | ---: | ---: |
| (0.125, -1.225) | 0.716 / 1 | low confidence | 52 | 20 |
| (0.575, -1.375) | 0.865 / 1 | low confidence | 25 | 10 |
| (0.125, -1.775) | 0.927 / 1 | low confidence | 14 | 6 |
| (0.275, -1.975) | NaN / 0 | invalid | none | 0 |

No valid terrain cell became lethal. Existing obstacle/inflation preservation
is covered by unit tests. After traversability input stopped, all three
terrain cells above cleared to zero after the one-second timeout. During a
0.08 m/s command, odometry advanced 0.114 m, the rolling origin advanced by
0.05 m, and the watchdog restored zero command after 0.5 seconds.

The disabled and enabled runs both accepted an identical short Nav2 goal and
both aborted with error 107 before motion. The existing local static layer
rejected the initial SLAM map as malformed in that comparison, so no valid
terrain-dependent controller response or avoidance claim can be made. At the
default negative spawn, the initial global SLAM map also did not contain the
rover. These are navigation-baseline limitations, not evidence that DWB
responds to the soft terrain costs.

## Launch

```bash
source /opt/ros/jazzy/setup.bash
cd /home/leo11dk/Desktop/space/ros2_ws
source install/setup.bash

# Baseline, no Nav2
ros2 launch space_bringup simulation.launch.py \
  use_navigation:=false

# Nav2 with terrain soft costs
ros2 launch space_bringup simulation.launch.py \
  use_navigation:=true use_traversability_layer:=true

# Nav2 comparison without terrain contribution
ros2 launch space_bringup simulation.launch.py \
  use_navigation:=true use_traversability_layer:=false
```

## Deliberate limitations

Implemented: local Nav2 soft-cost integration, dynamic terrain-layer clearing,
an interpretable bounded mapping, diagnostics, and optional debug output.

Not implemented: lethal terrain classification, guaranteed terrain avoidance,
global terrain planning, hazard persistence, marker recommendation or
deployment, wheel-slip integration, ArduPilot control, RoboClaw communication,
CAD-derived runtime costs, or autonomous mission management.
