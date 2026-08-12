# ArduPilot firmware and configuration

ArduPilot source is not vendored in this repository. This directory records the
exact external firmware version selected by the project, validated
configuration exports, and reproducible export/validation procedures.

## Current status

[`version.txt`](version.txt) pins a **SITL** target only:

| Target | Value | Validated |
| --- | --- | --- |
| SITL | `Rover-4.7.0` @ `1511f27194f1dcc3728270883047bdf022b3fd53` | command path only, see below |
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
- **Firmware:** `Rover-4.7.0` @ `1511f27194f1dcc3728270883047bdf022b3fd53`
- **Target:** Rover SITL (`--model rover`), no Gazebo attached
- **Build:** `./waf configure --board sitl --enable-DDS && ./waf rover`
- **Toolchain:** Micro-XRCE-DDS-Gen branch `v4.7.0`
- **Transport:** `MicroXRCEAgent udp4 -p 2019`
- **Host:** Ubuntu 24.04, ROS 2 Jazzy
- **Operator:** repository maintainer

An earlier round of the same measurements was taken on `Rover-4.6.3`. Where
4.7.0 differs, the 4.7.0 figure is the one recorded here; the pin moved to
match the firmware actually flashed on the board.

### Measured and confirmed

- The build exposes 18 `/ap/*` topics, up from 15 on 4.6.3. The additions are
  `/ap/status`, `/ap/rc` and `/ap/goal_lla`.
- `/ap/status` is `ardupilot_msgs/msg/Status` and reports `vehicle_type`,
  `armed`, `mode`, `flying`, `external_control` and `failsafe`. It carries no
  pose, which is why the adapter prefers it as its vehicle-state source.
- `/ap/cmd_vel` is `geometry_msgs/msg/TwistStamped` with one AP_DDS
  subscription, QoS `BEST_EFFORT` / `VOLATILE` (measured on 4.6.3; on 4.7.0 the
  compatibility is demonstrated rather than re-measured, since commands
  published with that QoS moved the vehicle).
- `/ap/tf` is `tf2_msgs/msg/TFMessage` and is **subscribed** by AP_DDS on both
  revisions, so an external-odometry input path exists. Whether a transform
  published there is actually consumed by the EKF was **not** tested.
- `/ap/pose/filtered` and `/ap/twist/filtered` publish with
  `header.frame_id = base_link`.
- `/ap/navsat` reported `status.status = 2` with a valid fix at the default
  SITL home position.
- Services present: `/ap/arm_motors` (`ardupilot_msgs/srv/ArmMotors`),
  `/ap/mode_switch` (`ardupilot_msgs/srv/ModeSwitch`), `/ap/prearm_check`
  (`std_srvs/srv/Trigger`), `/ap/experimental/takeoff`, plus parameter
  services.
- Every `/ap/*` endpoint measured on 4.6.3 is `BEST_EFFORT` except `/ap/clock`,
  which is `RELIABLE`.
- `space_ardupilot_interface` republished `/cmd_vel_safe` onto `/ap/cmd_vel` as
  stamped `base_link` commands at 10 Hz against both live builds.
- Rover mode numbers used by the adapter (`MANUAL=0`, `HOLD=4`, `GUIDED=15`)
  were read from `Rover/mode.h` at the pinned revision.

### ArduPilot-authoritative motion, SITL built-in model

Demonstrated end to end on both revisions, driving only `/cmd_vel_safe`:

| Step | Rover-4.6.3 | Rover-4.7.0 |
| --- | --- | --- |
| `/ap/prearm_check` | `Vehicle is Armable` | not repeated |
| `/ap/mode_switch` to `15` | `curr_mode=15` | `curr_mode=15` |
| `/ap/arm_motors` arm | `result=True` | `result=True` |
| Drive `0.5 m/s` for 10 s | 5.246 m | 5.527 m |
| `/ap/arm_motors` disarm | `result=True` | `result=True` |

Position was read from ArduPilot's own `/ap/pose/filtered`, so the motion
originated from ArduPilot's actuator output rather than from ROS driving the
simulator directly.

This used SITL's built-in `--model rover` physics. **No Gazebo was attached**,
so this does not yet satisfy the Gazebo half of the Milestone A chain.

### Speed and stopping, measured on Rover-4.6.3 only

Averaged over a whole run the rover reached 0.403 m/s against a 0.5 m/s
command, which reads as a 20% shortfall. Measuring the steady-state portion
alone gives 0.521 m/s, within 4.3% of the command, so the shortfall is the
acceleration ramp rather than controller error or missing tuning.

Stopping was attributed rather than assumed. The adapter's stale watchdog
published zero 0.44 s after the last upstream command, ahead of ArduPilot's own
command hold-off, and roughly 0.24 m of travel followed. Total travel after
upstream commands cease is therefore about 0.7 m at 0.5 m/s.

**This is not a specified limit.** It is one run, and `/ap/pose/filtered`
position quantisation makes the instantaneous-speed tail noisy enough that the
exact stop instant is uncertain. It must be repeated, on the pinned revision,
before any bound is claimed.

### GPS-denied arming, measured on Rover-4.7.0 SITL

The indoor arena has no GPS, so this was tested rather than assumed. GPS was
disabled (`SIM_GPS1_ENABLE=0`, `GPS1_TYPE=0`), EKF sources were set to external
navigation (`EK3_SRC1_POSXY=6`, `EK3_SRC1_VELXY=6`, `EK3_SRC1_YAW=6`,
`VISO_TYPE=1`), and the vehicle was restarted.

| Attempt | Result |
| --- | --- |
| Mode switch to GUIDED | **accepted**, `curr_mode=15` |
| `/ap/prearm_check` | `Vehicle is Not Armable` |
| Arm, no external odometry | refused, `Arm: AHRS: waiting for home` |
| Arm, `/ap/tf` fed 20 s | refused, `Arm: AHRS: waiting for home` |
| `SET_GPS_GLOBAL_ORIGIN` | accepted, `EKF3 IMU0 origin set` |
| Arm after origin set | refused, `Arm: AHRS: waiting for home` |
| `MAV_CMD_DO_SET_HOME` | accepted, `Set HOME to -35.36326 149.1652` |
| Arm after home set | **still refused** |

Two things this establishes:

- **Entering GUIDED proves nothing.** The mode switch succeeded in every case,
  including cases where the vehicle could not arm and could not move. Any test
  that stops at mode entry will report success for a rover that cannot drive.
- Setting the EKF origin and home is **not sufficient** for GPS-denied arming
  on this build, contrary to what a reading of the origin-setting workaround
  would suggest.

What this does **not** establish: that GPS-denied operation is impossible. The
external odometry fed on `/ap/tf` during this test was a static transform with
a fixed translation. A real visual-inertial estimate moves and updates, and
ArduPilot's visual-odometry health checks may reject a static feed that a live
one would satisfy. The cause of the refusal was not isolated: it is not known
whether the transforms reached `AP_VisualOdom`, nor whether the EKF ever
accepted external navigation as a position source.

Deciding between the DDS-only architecture and a MAVLink/MAVROS path indoors
requires repeating this with a real odometry source, not with this placeholder.

### Pixhawk 6X firmware build

A hardware build was produced but **not yet flashed or run**:

- `Rover-4.7.0` @ `1511f271`, `./waf configure --board Pixhawk6X --enable-DDS`
- toolchain `gcc-arm-none-eabi-10-2020-q4-major` (the system GCC 13 fails the
  ChibiOS build on `-Werror=address`)
- `board_id 53`, matching the `PX4 FMU V6X` bootloader ID reported by the
  connected board
- image 1,583,284 B against 1,966,080 B of reported flash
- AP_DDS presence checked in the ELF rather than assumed

Nothing about its on-board behaviour is validated.

### Not validated

None of the following has been demonstrated and none may be described as
working:

- The ArduPilot Gazebo plugin. It builds against Gazebo Harmonic but has not
  been run with SITL, so no rover has moved in Gazebo.
- Stop latency as a *specified* limit. A single 0.045 m residual over 1.0 s was
  observed; no bound has been established or repeated.
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
