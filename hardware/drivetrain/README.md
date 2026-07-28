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

- a Jetson-side RoboClaw packet-serial driver
- a direct ROS-to-RoboClaw control path
- serial device configuration
- PWM ranges, neutral values, or output-channel assignments
- assumed current ratings or failsafe behavior

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
