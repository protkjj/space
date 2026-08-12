# ArduPilot firmware and configuration

ArduPilot source is not vendored in this repository. This directory records the
exact external firmware version selected by the project, validated
configuration exports, and reproducible export/validation procedures.

## Current status

[`version.txt`](version.txt) pins three targets separately:

| Target | Value | Validated |
| --- | --- | --- |
| SITL | `Rover-4.7.0` @ `1511f271` | command path and motion, see below |
| Hardware | `Rover-4.7.0` @ `1511f271`, built `--enable-DDS` | DDS interface only |
| HILS | `UNPINNED` | not attempted |

SITL and hardware currently run the same commit, but they stay separately
pinned: the hardware image is a local build rather than a release binary, and
ArduPilot documents Simulation-on-Hardware as still changing, so neither pin
should be assumed to carry over to the others.

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
- AP_DDS does **not** use one QoS for every topic. Measured per topic on
  4.7.0, identically on SITL and on the Pixhawk 6X over serial:

  | Reliability | Topics |
  | --- | --- |
  | `BEST_EFFORT` | `/ap/cmd_vel`, `/ap/pose/filtered`, `/ap/twist/filtered`, `/ap/tf`, `/ap/rc`, `/ap/navsat` |
  | `RELIABLE` | `/ap/status`, `/ap/clock` |

  This matters in practice: subscribing to `/ap/status` with an explicit
  `--qos-reliability best_effort` on hardware produced no output and looked
  like a dead topic. Check the publisher's QoS per topic rather than assuming
  one profile for the namespace.
- `/ap/status` publishes on change, and otherwise at 2 Hz
  (`AP_DDS_DELAY_STATUS_TOPIC_MS` is 100 ms and the periodic path fires after
  five intervals), so it is usable as a liveness signal.
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

**That first round used a broken timestamp, so its refusal proves less than it
appears to.** `AP_DDS_External_Odom.cpp` converts the transform's stamp with:

```cpp
const uint32_t time_ms {static_cast<uint32_t>(remote_time_us * 1E-3)};
```

A ROS wall-clock stamp is about 1.8e15 microseconds, so `time_ms` is about
1.8e12 and overflows `uint32_t`. The autopilot received a garbage timestamp,
which is reason enough to reject a measurement whether or not GPS-denied
arming is otherwise possible. **External odometry on `/ap/tf` must be stamped
in ArduPilot's own time base**, which it publishes on `/ap/clock`. On the
pinned build that clock read ~18 s against a wall clock of ~1.79e9 s.

Repeating with correctly stamped, moving odometry changed the result:

| Run | `/ap/prearm_check` | Arm |
| --- | --- | --- |
| 1 | **`Vehicle is Armable`** | refused |
| 2 | `Vehicle is Not Armable` | refused |
| 3 | `Vehicle is Not Armable` | refused |

Pre-arm passing even once matters: it means the EKF **can** accept external
navigation as a position source with no GPS. It is not reproducible with the
odometry used here, which was synthetic — constant velocity along one axis,
no rotation, and reported with zero position and angle error.

So the honest state is: **GPS-denied operation is neither demonstrated nor
ruled out.** The frame names are right (`odom` to `base_link`, compared
exactly), the transport works, `AP_VisualOdom` is compiled into both the SITL
and Pixhawk 6X builds, and the estimate has been accepted at least once. What
has not been shown is that it holds steadily enough to arm and drive. Settling
it requires a real estimate from the camera and IMU, not a synthetic one, and
that work has not started.

Also worth carrying forward: a frozen transform and a moving one are different
signals to ArduPilot's visual-odometry handling. Do not test this path with a
placeholder that never changes.

### Hardware bring-up, Pixhawk 6X over USB serial

Measured on the actual board after flashing the DDS build described below.

**The DDS interface is live on hardware.** The XRCE agent attached to the
second USB CDC interface and the board created its topics, publishers and
service repliers. `ros2 topic list` showed the same 18 `/ap/*` topics as SITL,
so the interface the adapter was written against exists on the real vehicle.

Transport and port mapping, from `Pixhawk6X/hwdef.dat`:

```text
SERIAL_ORDER OTG1 UART7 UART5 USART1 UART8 USART2 UART4 USART3 OTG2
  index        0     1     2      3     4      5     6      7     8
```

`SERIAL0` is OTG1 and `SERIAL8` is OTG2, so one USB cable exposes two serial
interfaces. Setting `SERIAL8_PROTOCOL=45` puts DDS on the second interface and
leaves MAVLink on the first, which keeps a ground station usable while the
companion computer speaks DDS. On the host these appear as two `ttyACM`
devices, distinguishable by their `if00` and `if02` `/dev/serial/by-id` names.

**BEST_EFFORT topics are dropped on the serial transport.** With RC connected,
`/ap/rc` publishes every loop and `ros2 topic echo` on it returned nothing for
seconds at a time, while the same RC data read over MAVLink on the other
interface was continuous and complete (`rssi=255`, all 8 channels tracking
stick movement). `/ap/status`, being RELIABLE, kept arriving throughout. This
does not appear in SITL, where DDS runs over UDP with bandwidth to spare.
Treat BEST_EFFORT `/ap/*` topics as lossy over serial, and do not diagnose a
silent BEST_EFFORT topic as a dead subsystem without checking a RELIABLE one.

**Arming is blocked by vehicle commissioning, not by the software path.** The
board reported, verbatim:

```text
Arm: Hardware safety switch
Arm: 3D Accel calibration needed
Arm: Compass not calibrated
Arm: AHRS: waiting for home
Arm: Battery 1 unhealthy
```

All five are standard first-time setup: the safety switch, accelerometer and
compass calibration, a position estimate, and a connected battery. None of them
implicates the DDS interface or the adapter. RC was bound and healthy over
MAVLink at the time, and `RC3_MIN`/`RC3_MAX` were still at defaults, so radio
calibration has not been performed either.

No arming, no motion, and no drivetrain behaviour has been demonstrated on
hardware.

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
