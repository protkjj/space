# ROS 2 workspace

This ROS 2 Jazzy workspace contains the rover's physical description,
simulation assets, bringup, command safety, perception, and the Phase 1
ArduPilot interface scaffold.

The supported baseline is Ubuntu 24.04, ROS 2 Jazzy, and Gazebo Harmonic.
Exactly the six packages listed below are active.

## Packages

| Package | Responsibility |
| --- | --- |
| `space_description` | Canonical physical links, joints, inertial properties, wheel geometry, and sensor mounting transforms |
| `space_gazebo` | Gazebo-only wrapper, plugins, friction and sensor configuration, ROS–Gazebo bridge configuration, and worlds |
| `space_bringup` | System-level simulation and hardware launch orchestration |
| `space_controller` | Backend-neutral command clipping, mode gate, and stale-command watchdog |
| `space_perception` | RGB-D operator overlay, measured cloud filtering, and local elevation mapping |
| `space_ardupilot_interface` | Buildable Phase 1 scaffold for the future ArduPilot DDS adapter |

`space_description` must not depend on `space_gazebo`. Simulation composes the
canonical physical model by including it from the Gazebo-side wrapper.

## Command boundary

The stable Phase 1 command boundary is:

```text
/cmd_vel_in  geometry_msgs/msg/Twist
    → command_safety_node
/cmd_vel_safe geometry_msgs/msg/Twist
    → selected backend
```

The Phase 1 simulator remaps/configures its temporary DiffDrive backend to
consume `/cmd_vel_safe`. The future ArduPilot adapter will subscribe to
`/cmd_vel_safe`, validate and stamp the command, and publish
`geometry_msgs/msg/TwistStamped` on `/ap/cmd_vel`. That adapter is not
implemented in Phase 1.

## Build and test

```bash
source /opt/ros/jazzy/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
colcon test
colcon test-result --all --verbose
source install/setup.bash
```

The whole workspace should be built together. The old PX4 package and
`px4_msgs` dependency have been removed; the ArduPilot scaffold does not yet
require `ardupilot_msgs`.

## Phase 1 simulation

```bash
source install/setup.bash
ros2 launch space_bringup simulation.launch.py
```

The simulator still moves the rover through a direct Gazebo DiffDrive plugin.
This temporary path preserves simulation capability during the refactor and
does not demonstrate ArduPilot or Pixhawk control.

The default world is `arena_test_slope_v04.sdf`; its generated STL assets must
first be produced as documented in
[`../docs/arena_simulation.md`](../docs/arena_simulation.md). Use
`use_rviz:=false`, `use_perception:=false`, or `use_navigation:=true` to change
optional launch components. Navigation defaults off until its full graph is
validated against the arena.

With `use_perception:=true`, the simulation also launches the sensor-derived
`/camera/points → /terrain/filtered_points → /terrain/elevation_points →
/terrain/features` pipeline and compact elevation/feature markers. The feature
cloud contains slope, roughness, plane-removed step height, coverage, and
data-quality confidence. `/terrain/traversability` adds continuous normalized
penalties, a prototype score, validity, and a dominant limiting-factor code.
It is not a guaranteed safety classification and does not implement hazard
decisions, marker recommendations, or Nav2 terrain costs.
Nav2 terrain-cost integration remains gated on calibration and physical
validation; current response and latency data are in
`../docs/traversability_calibration.md`.

## Phase 1 hardware launch

```bash
source install/setup.bash
ros2 launch space_bringup hardware.launch.py
```

This launch is for description and interface inspection only. It must not open
a serial connection, generate PWM, command RoboClaw directly, or control a
marker actuator. Until an ArduPilot backend is implemented,
`/cmd_vel_safe` intentionally has no actuator consumer.

## Milestone boundary

Phase 1 stops at the buildable scaffold and temporary simulation. Milestone A
will introduce ArduPilot Rover SITL, the official ArduPilot Gazebo plugin, DDS
state/control, and ArduPilot-authoritative movement. Milestone B will add a
semantic simulated marker mechanism. See
[`../docs/simulation_milestones.md`](../docs/simulation_milestones.md).
