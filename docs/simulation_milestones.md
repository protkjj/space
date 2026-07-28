# Simulation milestones

Acceptance is intentionally split. Phase 1 preserves a working temporary
simulation and prepares the repository for Milestone A. Marker deployment is a
separate Milestone B.

## Phase 1: repository foundation

Phase 1 acceptance covers:

- replacing the PX4 package with a buildable ArduPilot interface scaffold
- separating Gazebo-only assets from the canonical physical description
- separate simulation and hardware bringup
- a backend-neutral `/cmd_vel_safe` boundary
- a stateful command watchdog with periodic zero publication while stale,
  HOLD, or EMERGENCY
- documentation and package metadata correction
- ArduPilot firmware provenance structure without invented `.param` files
- successful available build, lint, unit, Xacro/URDF/SDF, and launch checks
- a repeatable arena STEP-to-mesh pipeline, Gazebo world, and RViz reference
  workflow; actual meshes remain gated on an available FreeCAD kernel
- a sensor-derived filtered point cloud and local elevation-grid prototype,
  without terrain scoring or hazard semantics
- sensor-derived slope, roughness, plane-removed step height, neighbourhood
  coverage, and data-quality confidence, without safety classification
- continuous normalized terrain penalties, prototype traversability, validity,
  and limiting-factor output, without autonomous hazard decisions

Phase 1 may move the rover directly through Gazebo's DiffDrive plugin:

```text
/cmd_vel_safe → Gazebo DiffDrive
```

That backend is temporary. Phase 1 does not validate ArduPilot control, DDS,
Rover SITL, Pixhawk hardware, or a marker mechanism.

Traversability, hazard classification, and marker-location recommendations
remain later sensor-driven work; Phase 1 publishes no placeholder values.

## Milestone A: ArduPilot-authoritative rover simulation

Milestone A is complete only when one reproducible launch demonstrates:

- a pinned ArduPilot Rover SITL version and a real, committed configuration
  export with provenance
- the compatible ArduPilot Gazebo plugin
- maintained communication between Rover SITL and Gazebo
- the ArduPilot DDS node and required command/state interfaces in the ROS graph
- `/cmd_vel_safe` translated into a stamped, frame-validated
  `geometry_msgs/msg/TwistStamped` command on `/ap/cmd_vel`
- documented pre-arm, arming, mode, and failure handling
- rover movement caused by ArduPilot/SITL actuator output rather than direct
  ROS authority over Gazebo DiffDrive
- one valid TF ownership chain from the localization frame through the rover
  base and sensor frames
- odometry with consistent timestamps, frame IDs, and one authoritative
  publisher for each transform
- IMU, RGB image, depth image, and camera-info streams at documented rates
- the existing depth overlay operating on simulated RGB-D data
- stale, HOLD, EMERGENCY, and communication-loss behavior that stops the rover
  within measured and specified limits
- automated launch tests for process startup, DDS interfaces, motion, stopping,
  TF, odometry, and sensor publication

Milestone A will replace the temporary authority path with:

```text
ROS 2
  → command safety
  → ArduPilot DDS
  → Rover SITL
  → ArduPilot Gazebo plugin
  → rover
```

Milestone A does not require marker deployment.

## Milestone B: semantic marker simulation

Milestone B begins after the Milestone A motion/state foundation is stable. It
is complete only when:

- high-level clients use a semantic `DeployMarker` action
- a simulated marker mechanism responds to that action
- feedback reports deployment state without exposing raw PWM
- the result reports success/failure and verification status
- marker inventory and retry/timeout behavior are defined
- simulation and hardware use the same high-level action contract
- simulation tests verify actuation, status, timeout/failure, and completion

Candidate hardware implementations include MAVLink
`MAV_CMD_DO_SET_SERVO`, ArduPilot Lua, and a custom ArduPilot DDS interface.
Milestone B design work must select a backend only after hardware and firmware
capabilities are validated.
