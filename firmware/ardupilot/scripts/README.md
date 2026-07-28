# ArduPilot support scripts

This directory is reserved for reproducible configuration-export and validation
scripts after a real ArduPilot version and workflow are selected.

Phase 1 deliberately contains no placeholder SITL start script, guessed
executable path, arbitrary network endpoint, serial device, or fabricated
validation command. Future scripts must:

- fail clearly when required external tools or versions are missing
- avoid embedding secrets or machine-specific device assumptions
- record or verify the pinned ArduPilot version
- identify the target board or SITL target
- make parameter export and validation steps reproducible
