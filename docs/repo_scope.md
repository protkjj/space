# Repository scope

## Supported baseline

- Ubuntu 24.04 and ROS 2 Jazzy
- Gazebo Harmonic simulation assets
- four-wheel skid-steer rover
- RGB-D camera, IMU, odometry, EKF, SLAM, and Nav2 configuration
- backend-neutral velocity safety boundary
- Pixhawk 6X running ArduPilot Rover as the selected autopilot architecture

Exact ArduPilot, Gazebo integration, and DDS component versions remain
unpinned until they have been validated together. A successful repository
build alone does not validate a firmware or hardware configuration.

## Phase 1 contents

Phase 1 includes:

- canonical physical URDF/Xacro in `space_description`
- Gazebo-only plugins, friction, sensor configuration, bridge configuration,
  and world assets in `space_gazebo`
- simulation and hardware bringup separation
- a command-safety node publishing the backend-neutral `/cmd_vel_safe` topic
- a buildable, implementation-free `space_ardupilot_interface` scaffold
- ArduPilot firmware documentation and a real-export policy

The direct Gazebo DiffDrive plugin remains only as a temporary Phase 1 backend.
It is not representative of the final Pixhawk/ArduPilot path and does not
validate ArduPilot control.

## Required dependency boundary

The physical description is simulator-independent:

```text
space_gazebo → space_description
space_description ↛ space_gazebo
```

Canonical links, joints, inertial values, physical sensor mounting transforms,
and wheel geometry belong to `space_description`. Gazebo systems, simulated
sensors, friction, any future noise properties, and other Gazebo tags belong
to `space_gazebo`.

## Explicitly outside Phase 1

- operational ArduPilot DDS command/state adapter
- ArduPilot Rover SITL and ArduPilot Gazebo plugin integration
- validated Pixhawk or SITL parameter exports
- Jetson-side RoboClaw packet-serial control
- invented serial endpoints, IP addresses, frame IDs, DDS rates, or firmware
  settings
- marker mechanism, `DeployMarker` action, or marker hardware transport choice
- mission-management and new custom-interface packages

## Removed legacy scope

- ROS 2 Jazzy as the project baseline
- PX4/uORB bridge implementation and `px4_msgs`
- large hospital, warehouse, and cafe simulation worlds
- large model libraries and unrelated STL assets
- legacy YOLO datasets and trained binaries
- drone/VTOL-focused control code
- transforming-arm firmware and servo sequencing
- baseline dependence on a physical LiDAR

The repository was separated from the original project so these large or
unrelated assets and their Git/LFS history do not remain in the rover
workspace.
