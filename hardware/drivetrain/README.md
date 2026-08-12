# Drivetrain

## Current baseline pending bench validation

```text
Jetson ROS 2
  → Pixhawk 6X running ArduPilot Rover
  → left/right throttle outputs
  → RoboClaw motor controller in RC/PWM mode
  → left/right motor groups
```

The mechanical baseline is a four-wheel skid-steer rover using encoder-equipped
brushed DC gearmotors. There are two RoboClaw 2x15A controllers, one per side,
and each drives that side's two wheels on its own channel, so every wheel has
an independent channel and an independent encoder.

An earlier version of this section said the two motors on a side shared one
channel. That was wrong, and it disagreed with both `docs/architecture.md`,
which has always specified two controllers, and with `roboclaw_reader`, which
opens one link per side and averages the two encoders each controller reports.
The four-channel arrangement is the one the code implements.

The target rover mass is 2.5 kg and the preliminary target speed range is
0.1–0.3 m/s. Final motor and controller selection still depends on measured
terrain and load data.

The RC/PWM interface is an architectural baseline, not yet a bench-validated
selection. This repository contains no evidence establishing electrical
compatibility, calibrated neutral behavior, channel assignments, current
capacity, or a safe response to signal loss.

Phase 1 deliberately does not include:

- a Jetson-side RoboClaw packet-serial **control** driver
- a direct ROS-to-RoboClaw control path
- serial device configuration
- PWM ranges, neutral values, or output-channel assignments
- assumed current ratings or failsafe behavior

Read-only encoder telemetry is a separate, permitted case. The encoders are
wired to the RoboClaws rather than to the Pixhawk, so wheel odometry can only
be obtained by reading them over the RoboClaw link. A node doing so must be
read-only, must never issue a motion or configuration command, and must not
sit on the command path. See the drivetrain boundary in
[`../../docs/architecture.md`](../../docs/architecture.md). Nothing about the
control exclusions above changes: ArduPilot remains the only writer.

### Reading encoders

The firmware reported on the current units is `4.4.9`.

**Wheel odometry needs command 78, `GETENCODERS`, and nothing else.** The
request is two bytes and the reply is ten: two 32-bit counts and a CRC16. That
command appears in every manual revision and in both the legacy and current
libraries, so there is no version risk attached to it.

Command 73, `Read All Status`, is a bandwidth optimisation rather than a
capability. The manual says so directly, immediately after its specification:
it consolidates data otherwise available from the individual status commands,
including the encoders from 78. Its reply is 58 bytes, 56 of payload plus a
CRC16. Using it saves round trips when several values are wanted at once; it
contributes no data that 78 and its siblings do not already provide.

An earlier note here said 73 was the command wheel odometry depended on, and
gave its reply as 74 bytes. Both were wrong. The path does not hinge on 73
being present.

BasicMicro's own ROS 2 driver calls `GetStatus(73)` in a hardware test and
states its validation hardware as "USB Roboclaw 2x15a v4.4.2 or newer", which
covers these units, so 73 is very likely available as well.

### Confirmed against a controller

Measured on one unit reporting `USB Roboclaw 2x15A v4.4.9`:

| Check | Result |
| --- | --- |
| Command 78 framing and CRC | 1228 replies, 0 rejected |
| Command 79, speeds | verified |
| Command 73 reply length | **58 bytes**, CRC over 56 of payload verified |
| Command 73 carries the encoders | `0x9152` and `0x9df2` in its reply matched the counts command 78 returned at the same moment |
| M1 and M2 independence | turning one wheel moved only that encoder |
| Count direction | both count up when the wheel turns forward, so neither side needs its sign inverted |

The rover's own parser was used for this rather than a copy, so the check
validates the code that will run.

### Counts per revolution

Datasheet: 64 CPR at the motor through 100:1 gearing, so 6400 per output
revolution. Measured by hand against an alignment mark: **6554 over ten
revolutions, 2.4% above the datasheet**.

That difference is inside the precision of the method. A quarter turn of
misalignment over ten revolutions is 2.5%, so the residual is consistent with
stopping slightly past the mark rather than with the datasheet being wrong.
**6400 is kept**, and the measurement is recorded rather than the figure being
silently adjusted to match one hand-turned trial.

An earlier attempt without a mark gave 5288 or 6610 per revolution depending
on whether the operator had turned four revolutions or five, which is why the
mark matters: over one revolution a quarter turn of error is 25%.

The value worth confirming later is not this one on its own but the product of
radius and counts, since that is what converts counts into distance. Rolling
the assembled rover a measured three metres and comparing against the reported
odometry tests both at once, and should be done before the odometry is relied
on for navigation.

## Output assignment

Skid steer needs two distinct commands, a left throttle and a right throttle,
however many wheels there are. ArduPilot allows several outputs to carry the
same function, so four channels are driven from four outputs rather than by
splitting two signals in the wiring:

| Output | `SERVO*_FUNCTION` | Goes to |
| --- | --- | --- |
| MAIN 1 | 73, `ThrottleLeft` | left controller, S1 |
| MAIN 2 | 73, `ThrottleLeft` | left controller, S2 |
| MAIN 3 | 74, `ThrottleRight` | right controller, S1 |
| MAIN 4 | 74, `ThrottleRight` | right controller, S2 |

The function numbers are read from `SRV_Channel.h:117-118` at the pinned
revision `1511f271`, so they match the firmware actually flashed rather than
whatever a wiki page says about some other version.

Signal and ground are connected; **the +5V pin is not**. Both controllers and
the autopilot already have their own supplies, so joining the 5V lines would
tie two regulators together for no benefit. Ground is connected even though
the two are already common through the battery, because the power ground
carries motor current and the voltage it drops moves the reference the PWM
signal is measured against.

This assignment is **not yet validated**. Nothing here has been confirmed
against the vehicle: it records what is to be set and why, and the checklist
below is what would establish that it works.

## Required bench-validation checklist

- [ ] Confirm Pixhawk output and RoboClaw input electrical-signal compatibility
  using the exact hardware revisions.
- [ ] Confirm the required shared-ground arrangement and safe power-up order.
- [ ] Calibrate neutral independently for the left and right inputs and record
  the validated values outside this document until exported from the real
  configuration.
- [ ] Verify forward/reverse direction for both motor groups and document any
  intentional reversal.
- [ ] Remove or interrupt the control signal and verify the observed signal-loss
  response before operating the rover off the bench.
- [ ] Measure continuous and transient motor current and verify controller,
  wiring, connector, and power-system capacity.
- [ ] Test starting, stall, turning, and terrain loading on all four channels,
  including skid-steer pivot turns.
- [ ] Confirm RoboClaw mixing is disabled on both controllers, so that only
  ArduPilot mixes.

Each completed item should record the hardware identifiers, ArduPilot firmware
version, configuration-export reference, test date, operator, method,
measurements, and pass/fail result.

## Motor-selection inputs still required

- maximum course slope
- step and obstacle height
- final wheel diameter and width
- granular-terrain rolling and turning resistance
- measured starting, running, transient, and stall currents

Motor and drivetrain sizing must cover the worst validated case among climbing,
step traversal, granular terrain, and skid-steer rotation, with an explicit
engineering margin.
