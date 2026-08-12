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
brushed DC gearmotors, with each side grouped onto one RoboClaw motor channel.
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

None of this has been confirmed against a unit. Reply lengths and field
layouts must be checked against a live response before any parser is trusted,
because a misread count does not fail loudly — it produces a plausible pose
that is quietly wrong.

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
- [ ] Test two-motors-per-channel starting, stall, turning, and terrain loading,
  including skid-steer pivot turns.

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
