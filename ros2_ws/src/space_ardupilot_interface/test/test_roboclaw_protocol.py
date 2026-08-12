"""Unit tests for the read-only RoboClaw packet framing."""

import struct

import pytest
from space_ardupilot_interface.roboclaw_protocol import (
    check_reply,
    CMD_GET_ENCODERS,
    CMD_GET_SPEEDS,
    crc16,
    DEFAULT_ADDRESS,
    expected_reply_length,
    parse_encoders,
    parse_speeds,
    read_request,
)


def encoder_reply(first, second, request):
    """Build a well-formed encoder reply for the given request."""
    payload = struct.pack('>II', first, second)
    return payload + struct.pack('>H', crc16(bytes(request) + payload))


def test_request_is_address_then_command():
    assert read_request(CMD_GET_ENCODERS) == bytes((0x80, 78))
    assert read_request(CMD_GET_ENCODERS, address=0x81) == bytes((0x81, 78))


def test_only_read_commands_can_be_framed():
    # There is no path in this module that builds a motion command. ArduPilot
    # owns motion; a second writer would be two controllers with no
    # arbitration between them.
    for motion_command in (32, 33, 34, 35, 36, 37):
        with pytest.raises(ValueError, match='writing to the controller'):
            read_request(motion_command)


def test_crc_matches_a_known_value():
    # CCITT with polynomial 0x1021 seeded at zero.
    assert crc16(b'') == 0
    assert crc16(b'\x00') == 0
    assert crc16(b'\x01') == 0x1021
    assert crc16(bytes((DEFAULT_ADDRESS, CMD_GET_ENCODERS))) == crc16(
        b'\x80\x4e')


def test_encoders_round_trip():
    request = read_request(CMD_GET_ENCODERS)
    reply = encoder_reply(123456, 654321, request)
    assert parse_encoders(request, reply) == (123456, 654321)


def test_encoder_counts_near_the_wrap_are_returned_unchanged():
    # The consumer takes differences modulo the counter, so a value just below
    # the wrap is data rather than an error.
    request = read_request(CMD_GET_ENCODERS)
    top = (1 << 32) - 1
    reply = encoder_reply(top, 0, request)
    assert parse_encoders(request, reply) == (top, 0)


def test_a_corrupted_payload_is_rejected():
    request = read_request(CMD_GET_ENCODERS)
    reply = bytearray(encoder_reply(1000, 2000, request))
    reply[0] ^= 0xFF
    # This is the case that matters: without the CRC the count would parse
    # cleanly and produce a plausible pose that is quietly wrong.
    assert parse_encoders(request, bytes(reply)) is None


def test_a_corrupted_crc_is_rejected():
    request = read_request(CMD_GET_ENCODERS)
    reply = bytearray(encoder_reply(1000, 2000, request))
    reply[-1] ^= 0xFF
    assert parse_encoders(request, bytes(reply)) is None


def test_a_reply_to_a_different_request_is_rejected():
    # The CRC covers the request bytes, so a reply cannot be attributed to a
    # request that did not produce it.
    sent = read_request(CMD_GET_ENCODERS, address=0x80)
    other = read_request(CMD_GET_ENCODERS, address=0x81)
    reply = encoder_reply(500, 600, other)
    assert parse_encoders(sent, reply) is None


@pytest.mark.parametrize('short_by', [1, 2, 5])
def test_a_truncated_reply_is_rejected(short_by):
    request = read_request(CMD_GET_ENCODERS)
    reply = encoder_reply(10, 20, request)
    assert parse_encoders(request, reply[:-short_by]) is None


def test_an_over_long_reply_is_rejected():
    request = read_request(CMD_GET_ENCODERS)
    reply = encoder_reply(10, 20, request)
    assert parse_encoders(request, reply + b'\x00') is None


def test_an_empty_reply_is_rejected():
    request = read_request(CMD_GET_ENCODERS)
    assert parse_encoders(request, b'') is None


def test_speeds_are_signed():
    request = read_request(CMD_GET_SPEEDS)
    payload = struct.pack('>ii', -1500, 1500)
    reply = payload + struct.pack('>H', crc16(bytes(request) + payload))
    assert parse_speeds(request, reply) == (-1500, 1500)


def test_check_reply_returns_the_payload_only():
    request = read_request(CMD_GET_ENCODERS)
    reply = encoder_reply(7, 8, request)
    payload = check_reply(request, reply, 8)
    assert payload == reply[:8]


def test_expected_reply_length():
    assert expected_reply_length(CMD_GET_ENCODERS) == 10
    assert expected_reply_length(CMD_GET_SPEEDS) == 10
    with pytest.raises(ValueError, match='no known reply length'):
        expected_reply_length(73)
