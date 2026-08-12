# Rover software and control architecture

## Status

This document describes the Phase 1 repository boundary and the intended
Milestone A/B architecture. Phase 1 is implemented as a safe scaffold; neither
Milestone A nor Milestone B is complete.

The current target is Ubuntu 24.04, ROS 2 Jazzy, Gazebo Harmonic, ArduPilot
Rover, Pixhawk 6X, Jetson Orin NX, OAK-D Pro W, and two RoboClaw 2x15A
controllers. The workspace is intentionally limited to exactly six packages.

## Package responsibilities

```text
space_bringup
├── includes space_gazebo for simulation
├── starts the physical description for hardware inspection
├── starts space_controller
└── orchestrates existing navigation/perception components

space_gazebo
└── depends on space_description

space_controller
└── publishes backend-neutral /cmd_vel_safe

space_ardupilot_interface
└── Phase 1 scaffold; future consumer of /cmd_vel_safe
```

`space_description` owns only the canonical physical robot: links, joints,
geometry, inertial properties, wheel dimensions, and physical sensor mounting
transforms. It must expand independently without `space_gazebo`.

`space_gazebo` owns simulation composition and simulator-only behavior:

- the temporary DiffDrive plugin
- Gazebo odometry and joint-state systems
- simulated IMU and RGB-D sensors
- friction and other Gazebo-specific tags; any future sensor-noise
  configuration also belongs here
- bridge configuration and simulation worlds
- authoritative arena CAD, generated meshes, and the RViz arena marker

The dependency direction is:

```text
space_gazebo → space_description
space_description ↛ space_gazebo
```

## Command ownership

High-level motion producers publish `geometry_msgs/msg/Twist` on
`/cmd_vel_in`. `space_controller` clips accepted commands, applies the
documented driving-mode gate, and maintains a stateful stale-command watchdog.
It publishes backend-neutral commands on `/cmd_vel_safe`.

The Phase 1 mode contract remains `std_msgs/msg/UInt8` on `/space/mode`:

| Value | Name | Command behavior |
| ---: | --- | --- |
| `0` | `ROVER` | Accept and forward clipped fresh commands |
| `1` | `HOLD` | Publish zero immediately and periodically while active |
| `2` | `EMERGENCY` | Publish zero immediately and periodically while active |

Unknown values are rejected without changing the current mode. These values
must be defined as named constants in `space_controller`; consumers must not
duplicate unexplained numeric literals. Creating a custom mode message is
outside Phase 1.

The command-safety parameters are:

| Parameter | Phase 1 default | Constraint |
| --- | --- | --- |
| `input_topic` | `/cmd_vel_in` | ROS input topic |
| `output_topic` | `/cmd_vel_safe` | Backend-neutral output topic |
| `mode_topic` | `/space/mode` | `UInt8` mode topic |
| `max_linear_mps` | `0.30` | Finite and greater than zero |
| `max_angular_radps` | `0.80` | Finite and greater than zero |
| `command_timeout_sec` | `0.50` | Finite and greater than zero |
| `watchdog_period_sec` | `0.05` | Finite and greater than zero |
| `stop_publish_period_sec` | `0.20` | Finite and greater than zero |

A zero `command_timeout_sec` does not disable the watchdog and is invalid
configuration. Non-finite velocity components are rejected without refreshing
the watchdog. The watchdog and periodic stop-publication timers use the node's
ROS clock so the same behavior can be tested with `use_sim_time`.

Phase 1 temporary simulation:

```text
/cmd_vel_in
  → command_safety_node
  → /cmd_vel_safe
  → Gazebo DiffDrive
```

The watchdog publishes zero periodically while commands are stale or the rover
is in HOLD/EMERGENCY, and resumes forwarding after a fresh accepted command in
the driving mode. The simulator backend must consume `/cmd_vel_safe`; high-
level and backend topics must not both be named `/cmd_vel`.

Milestone A target:

```text
ROS 2 motion source
  → command_safety_node
  → /cmd_vel_safe (geometry_msgs/msg/Twist)
  → space_ardupilot_interface
  → /ap/cmd_vel (geometry_msgs/msg/TwistStamped)
  → ArduPilot DDS
  → Rover SITL
  → ArduPilot Gazebo plugin
  → rover actuators in Gazebo
```

The adapter is responsible for command timestamps, frame selection and
validation, ArduPilot mode and pre-arm/arming management, vehicle-state
monitoring, and communication-loss detection.

### Milestone A progress

The command leg of that chain is implemented and was exercised against a live
Rover SITL at the firmware revision pinned in `firmware/ardupilot/version.txt`.
The measurements behind each claim are recorded in
[`../firmware/ardupilot/README.md`](../firmware/ardupilot/README.md).

Demonstrated:

- `/cmd_vel_safe` is republished on `/ap/cmd_vel` as stamped, `base_link`
  commands whose QoS matches the AP_DDS subscription measured on that build.
- Stale commands and autopilot silence both produce zero commands.
- The AP_DDS command, state, and service interfaces exist in the ROS graph.
- ArduPilot-authoritative movement, driving only `/cmd_vel_safe`: pre-arm
  check, GUIDED entry, arming, 5.2 m of travel, stopping when commands cease,
  and disarming. Position was read from ArduPilot's own `/ap/pose/filtered`,
  so the motion came from ArduPilot's actuator output rather than from ROS
  driving the simulator.

That run used SITL's built-in rover model with no Gazebo attached, so the
Gazebo half of the chain above is still unproven.

Not demonstrated, and not to be described as working:

- ArduPilot Gazebo plugin integration. No rover has moved in Gazebo.
- TF ownership, odometry ownership, and sensor streams.
- Stop latency as a specified, repeated limit, and automated launch tests.
- Any Pixhawk 6X hardware behaviour. The board checked so far reports no
  `DDS_ENABLE` parameter, so its flashed firmware contains no AP_DDS and the
  hardware transport question is still open.

### GPS-denied operation is unresolved

The competition arena is indoors. Rover SITL at the pinned revision, with GPS
disabled and EKF sources set to external navigation, **refused to arm**:
`Arm: AHRS: waiting for home`. Setting the EKF origin with
`SET_GPS_GLOBAL_ORIGIN` and setting home with `MAV_CMD_DO_SET_HOME` both
succeeded and neither changed the refusal.

Mode entry is not evidence here. GUIDED was accepted in every one of those
attempts, including the ones where the vehicle could not arm and did not move.

The external odometry used in that test was a static placeholder transform, so
the refusal is not yet attributable. It may be the vehicle rejecting
GPS-denied arming, or it may be the visual-odometry health check correctly
rejecting a feed that never moves. Until a real estimate is available from the
camera and IMU, the indoor architecture is undecided, and no claim should be
made that either the DDS-only or a MAVLink-assisted path works indoors.
Measurements are in [`../firmware/ardupilot/README.md`](../firmware/ardupilot/README.md).

### Autopilot state is not an estimator input

The adapter subscribes to ArduPilot state only to detect communication loss and
discards the message contents.

When a companion-computer estimate is sent to the autopilot, the estimator
producing it must not consume the autopilot's own fused estimate. Doing so
counts the same information twice: the fused covariance shrinks while the true
error does not, so the system reports rising confidence while drifting. The
failure is silent, which is why the boundary is enforced structurally in the
adapter rather than by convention. Autopilot state may drive low-level safety
reactions such as rollover or failsafe handling, never estimator input.

## Real drivetrain boundary

The current baseline pending bench validation is:

```text
Jetson ROS 2
  → Pixhawk 6X running ArduPilot Rover
  → left/right throttle outputs
  → RoboClaw in RC/PWM mode
  → left/right motor groups
```

The Jetson does not command RoboClaw directly in the Phase 1 or baseline target
architecture. No ROS node should open a RoboClaw serial connection or generate
motor PWM.

The Phase 1 hardware launch is for description and interface validation only.
It must emit a clear startup warning that the ArduPilot hardware adapter is
unimplemented. If `command_safety_node` is started, `/cmd_vel_safe`
intentionally has no actuator consumer.

## Marker boundary

Marker deployment is Milestone B, not Phase 1 or Milestone A. Mission-level
code will use a semantic `DeployMarker` action with deployment state, status,
verification, and result semantics. It will not expose raw PWM.

Candidate hardware backends to evaluate later are:

- MAVLink `MAV_CMD_DO_SET_SERVO`
- ArduPilot Lua
- a custom ArduPilot DDS interface

No backend, servo channel, PWM value, timing, or verification sensor is selected
during Phase 1.

Terrain analysis is likewise future sensor-driven work. CAD is visualization
ground truth and must not become a traversability shortcut. The future flow is
depth/PointCloud2 filtering, frame transformation, elevation representation,
feature and uncertainty calculation, traversability scoring, costmap
integration, and only then hazard or marker-location decisions.

The measured-data and geometric-feature stages are implemented inside
`space_perception`:

```text
/camera/points
  → vectorized range/crop/voxel filtering in odom
  → rover-centred median elevation cells
  → elevation PointCloud2 and RViz MarkerArray
  → local plane slope, robust roughness, plane-removed step height
  → feature PointCloud2, compact markers, and quality diagnostics
  → normalized penalties, continuous prototype traversability, and validity
  → bounded soft costs in the rolling Nav2 local costmap
```

These stages publish measurements, geometry, quality confidence, interpretable
penalties, and a continuous prototype score. Guaranteed safe/unsafe
classification, hazard decisions, marker recommendation, wheel-slip fusion,
global terrain planning, and guaranteed terrain avoidance remain
unimplemented. The local-only integration is described in
[`nav2_traversability_layer.md`](nav2_traversability_layer.md).

Simulation alone starts the 3D `robot_localization` EKF configuration required
to retain Z, roll, and pitch for slope mapping. `hardware.launch.py` starts no
EKF and remains an interface-only placeholder; a hardware EKF must wait for
validated Pixhawk and VIO message definitions and topic ownership.

## Configuration ownership

- ROS topic names and backend-neutral node behavior belong in ROS package
  configuration.
- Real ArduPilot parameter exports belong in `firmware/ardupilot/params/`.
- Each future export must identify its firmware build and physical target.
- Secrets, guessed device paths, arbitrary DDS endpoints, and invented
  parameters do not belong in the repository.
