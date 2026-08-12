#!/usr/bin/env python3
"""
Verify the RoboClaw read protocol against a real controller.

The encoder parser was written from the manual and from the vendor's own
driver, without a unit to try it on. This checks it against one, and it does
so through the same module the rover uses, so a pass here validates the code
that will actually run rather than a copy of it.

One controller is enough. The open question is the byte layout and the CRC,
not how many units answer.

**Read-only.** It sends only read commands, and the protocol module it uses
cannot frame a motion command at all. Nothing here can turn a motor. It is
still worth raising the wheels first: this confirms an assumption, and an
assumption worth confirming is one that might be wrong.

Usage::

    ./probe_roboclaw.py                        # autodetect a single device
    ./probe_roboclaw.py /dev/ttyACM0
    ./probe_roboclaw.py /dev/ttyACM0 --address 0x81 --seconds 10
"""

import argparse
import glob
import os
import sys
import time

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', '..', '..', 'ros2_ws', 'src', 'space_ardupilot_interface',
))

try:
    from space_ardupilot_interface.roboclaw_protocol import (
        CMD_GET_ENCODERS,
        CMD_GET_SPEEDS,
        CMD_READ_FIRMWARE,
        crc16,
        DEFAULT_ADDRESS,
        expected_reply_length,
        parse_encoders,
        parse_speeds,
        read_request,
    )
except ImportError as exc:
    sys.exit(
        f'cannot import the rover protocol module: {exc}\n'
        'Run this from a checkout with ros2_ws/src present, so that a pass '
        'here validates the code the rover actually uses.'
    )

try:
    import serial
except ImportError:
    sys.exit(
        'pyserial is not installed.\n'
        '  python3 -m pip install --user --break-system-packages pyserial'
    )


def autodetect() -> str:
    """Return a single candidate device, or exit saying what was found."""
    candidates = sorted(glob.glob('/dev/ttyACM*') + glob.glob('/dev/ttyUSB*'))
    if not candidates:
        sys.exit('no /dev/ttyACM* or /dev/ttyUSB* device found')
    if len(candidates) > 1:
        sys.exit(
            'several candidate devices; pass one explicitly:\n  '
            + '\n  '.join(candidates)
            + '\nA Pixhawk also appears as ttyACM, so check '
              '/dev/serial/by-id to tell them apart.'
        )
    return candidates[0]


def parse_args():
    """Return parsed command-line options."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('device', nargs='?', help='serial device')
    parser.add_argument('--baud', type=int, default=115200)
    parser.add_argument('--address', type=lambda v: int(v, 0),
                        default=DEFAULT_ADDRESS)
    parser.add_argument('--seconds', type=float, default=8.0,
                        help='how long to stream encoder counts')
    return parser.parse_args()


def exchange(port, command, address, payload_bytes):
    """Send one read command and return (request, raw reply)."""
    request = read_request(command, address)
    port.reset_input_buffer()
    port.write(request)
    reply = port.read(payload_bytes + 2)
    return request, reply


def probe_firmware(port, address):
    """Read the firmware string, which also proves the address is right."""
    print('\n--- firmware version (command 21) ---')
    request = read_request(CMD_READ_FIRMWARE, address)
    port.reset_input_buffer()
    port.write(request)
    # The version reply is a variable-length string terminated by a null,
    # followed by the CRC, so it is read by timeout rather than by length.
    raw = port.read(64)
    if not raw:
        print('  no reply. Wrong address, wrong baud, or wrong device.')
        return False
    text = raw.split(b'\x00')[0].decode('ascii', 'replace').strip()
    print(f'  {text!r}')
    print(f'  raw: {raw.hex()}')
    return True


def probe_encoders(port, address, seconds):
    """Stream encoder counts, verifying every reply."""
    print(f'\n--- encoders (command 78) for {seconds:.0f}s ---')
    print('  Turn a wheel by hand; the counts should move.')
    print('  count1      count2      delta1   delta2   status')

    good = 0
    bad = 0
    first = None
    previous = None
    deadline = time.time() + seconds
    next_print = 0.0

    while time.time() < deadline:
        request, reply = exchange(
            port, CMD_GET_ENCODERS, address,
            expected_reply_length(CMD_GET_ENCODERS) - 2)
        counts = parse_encoders(request, reply)
        if counts is None:
            bad += 1
            if bad <= 3:
                print(f'  CRC or framing failed. raw: {reply.hex()!r}')
        else:
            good += 1
            if first is None:
                first = counts
            if time.time() >= next_print:
                d1 = counts[0] - (previous[0] if previous else counts[0])
                d2 = counts[1] - (previous[1] if previous else counts[1])
                print(f'  {counts[0]:<11d} {counts[1]:<11d} '
                      f'{d1:<8d} {d2:<8d} ok')
                previous = counts
                next_print = time.time() + 0.5
        time.sleep(0.02)

    print(f'\n  verified {good}, rejected {bad}')
    if first is not None and previous is not None:
        print(f'  moved {previous[0] - first[0]} and '
              f'{previous[1] - first[1]} counts during the probe')
    return good, bad


def probe_speeds(port, address):
    """Read measured speeds, which the slip calculation will want."""
    print('\n--- speeds (command 79) ---')
    request, reply = exchange(
        port, CMD_GET_SPEEDS, address,
        expected_reply_length(CMD_GET_SPEEDS) - 2)
    speeds = parse_speeds(request, reply)
    if speeds is None:
        print(f'  CRC or framing failed. raw: {reply.hex()!r}')
        return False
    print(f'  {speeds[0]} and {speeds[1]} counts per second')
    return True


def probe_status(port, address):
    """Try command 73, which is an optimisation rather than a requirement."""
    print('\n--- read all status (command 73), optional ---')
    # 73 is not in the module's allowed read list, because the rover does not
    # use it. Frame it here directly so the probe can report whether it works
    # without widening what the rover is able to send.
    frame = bytes((address & 0xFF, 73))
    port.reset_input_buffer()
    port.write(frame)
    reply = port.read(64)
    if not reply:
        print('  no reply; the odometry path does not need this command')
        return
    print(f'  {len(reply)} bytes: {reply.hex()}')
    if len(reply) >= 2:
        payload = reply[:-2]
        received = int.from_bytes(reply[-2:], 'big')
        expected = crc16(frame + payload)
        match = 'matches' if received == expected else 'does NOT match'
        print(f'  CRC over {len(payload)} payload bytes {match}')


def main():
    """Probe one controller and report whether the parser handles it."""
    args = parse_args()
    device = args.device or autodetect()

    reply = input(
        'This only reads, but it confirms an assumption that might be '
        'wrong.\nAre the wheels off the ground? [yes/N] ').strip().lower()
    if reply not in ('y', 'yes'):
        sys.exit('Aborted. Raise the wheels first.')

    print(f'\nopening {device} at {args.baud} baud, '
          f'address 0x{args.address:02x}')
    port = serial.Serial(device, args.baud, timeout=0.1)

    try:
        if not probe_firmware(port, args.address):
            print('\nNo reply to the simplest read. Nothing below will work.')
            print('Check the device, the baud rate, and the address.')
            return 1
        good, bad = probe_encoders(port, args.address, args.seconds)
        probe_speeds(port, args.address)
        probe_status(port, args.address)
    finally:
        port.close()

    print('\n' + '=' * 58)
    print('VERDICT')
    print('=' * 58)
    if good and not bad:
        print("  Every reply verified. The rover's parser handles this")
        print('  controller, and the encoder path is confirmed end to end.')
        return 0
    if good and bad:
        print(f'  {bad} of {good + bad} replies failed verification.')
        print('  The parser is right but the link is marginal: check the')
        print('  cable and the baud rate before trusting the odometry.')
        return 1
    print('  No reply verified. The reply layout differs from what the')
    print('  parser expects; send the raw bytes above rather than adjusting')
    print('  the parser by guesswork.')
    return 1


if __name__ == '__main__':
    sys.exit(main())
