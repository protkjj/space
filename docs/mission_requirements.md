# Mission-derived requirements draft

Requirements must be traced to confirmed mission constraints or validated
engineering evidence. Unknown electrical, mechanical, firmware, and interface
values must not be filled with guessed defaults.

## Confirmed competition constraints

| Item | Value |
| --- | --- |
| Finalists | 8 teams |
| Time structure | 20-minute mission + 3-minute setup + 3-minute removal |
| Final rover mass | 3 kg maximum |
| Target rover mass | 2.5 kg |
| Stowed volume | Within 300 × 300 × 200 mm |
| Course | 2.4 m uneven rock section + 3 m granular section; 3 m width |
| Route | Lander departure, rocks/obstacles, sand/slope, route following, target arrival |
| Operator view | Camera-based remote operation |
| Required capabilities | Lander departure, mobility, imaging, and a team-proposed mission |

## Current architecture direction

| Area | Direction |
| --- | --- |
| Steering | Four-wheel skid steer / differential drive |
| Motors | Brushed DC gearmotors with encoders |
| Motor control | RoboClaw two-channel family; capacity to be selected from validated load/current calculations |
| Autopilot | Pixhawk 6X running ArduPilot Rover |
| Compute | Jetson-class onboard computer running ROS 2 Jazzy |
| Sensors | RGB-D camera first; no physical LiDAR in the baseline |
| Navigation | Grid/global planning with a DWB-family local controller |
| State estimation | Wheel/vehicle odometry and IMU fusion |
| Mission payload | Lightweight observation or mapping concepts remain candidates |

## Baseline drivetrain, pending bench validation

```text
Jetson ROS 2
  → Pixhawk 6X / ArduPilot Rover
  → left/right throttle outputs
  → RoboClaw in RC/PWM mode
  → left/right motor groups
```

This is an architectural baseline, not evidence that the electrical or control
interface has passed bench testing. Phase 1 does not add a direct Jetson-to-
RoboClaw packet-serial path.

Before the drivetrain is treated as selected and validated, testing must cover:

- electrical signal compatibility
- shared-ground requirements
- neutral calibration
- direction reversal and correction
- response to signal loss
- controller and wiring current capacity
- two-motors-per-channel loading

No PWM range, neutral value, output channel, current rating, or failsafe
behavior is specified until measured or confirmed from the exact hardware and
firmware configuration.

## Open decisions

| Decision | Evidence required |
| --- | --- |
| Wheel diameter | Step and obstacle height |
| Motor torque and speed | High/medium/low slope angles and step height |
| Driver and battery capacity | Measured motor currents and transient loads |
| Wheel width and track | Sand depth, grain size, compaction, and turning resistance |
| Encoder feedback route | Confirmed Pixhawk/ArduPilot and Jetson integration design |
| Mission payload | Scoring method and size/mass constraints |
| RGB-D reliability | Tests on representative granular and low-texture surfaces |
| Camera configuration | Team-camera rules and availability of competition video |
| Localization/map strategy | Whether online mapping or a prior/static map is allowed |
| Marker mechanism | Payload requirements, actuation, sensing, and verification |

Marker transport is deliberately undecided. Future evaluation may compare
MAVLink `MAV_CMD_DO_SET_SERVO`, ArduPilot Lua, and a custom ArduPilot DDS
interface, but mission-level code must eventually use a semantic
`DeployMarker` action rather than raw PWM.
