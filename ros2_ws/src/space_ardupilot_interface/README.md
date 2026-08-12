# space_ardupilot_interface

This package translates the backend-neutral velocity boundary into the
ArduPilot DDS command interface.

```text
/cmd_vel_safe (geometry_msgs/msg/Twist)
  -> space_ardupilot_adapter
  -> /ap/cmd_vel (geometry_msgs/msg/TwistStamped)
  -> ArduPilot AP_DDS
```

## Status

The command path is implemented and was exercised against a live Rover SITL at
the firmware revision pinned in
[`firmware/ardupilot/version.txt`](../../../firmware/ardupilot/version.txt).

What has been demonstrated:

- `/cmd_vel_safe` is republished on `/ap/cmd_vel` as a stamped, frame-tagged
  `TwistStamped` at the configured rate, with QoS that matches the AP_DDS
  subscription measured on that build.
- Stale commands and autopilot communication loss both produce zero commands.

What has **not** been demonstrated, and must not be described as working:

- ArduPilot-authoritative rover motion. Arming and mode switching are
  implemented as configuration but are disabled by default and have not moved
  a vehicle, simulated or real.
- Any hardware path. No Pixhawk has been driven by this node.

See [`firmware/ardupilot/README.md`](../../../firmware/ardupilot/README.md)
for the full validation record.

## Parameters

Every value is a ROS parameter; none is hardcoded in the node. Defaults live in
[`config/adapter.yaml`](config/adapter.yaml), which marks each value as either
measured from the pinned build or unvalidated.

| Parameter | Default | Meaning |
| --- | --- | --- |
| `input_topic` | `/cmd_vel_safe` | Backend-neutral input |
| `output_topic` | `/ap/cmd_vel` | AP_DDS command topic |
| `vehicle_state_topic` | `/ap/pose/filtered` | Liveness source only |
| `arm_service` | `/ap/arm_motors` | `ardupilot_msgs/srv/ArmMotors` |
| `mode_service` | `/ap/mode_switch` | `ardupilot_msgs/srv/ModeSwitch` |
| `prearm_service` | `/ap/prearm_check` | `std_srvs/srv/Trigger` |
| `frame_id` | `base_link` | Command frame |
| `command_timeout_sec` | `0.5` | Upstream staleness limit |
| `link_timeout_sec` | `3.0` | Autopilot silence limit |
| `publish_rate_hz` | `10.0` | Command publication rate |
| `manage_vehicle` | `false` | Allow arming and mode changes |
| `target_mode` | `15` | Rover GUIDED, from `Rover/mode.h` |

`manage_vehicle` defaults to `false` because enabling it lets the node change
the state of a real vehicle. Arming must be an explicit choice.

## One-way state barrier

The node subscribes to an ArduPilot state topic only to detect communication
loss. It stores the arrival time and discards the message contents.

This is deliberate. If ArduPilot's own filtered estimate were fed back into the
estimator that produces the odometry sent to ArduPilot, the same information
would be counted twice: the fused covariance would shrink while the true error
did not. That failure is silent, so the barrier is structural rather than a
comment — the pose value is never retained. Autopilot state may be used for
low-level safety reactions, never as an estimator input.

## Dependencies

`ardupilot_msgs` is an optional runtime dependency, needed only for arming and
mode switching. The node imports it defensively and logs a clear error if
`manage_vehicle` is enabled without it. Build it from the ArduPilot source
tree:

```bash
cd "$ARDUPILOT_DIR/Tools/ros2"
colcon build --packages-select ardupilot_msgs
```

## Real drivetrain baseline

Pending bench validation:

```text
Jetson ROS 2
  -> Pixhawk 6X running ArduPilot Rover
  -> left/right throttle outputs
  -> RoboClaw motor controller
  -> left/right motor groups
```

The Jetson does not command RoboClaw packet serial for motion control.
