# ArduPilot firmware and configuration

ArduPilot source is not vendored in this repository. This directory records the
exact external firmware version selected by the project, validated
configuration exports, and reproducible export/validation procedures.

## Phase 1 status

[`version.txt`](version.txt) is `UNPINNED`. No ArduPilot release or commit is
considered selected until Rover SITL, the ArduPilot Gazebo plugin, DDS
interfaces, and the Pixhawk 6X hardware target are validated as a compatible
set.

No Pixhawk or SITL `.param` export exists in Phase 1. Do not create a parameter
file by copying assumed defaults or inventing values.

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
