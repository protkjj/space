# ArduPilot firmware and configuration

ArduPilot source is not vendored in this repository. This directory records the
exact external firmware version selected by the project, validated
configuration exports, and reproducible export/validation procedures.

## Current status

[`version.txt`](version.txt) pins a **SITL** target only:

| Target | Value | Validated |
| --- | --- | --- |
| SITL | `Rover-4.6.3` @ `3fc7011a7d3dc047cbb17d8bd98ee94577d144c6` | partially, see below |
| HILS / hardware | `UNPINNED` | no |

The SITL and hardware pins are deliberately separate. ArduPilot documents
Simulation-on-Hardware as still changing, so the SITL pin must not be assumed
to apply to a hardware or HILS build.

No Pixhawk or SITL `.param` export exists. Do not create a parameter file by
copying assumed defaults or inventing values. Rover SITL was started from
ArduPilot's own `Tools/autotest/default_params/rover.parm` with no repository
overlay, so there is nothing validated to export yet.

## SITL DDS validation record

- **Date:** 2026-08-12
- **Firmware:** `Rover-4.6.3` @ `3fc7011a7d3dc047cbb17d8bd98ee94577d144c6`
- **Target:** Rover SITL (`--model rover`), no Gazebo attached
- **Build:** `./waf configure --board sitl --enable-dds && ./waf rover`
- **Transport:** `MicroXRCEAgent udp4 -p 2019`
- **Host:** Ubuntu 24.04, ROS 2 Jazzy
- **Operator:** repository maintainer

### Measured and confirmed

- The build exposes 15 `/ap/*` topics and 6 `/ap/*` services.
- `/ap/cmd_vel` is `geometry_msgs/msg/TwistStamped` with one AP_DDS
  subscription, QoS `BEST_EFFORT` / `VOLATILE`.
- `/ap/tf` is `tf2_msgs/msg/TFMessage` and is **subscribed** by AP_DDS, so an
  external-odometry input path exists in this build. Whether a transform
  published there is actually consumed by the EKF was **not** tested.
- `/ap/pose/filtered` and `/ap/twist/filtered` publish with
  `header.frame_id = base_link`.
- `/ap/navsat` reported `status.status = 2` with a valid fix at the default
  SITL home position.
- Services present: `/ap/arm_motors` (`ardupilot_msgs/srv/ArmMotors`),
  `/ap/mode_switch` (`ardupilot_msgs/srv/ModeSwitch`), `/ap/prearm_check`
  (`std_srvs/srv/Trigger`), `/ap/experimental/takeoff`, plus parameter
  services.
- Every `/ap/*` endpoint measured is `BEST_EFFORT` except `/ap/clock`, which is
  `RELIABLE`.
- `space_ardupilot_interface` republished `/cmd_vel_safe` onto `/ap/cmd_vel` as
  stamped `base_link` commands at 10 Hz against this live build.
- Rover mode numbers used by the adapter (`MANUAL=0`, `HOLD=4`, `GUIDED=15`)
  were read from `Rover/mode.h` at this exact revision.

### Not validated

None of the following has been demonstrated and none may be described as
working:

- ArduPilot-authoritative rover **motion**. The vehicle was never armed and
  never placed in GUIDED, so no actuator output was produced.
- The ArduPilot Gazebo plugin. It builds against Gazebo Harmonic but has not
  been run with SITL.
- Any TF ownership chain, odometry publisher ownership, or sensor stream.
- Measured stop latency for stale, HOLD, EMERGENCY, or communication loss.
- Automated launch tests.
- Anything on Pixhawk 6X hardware, including whether the flashed firmware
  contains AP_DDS at all. Use
  [`scripts/probe_autopilot.py`](scripts/probe_autopilot.py) to answer that.
- GPS-denied operation and external odometry actually feeding EKF3.

### Reproduction

[`scripts/setup_sitl.sh --check`](scripts/setup_sitl.sh) verifies each
prerequisite and names the exact missing command. Known host pitfalls it
reports rather than hides:

- `--enable-dds` requires `microxrceddsgen`, which needs a JRE newer than 8.
- `sim_vehicle.py` exits immediately if MAVProxy cannot import matplotlib,
  which happens when a user-local NumPy shadows the system NumPy. In that case
  run with `--no-mavproxy` and attach any MAVLink client to
  `tcp:127.0.0.1:5760`; SITL blocks on SERIAL0 until one connects.
- `/ap/arm_motors` and `/ap/mode_switch` need `ardupilot_msgs` built from
  `Tools/ros2`.

## Required provenance for future exports

Every parameter export must be taken from a real configuration and accompanied
by:

- exact ArduPilot release or commit
- target board
- physical hardware identifier, or an explicit SITL target identifier
- export date
- validation status
- export command/tool and procedure
- operator or responsible owner
- applicable vehicle/model revision
- link to the validation record or test results

DDS interfaces, message availability, frame semantics, and publication rates
may depend on the pinned ArduPilot build. These must be measured and documented
for that build rather than inferred from another release.

## Validation rule

No firmware configuration is considered validated merely because the ROS
workspace builds. Validation must exercise the intended target:

- Rover SITL with the selected Gazebo plugin for simulation configuration
- the exact Pixhawk 6X board and drivetrain signals for hardware configuration
- required DDS topics/services and measured update rates
- pre-arm, arm, disarm, mode, timeout, and communication-loss behavior
- configuration reload/reboot and repeatability

The baseline real drivetrain is:

```text
Jetson ROS 2
  → Pixhawk 6X running ArduPilot Rover
  → left/right throttle outputs
  → RoboClaw in RC/PWM mode
  → left/right motor groups
```

That RC/PWM link remains pending bench validation. See
[`../../hardware/drivetrain/README.md`](../../hardware/drivetrain/README.md).
