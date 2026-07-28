# ArduPilot parameter exports

This directory intentionally contains no `.param` files in Phase 1.

Add a parameter file only after exporting it from a real, validated Pixhawk or
SITL configuration. Do not create placeholder exports or fill unknown values
from assumptions.

Each export must have an accompanying record containing:

- exact ArduPilot release or commit
- target board
- physical hardware identifier, or explicit SITL target identifier
- export date
- validation status
- export tool and reproducible procedure
- operator or owner
- vehicle/model revision
- applicable validation results

Use names that distinguish the target and configuration purpose without
embedding secrets. Review exports before committing them; device credentials,
network secrets, and unrelated local configuration must not be included.
