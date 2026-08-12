#!/usr/bin/env python3
"""
Export autopilot parameters, with the provenance the repository requires.

Reads every parameter over MAVLink and writes an ArduPilot-format ``.param``
file with a header recording the firmware version, board, date, and how the
export was produced. ``firmware/ardupilot/params/README.md`` requires that
provenance; an export without it should not be committed.

This only reads. It never writes a parameter, arms, or changes a mode.

Usage::

    ./export_params.py                          # full export to a dated file
    ./export_params.py --device /dev/ttyACM0
    ./export_params.py --show BATT              # print matching params only
    ./export_params.py --out rover_bench.param
"""

import argparse
import glob
import sys
import time

try:
    from pymavlink import mavutil
except ImportError:
    sys.exit(
        'pymavlink is not installed.\n'
        '  python3 -m pip install --user --break-system-packages pymavlink'
    )


USB_DEVICE_PATTERNS = (
    '/dev/ttyACM*',
    '/dev/serial/by-id/*',
    '/dev/cu.usbmodem*',
)


def autodetect():
    """Return a single candidate device, or exit explaining what was found."""
    candidates = sorted(
        path for pattern in USB_DEVICE_PATTERNS for path in glob.glob(pattern)
    )
    if not candidates:
        sys.exit(
            'No autopilot device found.\n'
            f'Looked for: {", ".join(USB_DEVICE_PATTERNS)}\n'
            'Pass one explicitly with --device.'
        )
    if len(candidates) > 1:
        # A board exposing two CDC interfaces is normal; the first is the
        # MAVLink one. Say so rather than silently guessing.
        print(f'Multiple devices found, using {candidates[0]}:')
        for path in candidates:
            print(f'  {path}')
    return candidates[0]


def parse_args():
    """Return parsed command-line options."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--device', help='MAVLink serial device')
    parser.add_argument('--baud', type=int, default=115200)
    parser.add_argument('--out', help='output .param path')
    parser.add_argument('--show', metavar='PREFIX',
                        help='print parameters starting with PREFIX and exit')
    parser.add_argument('--timeout', type=float, default=90.0,
                        help='seconds to wait for the full parameter set')
    return parser.parse_args()


def identity(conn):
    """Return a dict describing the connected autopilot, best effort."""
    info = {}
    conn.mav.command_long_send(
        conn.target_system, conn.target_component,
        mavutil.mavlink.MAV_CMD_REQUEST_MESSAGE, 0,
        mavutil.mavlink.MAVLINK_MSG_ID_AUTOPILOT_VERSION, 0, 0, 0, 0, 0, 0,
    )
    msg = conn.recv_match(type='AUTOPILOT_VERSION', blocking=True, timeout=10)
    if msg is None:
        info['firmware'] = 'AUTOPILOT_VERSION not received'
        return info

    raw = msg.flight_sw_version
    info['firmware'] = (
        f'{(raw >> 24) & 0xFF}.{(raw >> 16) & 0xFF}.{(raw >> 8) & 0xFF}'
    )
    # ArduPilot stores the git hash here as ASCII characters, not packed
    # bytes, so hex-encoding it would produce something that cannot be
    # compared against the pin in version.txt.
    raw = getattr(msg, 'flight_custom_version', None)
    if raw:
        data = bytes(byte & 0xFF for byte in raw).rstrip(b'\x00')
        text = data.decode('ascii', 'replace').strip()
        if text and all(character.isprintable() for character in text):
            info['commit'] = text
        else:
            info['commit'] = ''.join(f'{byte:02x}' for byte in data)
    info['board'] = f'vendor {msg.vendor_id} product {msg.product_id}'
    return info


def fetch_all(conn, timeout):
    """Request every parameter and return {name: (value, index, count)}."""
    conn.mav.param_request_list_send(
        conn.target_system, conn.target_component
    )
    found = {}
    expected = None
    last_new = time.time()
    deadline = time.time() + timeout

    while time.time() < deadline:
        msg = conn.recv_match(type='PARAM_VALUE', blocking=True, timeout=2)
        if msg is None:
            # Nothing arriving and nothing new for a while means it is done
            # or stalled; either way stop rather than block for the full
            # timeout.
            if time.time() - last_new > 8:
                break
            continue
        name = msg.param_id
        if isinstance(name, bytes):
            name = name.decode('ascii', 'replace')
        name = name.strip('\x00')
        if name not in found:
            last_new = time.time()
            if len(found) % 200 == 0 and found:
                print(f'  {len(found)}/{msg.param_count}')
        found[name] = (msg.param_value, msg.param_index, msg.param_count)
        expected = msg.param_count
        if expected and len(found) >= expected:
            break

    return found, expected


def write_export(path, params, info, device, expected):
    """Write the .param file with a provenance header."""
    missing = (expected - len(params)) if expected else None
    with open(path, 'w') as handle:
        handle.write('# ArduPilot parameter export\n')
        handle.write('#\n')
        firmware = info.get('firmware', 'unknown')
        handle.write(f'# firmware version : {firmware}\n')
        if 'commit' in info:
            handle.write(f'# firmware commit  : {info["commit"]}\n')
        handle.write(f'# board            : {info.get("board", "unknown")}\n')
        handle.write(f'# source device    : {device}\n')
        handle.write(f'# parameters read  : {len(params)}\n')
        handle.write(f'# parameters total : {expected}\n')
        if missing:
            handle.write(
                f'# INCOMPLETE       : {missing} parameter(s) not received; '
                're-run before treating this as a backup\n'
            )
        handle.write('#\n')
        handle.write('# Fill in before committing, per params/README.md:\n')
        handle.write('#   physical hardware identifier :\n')
        handle.write('#   export date                  :\n')
        handle.write('#   operator                     :\n')
        handle.write('#   vehicle/model revision       :\n')
        handle.write('#   validation status            :\n')
        handle.write('#   link to validation record    :\n')
        handle.write('#\n')
        for name in sorted(params):
            handle.write(f'{name},{params[name][0]:.6f}\n')
    return missing


def main():
    """Connect, read every parameter, and write or print the result."""
    args = parse_args()
    device = args.device or autodetect()

    print(f'connecting to {device}')
    conn = mavutil.mavlink_connection(
        device, baud=args.baud, source_system=242
    )
    if conn.wait_heartbeat(timeout=20) is None:
        sys.exit(f'no heartbeat from {device}')
    print(f'connected: system={conn.target_system}')

    info = identity(conn)
    print(f'firmware: {info.get("firmware", "unknown")}')

    print('reading parameters (this takes up to a minute)...')
    params, expected = fetch_all(conn, args.timeout)
    print(f'read {len(params)} of {expected} parameters')

    if args.show:
        prefix = args.show.upper()
        matches = sorted(n for n in params if n.startswith(prefix))
        if not matches:
            print(f'\nno parameters start with {prefix}')
            print('(if this is unexpected, the read may be incomplete)')
            return 1
        print()
        for name in matches:
            print(f'{name} = {params[name][0]}')
        return 0

    out = args.out or 'autopilot_params.param'
    missing = write_export(out, params, info, device, expected)
    print(f'\nwrote {out}')
    if missing:
        print(f'WARNING: {missing} parameter(s) missing; re-run before '
              'relying on this as a backup')
        return 1
    print('Complete export. Fill in the provenance header before committing.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
