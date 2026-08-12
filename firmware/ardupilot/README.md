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
navigation as a position source with no GPS.

**The non-reproducibility is timing, not data content.** An earlier revision of
this record guessed that ArduPilot rejects a static or constant-velocity feed.
That guess has no basis in the code: `AP_VisualOdom_Backend::healthy()` only
checks that something arrived within 300 ms, and nothing inspects the motion.
The actual gates a sample must pass are:

| Stage | Where | Drops the sample when |
| --- | --- | --- |
| Frame filter | `AP_DDS_External_Odom.cpp` | frame is not exactly `odom` to `base_link` |
| EKF buffer write | `AP_NavEKF3_Measurements.cpp` | under 20 ms since the last sample, by sender stamp, or states not initialised |
| Fusion recall | `AP_NavEKF3_PosVelFusion.cpp` | the stamp misses the fusion horizon, which trails the present by the EKF delay |
| Aiding start | `AP_NavEKF3_Control.cpp` | source is not EXTNAV, or tilt alignment is incomplete |

Stamping from `/ap/clock` and extrapolating locally leaves a per-run offset
between when the clock was sampled and when ArduPilot receives the transform.
`AP_DDS_External_Odom.cpp` carries a TODO acknowledging it performs no jitter
correction, so nothing absorbs that offset. Whether a run lands inside the
fusion horizon is therefore luck, which is exactly the "passes once, then
does not" behaviour observed.

**Watch for `EKF3 IMU0 is using external nav data`.** That message, emitted
from `AP_NavEKF3_Control.cpp`, is the point at which aiding actually starts.
Pre-arm success is a weaker and later signal; if that message never appears,
aiding never began. It was not captured during these runs.

**`/ap/clock` does not reach the companion computer over serial.** It was
measured at 0 Hz on the Pixhawk 6X while `/ap/time` arrived at about 64 Hz,
so the clock-stamping approach used here cannot be reproduced on hardware as
written.

### GPS-denied arming and driving, demonstrated on SITL

With the timestamp and the source configuration both corrected, the rover
armed and drove with no GPS at all:

```text
EKF3 IMU0 is using external nav data
EKF3 IMU0 initial pos NED = -1.6,0.1,0.0 (m)
prearm_check : success=True, 'Vehicle is Armable'
mode_switch  : curr_mode=15
arm          : result=True
Throttle armed
travelled 0.623 m
```

The configuration that works:

| Parameter | Value | Why |
| --- | --- | --- |
| `EK3_SRC1_POSXY` | `6` | external navigation |
| `EK3_SRC1_VELXY` | `6` | external navigation |
| `EK3_SRC1_YAW` | `6` | external navigation |
| `EK3_SRC1_VELZ` | `0` | **must be cleared**; see below |
| `EK3_SRC1_POSZ` | `1` | barometer, unrelated to the horizontal problem |
| `VISO_TYPE` | `1` | instantiates `AP_VisualOdom` so the DDS handler has somewhere to deliver |

**`EK3_SRC1_VELZ` is the one that is easy to miss.** It defaults to GPS, and
`AP_NavEKF_Source::pre_arm_check` scans every field of every source set, so a
single leftover GPS source blocks arming with `AHRS: EK3 sources require GPS`
no matter how well the horizontal sources are configured. That message does
not say which field is at fault; read them all back rather than assuming the
three obvious ones are the whole set. `EK3_SRC2_*` and `EK3_SRC3_*` were all
`None` here and were not implicated.

**`EK3_SRC1_VELXY = 6` receives no data over DDS.** `AP_DDS_External_Odom`
delivers pose only — it contains no velocity handling at all — and the
external-navigation velocity path, `writeExtNavVelData`, is reached only from
the MAVLink `VISION_SPEED_ESTIMATE` and Intel T265 backends. The arming check
passes because it only verifies that the subsystem named by the source is
enabled, which `VISO_TYPE` satisfies, so this is silent. Horizontal velocity
is therefore dead-reckoned between position updates. Setting it to `6` is
harmless but decorative on a `/ap/tf`-only setup; `7` (wheel encoder) is the
value with real data behind it once encoders are available.

Feeding requirements, all of which mattered:

- stamp from `/ap/time`, which is ArduPilot's own time base
- stamp slightly in the past, not the future
- advance the stamp by at least 20 ms between samples, or the EKF drops them
- keep feeding continuously, including while the arming services are called.
  Aiding stops after roughly five seconds without a fused sample, and
  `EKF3 IMU0 stopped aiding` is the message that says so.
- **do not jump the reported position.** The DDS path hardcodes
  `reset_counter` to 0, so there is no way to tell the EKF that an estimate
  discontinuity was intentional. A restarted VIO or script that resumes from a
  different origin looks like a physically impossible movement. Resume from
  where the previous estimate left off, or expect the fusion to reject it.
- frame ids exactly `odom` and `base_link`; the comparison is a `strcmp`, so
  a namespace prefix is silently ignored
- send `SET_GPS_GLOBAL_ORIGIN` once so the EKF has an origin
- **reboot after setting `VISO_TYPE`.** It is `@RebootRequired`, and
  `AP_VisualOdom` is initialised once at boot, so without a reboot the driver
  is null and every transform is discarded without a message. A parameter
  readback showing the right value does not mean the vehicle can receive.

### GPS-denied external navigation, confirmed on the Pixhawk 6X

Everything above was SITL. Repeating it on the board:

```text
transforms published : 1136 over 60 s   (18.9 Hz against a 20 Hz target)
skipped for spacing  : 0
/ap/time received    : 5093             (85 Hz)
aiding started       : yes
aiding stopped again : no

EKF3 IMU0 is using external nav data
EKF3 IMU1 is using external nav data
Set HOME to -35.36326 149.1652 at 584.10m
```

Both EKF cores attached and held for the full minute without dropping, and
`AHRS: waiting for home` no longer appears. The serial link carries external
odometry inbound: not one sample was lost to the 20 ms spacing rule, even
though the same link is saturated in the outbound direction with `/ap/clock`
and `/ap/status` at 0 Hz. The two directions had to be measured separately;
the outbound figures said nothing about this one.

Arming is still refused, but only by vehicle commissioning: safety switch,
accelerometer calibration, compass calibration, and battery health. Nothing
remaining points at the software path.

**`PreArm: VisOdom: out of memory` is a misleading message.** It appeared
throughout the failed attempts while free memory was 542 KB, which is ample
for an object of this size. `AP_VisualOdom.cpp` asserts that a null backend
must mean an allocation failure, but the backend is equally null when
`init()` ran while `VISO_TYPE` was still 0. Since `VISO_TYPE` is
`@RebootRequired` and `init()` runs once at boot, setting it and not
rebooting produces exactly that state. Read this message as "no backend",
not as "no memory".

**Judge this by `EKF3 IMU0 is using external nav data`**, not by pre-arm.
That message is when aiding actually starts. Pre-arm success is later and
weaker, and an earlier round of this testing reported "no aiding" for every
configuration purely because its status channel had failed to connect and
every check therefore returned false.

What this does **not** show: that a real odometry source works. The estimate
fed here was synthetic and reported 0.05 m/s while the vehicle was commanded
at 0.4 m/s, so the vehicle drove while believing it had barely moved. Arming
and driving are demonstrated; positional accuracy is not, and cannot be until
the estimate comes from real sensors. It is also SITL only — nothing here has
been repeated on the Pixhawk 6X.

Wheel odometry remains attractive as an alternative, because ArduPilot stamps
encoder data on its own clock and none of the buffer or recall timing applies.
Note that `EK3_SRC1_POSXY = 7` is **invalid** — `AP_NavEKF_Source` rejects it
and pre-arm reports `Check EK3_SRC1_POSXY`. Wheel encoders are a velocity
source only, so that configuration is `EK3_SRC1_VELXY = 7` with
`EK3_SRC1_POSXY = 0`, which dead-reckons a relative position.

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
