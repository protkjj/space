#!/usr/bin/env python3
"""
Set named autopilot parameters, and prove afterwards that they took.

Every other script here reads. This one writes, so it is deliberately narrow:
it touches only parameters named on the command line, shows the old value
beside the new one before doing anything, asks for confirmation, and reads
each value back afterwards. A write that does not read back as requested is
reported as a failure rather than assumed to have worked.

Parameters are refused silently by ArduPilot more often than one would like --
a name that does not exist on this vehicle produces no error, just no change.
Reading back is what turns that into something visible.

Usage::

    ./set_params.py SERVO1_FUNCTION=73 SERVO3_FUNCTION=74
    ./set_params.py --device /dev/ttyACM0 BRD_SAFETY_DEFLT=0
    ./set_params.py --yes SERVO1_FUNCTION=73        # skip the confirmation
"""

import argparse
import sys
import time

try:
    from pymavlink import mavutil
except ImportError:
    sys.exit(
        'pymavlink is not installed.\n'
        '  python3 -m pip install --user --break-system-packages pymavlink'
    )


# ArduPilot stores integers in a float field, so a value is "the same" when it
# lands within half a unit rather than exactly. Real-valued parameters are
# compared on the same tolerance, which is loose for them but never wrong for
# the integer parameters this is mostly used on.
TOLERANCE = 0.001


def parse_assignment(text):
    """Return (NAME, value) from a NAME=VALUE argument."""
    if '=' not in text:
        raise ValueError(f'expected NAME=VALUE, got {text!r}')
    name, _, raw = text.partition('=')
    name = name.strip().upper()
    if not name:
        raise ValueError(f'empty parameter name in {text!r}')
    if len(name) > 16:
        raise ValueError(f'parameter names are at most 16 characters: {name}')
    try:
        value = float(raw.strip())
    except ValueError:
        raise ValueError(f'{raw.strip()!r} is not a number, in {text!r}')
    return name, value


def parse_args():
    """Return parsed command-line options."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('assignments', nargs='+', metavar='NAME=VALUE')
    parser.add_argument('--device', default='/dev/ttyACM0',
                        help='MAVLink serial device (not the DDS one)')
    parser.add_argument('--baud', type=int, default=115200)
    parser.add_argument('--yes', action='store_true',
                        help='do not ask before writing')
    return parser.parse_args()


def connect(device, baud):
    """Open the link and wait for the autopilot."""
    print(f'connecting to {device}')
    conn = mavutil.mavlink_connection(device, baud=baud, source_system=243)
    if conn.wait_heartbeat(timeout=20) is None:
        sys.exit(f'no heartbeat from {device}')
    print(f'connected: system={conn.target_system}')
    return conn


def read_param(conn, name, timeout=5.0):
    """
    Return (value, type) for one parameter, or (None, None).

    The request is re-sent while waiting rather than asked once and hoped
    for, because a single request that arrives during a busy moment is simply
    lost and the caller would otherwise conclude the parameter is absent.
    """
    deadline = time.time() + timeout
    next_request = 0.0
    while time.time() < deadline:
        if time.time() >= next_request:
            conn.mav.param_request_read_send(
                conn.target_system, conn.target_component,
                name.encode('ascii'), -1)
            next_request = time.time() + 1.0
        msg = conn.recv_match(type='PARAM_VALUE', blocking=True, timeout=0.5)
        if msg is None:
            continue
        if msg.param_id.strip('\x00') == name:
            return msg.param_value, msg.param_type
    return None, None


def write_param(conn, name, value, param_type):
    """Send one parameter value."""
    conn.mav.param_set_send(
        conn.target_system, conn.target_component,
        name.encode('ascii'), float(value), param_type)


def main():
    """Set the named parameters and verify each one."""
    args = parse_args()

    try:
        wanted = [parse_assignment(text) for text in args.assignments]
    except ValueError as exc:
        sys.exit(str(exc))

    names = [name for name, _ in wanted]
    if len(set(names)) != len(names):
        sys.exit('the same parameter is named more than once')

    conn = connect(args.device, args.baud)

    print('\n--- current values ---')
    current = {}
    missing = []
    for name, target in wanted:
        value, param_type = read_param(conn, name)
        current[name] = (value, param_type)
        if value is None:
            missing.append(name)
            print(f'  {name:20s} NOT FOUND')
        elif abs(value - target) <= TOLERANCE:
            print(f'  {name:20s} {value:g}  (already {target:g})')
        else:
            print(f'  {name:20s} {value:g}  ->  {target:g}')

    if missing:
        print('\nThese parameters do not exist on this vehicle:')
        for name in missing:
            print(f'  {name}')
        print('Check the spelling against an export before writing anything.')
        return 1

    changes = [(name, target) for name, target in wanted
               if abs(current[name][0] - target) > TOLERANCE]
    if not changes:
        print('\nEverything is already set. Nothing to write.')
        return 0

    if not args.yes:
        reply = input(f'\nWrite {len(changes)} parameter(s)? [yes/N] ')
        if reply.strip().lower() not in ('y', 'yes'):
            print('Aborted. Nothing was written.')
            return 1

    print('\n--- writing ---')
    for name, target in changes:
        write_param(conn, name, target, current[name][1])
        print(f'  {name:20s} sent {target:g}')
    # The autopilot applies and stores a parameter asynchronously, so reading
    # back immediately can return the old value and look like a failure.
    time.sleep(0.5)

    print('\n--- reading back ---')
    failures = []
    for name, target in changes:
        value, _ = read_param(conn, name)
        if value is None:
            failures.append((name, target, None))
            print(f'  {name:20s} no reply')
        elif abs(value - target) > TOLERANCE:
            failures.append((name, target, value))
            print(f'  {name:20s} {value:g}  WANTED {target:g}')
        else:
            print(f'  {name:20s} {value:g}  ok')

    print('\n' + '=' * 58)
    if failures:
        print(f'{len(failures)} of {len(changes)} did not take.')
        print('A parameter can be refused because the value is out of range,')
        print('or because it is read-only while armed. Nothing here retries,')
        print('because a silent retry would hide the reason.')
        return 1
    print(f'All {len(changes)} verified against the vehicle.')
    print('Parameters marked @RebootRequired need a reboot to take effect;')
    print('this cannot tell which those are, so check the ones you changed.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
