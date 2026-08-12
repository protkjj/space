#!/usr/bin/env python3
"""
Frame and parse the RoboClaw packet-serial replies this rover reads.

Only reading is implemented, and deliberately so. ArduPilot owns motion on
this rover; a second writer would mean two controllers driving the same motors
with no arbitration. Nothing here can command a motor: there is no function
that builds a motion command, and the only commands framed are reads.

The wheel odometry needs one command, 78 `GETENCODERS`, whose two-byte request
and ten-byte reply appear in every manual revision and in both the legacy and
current vendor libraries. Command 73 `Read All Status` returns the same
encoder data among other values and saves round trips, but contributes nothing
unique, so the odometry does not depend on it being present.

Every reply is checked against its CRC before any value is believed. That
matters more than usual here: a misframed reply would otherwise yield a
plausible count, and a plausible-but-wrong count produces a plausible-but-
wrong pose that nothing downstream can detect. With the check, a framing
mistake fails loudly instead.
"""

import struct
from typing import Optional, Tuple


# Packet serial default address. Each controller sits on its own USB device
# here, so both can keep the default rather than being re-addressed.
DEFAULT_ADDRESS = 0x80

CMD_GET_ENCODERS = 78
CMD_GET_SPEEDS = 79
CMD_READ_FIRMWARE = 21

# Reply payloads, excluding the trailing CRC16.
ENCODERS_PAYLOAD_BYTES = 8
SPEEDS_PAYLOAD_BYTES = 8
CRC_BYTES = 2

_CRC_POLYNOMIAL = 0x1021
_COUNTER_MODULUS = 1 << 32


def crc16(data: bytes, seed: int = 0) -> int:
    """
    Return the CRC16 the controller uses, over the given bytes.

    CCITT with polynomial 0x1021, seeded at zero, and computed across the
    request and the reply together rather than over the reply alone.
    """
    crc = seed
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ _CRC_POLYNOMIAL) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc


def read_request(command: int, address: int = DEFAULT_ADDRESS) -> bytes:
    """Return the two bytes that ask for one read-only value."""
    if command not in (CMD_GET_ENCODERS, CMD_GET_SPEEDS, CMD_READ_FIRMWARE):
        raise ValueError(
            f'command {command} is not one of the read commands this module '
            'supports; writing to the controller is not implemented'
        )
    return bytes((address & 0xFF, command & 0xFF))


def check_reply(request: bytes, reply: bytes,
                payload_bytes: int) -> Optional[bytes]:
    """
    Return the payload if the CRC matches, and None if it does not.

    The CRC covers the request bytes as well as the payload, so both are
    needed to verify a reply.
    """
    if len(reply) != payload_bytes + CRC_BYTES:
        return None
    payload = reply[:payload_bytes]
    received = struct.unpack('>H', reply[payload_bytes:])[0]
    expected = crc16(bytes(request) + payload)
    if received != expected:
        return None
    return payload


def parse_encoders(request: bytes,
                   reply: bytes) -> Optional[Tuple[int, int]]:
    """
    Return (encoder1, encoder2) as signed counts, or None on a bad reply.

    The controller sends unsigned big-endian 32-bit values that wrap; they are
    returned as-is rather than sign-extended, because the consumer takes
    differences modulo the counter and a wrap is one count of motion.
    """
    payload = check_reply(request, reply, ENCODERS_PAYLOAD_BYTES)
    if payload is None:
        return None
    first, second = struct.unpack('>II', payload)
    return first % _COUNTER_MODULUS, second % _COUNTER_MODULUS


def parse_speeds(request: bytes, reply: bytes) -> Optional[Tuple[int, int]]:
    """Return (speed1, speed2) in counts per second, or None on a bad reply."""
    payload = check_reply(request, reply, SPEEDS_PAYLOAD_BYTES)
    if payload is None:
        return None
    return struct.unpack('>ii', payload)


def expected_reply_length(command: int) -> int:
    """Return how many bytes a reply to this read command occupies."""
    if command == CMD_GET_ENCODERS:
        return ENCODERS_PAYLOAD_BYTES + CRC_BYTES
    if command == CMD_GET_SPEEDS:
        return SPEEDS_PAYLOAD_BYTES + CRC_BYTES
    raise ValueError(f'no known reply length for command {command}')
