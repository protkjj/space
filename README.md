# space

ROS 2 Jazzy workspace for a lightweight four-wheel skid-steer lunar-rover
challenge prototype.

The current platform target is Ubuntu 24.04, ROS 2 Jazzy, and Gazebo Harmonic.

The repository intentionally keeps the first implementation small: a canonical
physical robot description, a Gazebo simulation, navigation and perception
configuration, a backend-neutral command-safety boundary, and a buildable
ArduPilot interface scaffold. Large environment assets, training datasets, and
unrelated drone or transforming-robot code are outside this repository's scope.

## Current Phase 1 status

Phase 1 is a repository refactor, not an ArduPilot control demonstration. It
provides:

- ROS 2 Jazzy package and documentation cleanup
- a simulation-independent physical model in `space_description`
- Gazebo-only assets and extensions in `space_gazebo`
- separate simulation and hardware bringup entry points
- command clipping, mode gating, and a stale-command watchdog in
  `space_controller`
- a buildable `space_ardupilot_interface` scaffold with no fabricated backend
- ArduPilot firmware/version documentation without guessed parameter files
- a CAD-backed arena pipeline and RViz workflow (mesh generation requires
  FreeCAD; see [`docs/arena_simulation.md`](docs/arena_simulation.md))
- a sensor-derived local elevation prototype using the simulated RGB-D point
  cloud; see [`docs/terrain_perception.md`](docs/terrain_perception.md)
- sensor-derived slope, roughness, step-height, coverage, and data-quality
  confidence; see [`docs/terrain_features.md`](docs/terrain_features.md)
- a continuous, interpretable traversability prototype with validity and
  limiting-factor output; see
  [`docs/traversability.md`](docs/traversability.md)

The Phase 1 Gazebo simulation still uses a temporary direct DiffDrive backend:

```text
/cmd_vel_in → command_safety_node → /cmd_vel_safe → Gazebo DiffDrive
```

This path exists only to preserve a working simulation during the refactor. It
does **not** represent or validate the final Pixhawk/ArduPilot control path.

## Baseline real drivetrain

The current baseline, pending bench validation, is:

```text
Jetson ROS 2
  → Pixhawk 6X running ArduPilot Rover
  → left/right throttle outputs
  → RoboClaw motor controller in RC/PWM mode
  → left/right motor groups
```

Phase 1 does not include a Jetson-side RoboClaw packet-serial driver, serial
connection, PWM generation, or operational ArduPilot hardware adapter. See
[`hardware/drivetrain/README.md`](hardware/drivetrain/README.md) for the required
bench checks.

## Repository layout

```text
space/
├── docs/                         # architecture, scope, requirements, milestones
├── firmware/
│   └── ardupilot/                # version and validated-export policy
├── hardware/                     # drivetrain and power design notes
└── ros2_ws/
    └── src/
        ├── space_description/    # canonical physical URDF/Xacro
        ├── space_gazebo/         # Gazebo-only wrapper, plugins, bridge, world
        ├── space_bringup/        # simulation and hardware orchestration
        ├── space_controller/     # backend-neutral command safety/watchdog
        ├── space_perception/     # depth-based operator overlay
        └── space_ardupilot_interface/ # Phase 1 buildable scaffold
```

The dependency direction is one-way:

```text
space_gazebo → space_description
space_description ↛ space_gazebo
```

The canonical physical Xacro must therefore expand without `space_gazebo`
installed or sourced.

## Build and test

```bash
source /opt/ros/jazzy/setup.bash
cd ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
colcon test
colcon test-result --all --verbose
source install/setup.bash
```

No `px4_msgs` exclusion or optional PX4 build is required after Phase 1. The
ArduPilot package is currently a scaffold and deliberately does not depend on
`ardupilot_msgs` until implementation code actually uses it.

## Launch

Temporary Phase 1 simulation:

```bash
source ros2_ws/install/setup.bash
ros2 launch space_bringup simulation.launch.py
```

Hardware-interface inspection only:

```bash
source ros2_ws/install/setup.bash
ros2 launch space_bringup hardware.launch.py
```

The hardware launch is not operational rover control in Phase 1. The ArduPilot
hardware adapter is not implemented, and `/cmd_vel_safe` intentionally has no
actuator consumer when the safety node is enabled without a backend.

## Project milestones

- **Phase 1:** repository cleanup, Gazebo asset separation, temporary direct
  Gazebo movement, command watchdog, and a buildable ArduPilot scaffold.
- **Milestone A:** ArduPilot Rover SITL, the ArduPilot Gazebo plugin, DDS state
  and control, ArduPilot-authoritative movement, valid TF/odometry, IMU and
  RGB-D streams, and verified stale-command stopping.
- **Milestone B:** a semantic `DeployMarker` action, simulated marker mechanism,
  status and verification, and a shared simulation/hardware semantic API.

Neither Milestone A nor Milestone B is complete. Detailed acceptance criteria
are in [`docs/simulation_milestones.md`](docs/simulation_milestones.md).
Traversability and marker selection remain future sensor-driven work.
Elevation mapping is implemented, but traversability scoring, hazard
identification, marker recommendation, and Nav2 terrain costs are not.
