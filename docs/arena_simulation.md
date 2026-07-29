# Arena CAD simulation

## Source inspection

The authoritative asset is
`space_gazebo/assets/source_cad/arena_test_slope_v04.stp`, copied byte-for-byte
from the repository-root download. Gazebo and RViz never load STEP directly.

The AP214 header identifies Autodesk Inventor 2023 and millimetres
(`SI_UNIT(.MILLI.,.METRE.)`). The file contains one `MANIFOLD_SOLID_BREP`, one
closed shell, and no assembly occurrence. Its 95 explicit Cartesian points span:

| Axis | Minimum (mm) | Maximum (mm) | Span (mm) |
| --- | ---: | ---: | ---: |
| X | -800 | 2400 | 3200 |
| Y | approximately 0 | 550 | 550 |
| Z | -4000 | 0 | 4000 |

This is a closed solid and includes the arena floor and raised slope geometry.
The thin Y extent and broad X/Z extents identify the source as Y-up. Runtime
assets are rotated +90 degrees around X, mapping `(X,Y,Z)` to `(X,-Z,Y)`.
Their resulting Gazebo footprint is 3.2 × 4.0 m and height is 0.55 m.
The model offset `(-0.8, -2.0, 0)` centres that footprint at the world origin.

FreeCAD 1.1.1 imported one object containing one valid, closed solid and one
shell. Independent Trimesh 4.12.2 inspection found one connected component,
consistent winding, no degenerate faces, and watertight visual and collision
meshes.

## Repeatable conversion

The verified portable FreeCAD console invocation is:

```bash
/home/leo11dk/Applications/FreeCAD-1.1.1/squashfs-root/AppRun \
  freecadcmd tools/convert_arena_step.py
```

Run it from `ros2_ws/src/space_gazebo` to regenerate both meshes:

```bash
cd ros2_ws/src/space_gazebo
/home/leo11dk/Applications/FreeCAD-1.1.1/squashfs-root/AppRun \
  freecadcmd tools/convert_arena_step.py
```

The script reports imported objects, valid shapes, solids, shells, closure and
the OpenCASCADE bounding box, then creates:

- `arena_visual.stl`: 46 vertices and 88 triangles
- `arena_collision.stl`: 29 vertices and 54 triangles

All CAD faces are planar, so tolerance alone produces the exact minimal
54-triangle surface. The visual mesh receives one deterministic planar
refinement pass for display density; this does not change the terrain shape.
STL has no unit metadata, so vertices remain in authoritative millimetres and
both Gazebo and RViz explicitly apply scale `0.001`. The tool never writes the
STEP source.

## Running

After conversion and a workspace build:

```bash
source /opt/ros/jazzy/setup.bash
cd ros2_ws
colcon build --symlink-install
source install/setup.bash
ros2 launch space_bringup simulation.launch.py
```

The CAD slope world can be selected explicitly with
`world:=arena_test_slope_v04.sdf`; it contains the CAD floor and therefore adds
no ground plane. When using that world, pass `spawn_z:=0.12`. Mesh intersection
measures its starting surface top at 0.10 m. The rover wheel bottom is −0.005 m
relative to `base_footprint`, so a 0.12 m spawn starts 0.015 m above contact and
settles under physics. The simulation default is now `arena_terrain_v04.sdf`
with `spawn_z:=0.23`.

RViz starts by default with fixed frame `odom`. To run it separately:

```bash
rviz2 -d "$(ros2 pkg prefix space_bringup)/share/space_bringup/rviz/rover_simulation.rviz"
```

The arena marker is engineering ground-truth reference only. Terrain autonomy
must instead follow the planned sensor-driven flow:

```text
OAK-D depth / PointCloud2
  → point-cloud filtering
  → frame transformation
  → elevation representation
  → slope, roughness, step-height, and uncertainty features
  → traversability score
  → Nav2 costmap integration
  → hazard and marker-drop decisions
```

The sensor prototype now publishes `/terrain/filtered_points`,
`/terrain/elevation_points`, and `/terrain/elevation_markers`. Candidate
`/terrain/traversability`, `/terrain/hazards`, and
`/terrain/recommended_marker_locations` interfaces remain planned only;
nothing publishes them.

## Visual acceptance checklist

Gazebo:

- arena footprint appears approximately 3.2 × 4.0 m
- maximum elevation appears approximately 0.55 m
- slope rises in the intended direction
- rover begins on the intended starting surface
- rover wheels contact the terrain without floating or sinking
- rover drives forward in body-X
- collision follows the visible slope

RViz:

- RobotModel aligns with the Gazebo pose
- arena Marker orientation matches Gazebo
- point cloud appears in front of the OAK-D frame
- odometry direction matches rover motion
- TF axes are consistent

Known limitations: final appearance still requires the checklist above; no
traversability, marker deployment, ArduPilot DDS, or SITL behavior is
implemented.
