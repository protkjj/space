# space_ardupilot_interface

This Phase 1 package is an intentionally executable-free scaffold for the
future ArduPilot Rover adapter. It does not open a transport, arm a vehicle,
change vehicle modes, or publish commands.

The backend-neutral input contract will be:

- `/cmd_vel_safe` (`geometry_msgs/msg/Twist`)

The future ArduPilot DDS output contract will be:

- `/ap/cmd_vel` (`geometry_msgs/msg/TwistStamped`)

The adapter must create timestamps, select and validate the command frame,
manage ArduPilot mode and arming/pre-arm workflows, monitor vehicle state, and
detect communication loss. Those responsibilities require a pinned and
validated ArduPilot build and are deferred to Milestone A. No DDS endpoint,
serial device, IP address, frame ID, update rate, or firmware parameter is
assumed in this scaffold.

The real drivetrain baseline, pending bench validation, is:

```text
Jetson ROS 2
  -> Pixhawk 6X running ArduPilot Rover
  -> left/right throttle outputs
  -> RoboClaw motor controller
  -> left/right motor groups
```

The Jetson will not command RoboClaw packet serial directly.
