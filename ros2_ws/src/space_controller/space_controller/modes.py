"""
Numeric rover-mode protocol carried by ``std_msgs/msg/UInt8``.

Phase 1 preserves the existing ``/space/mode`` contract:

* ``0``: ROVER, accept fresh driving commands.
* ``1``: HOLD, reject driving commands and publish stop commands.
* ``2``: EMERGENCY, reject driving commands and publish stop commands.
"""

from enum import IntEnum


class DriveMode(IntEnum):
    """Named values for the Phase 1 UInt8 mode protocol."""

    ROVER = 0
    HOLD = 1
    EMERGENCY = 2
