#!/usr/bin/env python3
"""Probe a connected autopilot and report its identity and DDS capability.

This script only reads. It never arms, never changes a mode, and never writes
a parameter.

It answers the questions that block the Milestone A hardware path:

- which ArduPilot version and board is actually flashed
- whether the flashed build contains AP_DDS at all (``DDS_ENABLE`` present)
- which serial port, if any, is already configured for DDS

Usage::

    ./probe_autopilot.py                      # default USB device glob
    ./probe_autopilot.py /dev/ttyACM0
    ./probe_autopilot.py udp:127.0.0.1:14550

Nothing about the connection is assumed: the endpoint must be passed or must
match one of the auto-detected USB devices, and the script fails loudly rather
than guessing.
"""

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


# Parameters that decide whether the DDS path is usable on this build.
DDS_PARAMS = (
    'DDS_ENABLE',
    'DDS_UDP_PORT',
    'DDS_IP0',
    'DDS_DOMAIN_ID',
)

# Serial protocol number for DDS/XRCE, per AP_SerialManager.
SERIAL_PROTOCOL_DDS_XRCE = 45

SERIAL_PROTOCOL_PARAMS = tuple(
    f'SERIAL{index}_PROTOCOL' for index in range(0, 8)
)


# USB serial device patterns. Linux exposes ArduPilot boards as ttyACM*;
# macOS exposes them as cu.usbmodem*. Both are listed so the same script
# works from either host without being told which one it is on.
USB_DEVICE_PATTERNS = (
    '/dev/ttyACM*',
    '/dev/serial/by-id/*',
    '/dev/cu.usbmodem*',
)


def autodetect() -> str:
    """Return a single USB autopilot device or exit with what was found."""
    candidates = sorted(
        path
        for pattern in USB_DEVICE_PATTERNS
        for path in glob.glob(pattern)
    )
    if not candidates:
        sys.exit(
            'No USB autopilot device found.\n'
            f'Looked for: {", ".join(USB_DEVICE_PATTERNS)}\n'
            'Check that the board is powered and the cable carries data, '
            'then pass the endpoint explicitly, e.g.:\n'
            '  ./probe_autopilot.py /dev/ttyACM0            # Linux\n'
            '  ./probe_autopilot.py /dev/cu.usbmodem01      # macOS\n'
            '  ./probe_autopilot.py udp:127.0.0.1:14550'
        )
    if len(candidates) > 1:
        sys.exit(
            'Multiple candidate devices found; pass one explicitly:\n  '
            + '\n  '.join(candidates)
        )
    return candidates[0]


def connect(endpoint: str):
    """Open the link and block until the autopilot heartbeats."""
    print(f'connecting to {endpoint}')
    if endpoint.startswith(('udp:', 'tcp:', 'udpin:', 'udpout:')):
        master = mavutil.mavlink_connection(endpoint, source_system=255)
    else:
        master = mavutil.mavlink_connection(
            endpoint, baud=115200, source_system=255
        )

    if master.wait_heartbeat(timeout=15) is None:
        sys.exit(f'No heartbeat from {endpoint} within 15s.')
    print(
        f'heartbeat: system={master.target_system} '
        f'component={master.target_component}'
    )
    return master


def report_version(master) -> None:
    """Request and print AUTOPILOT_VERSION, or say it was not received."""
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_REQUEST_MESSAGE,
        0,
        mavutil.mavlink.MAVLINK_MSG_ID_AUTOPILOT_VERSION,
        0, 0, 0, 0, 0, 0,
    )
    message = master.recv_match(
        type='AUTOPILOT_VERSION', blocking=True, timeout=10
    )
    print('\n--- autopilot identity ---')
    if message is None:
        print('AUTOPILOT_VERSION: not received within 10s')
        return

    raw = message.flight_sw_version
    print(
        'flight_sw_version: '
        f'{(raw >> 24) & 0xFF}.{(raw >> 16) & 0xFF}.{(raw >> 8) & 0xFF}'
    )
    commit = getattr(message, 'flight_custom_version', None)
    if commit:
        print(
            'flight_custom_version: '
            + ''.join(f'{byte:02x}' for byte in commit)
        )
    print(f'board vendor/product: {message.vendor_id}/{message.product_id}')


def fetch_params(master, names) -> dict:
    """Return {name: value_or_None} for each requested parameter."""
    found = {}
    for name in names:
        master.mav.param_request_read_send(
            master.target_system,
            master.target_component,
            name.encode('ascii'),
            -1,
        )
        deadline = time.time() + 2.0
        found[name] = None
        while time.time() < deadline:
            message = master.recv_match(
                type='PARAM_VALUE', blocking=True, timeout=0.5
            )
            if message is None:
                continue
            param_id = message.param_id
            if isinstance(param_id, bytes):
                param_id = param_id.decode('ascii')
            if param_id.strip('\x00') == name:
                found[name] = message.param_value
                break
    return found


def main() -> int:
    """Probe the autopilot and print a DDS-capability verdict."""
    endpoint = sys.argv[1] if len(sys.argv) > 1 else autodetect()
    master = connect(endpoint)
    report_version(master)

    print('\n--- DDS parameters ---')
    dds = fetch_params(master, DDS_PARAMS)
    for name, value in dds.items():
        print(f'{name}: {"ABSENT" if value is None else value}')

    print('\n--- serial protocols ---')
    serial = fetch_params(master, SERIAL_PROTOCOL_PARAMS)
    dds_ports = []
    for name, value in serial.items():
        if value is None:
            continue
        marker = ''
        if int(value) == SERIAL_PROTOCOL_DDS_XRCE:
            marker = '  <== DDS/XRCE'
            dds_ports.append(name)
        print(f'{name}: {int(value)}{marker}')

    print('\n--- verdict ---')
    if dds['DDS_ENABLE'] is None:
        print(
            'DDS_ENABLE is ABSENT: this firmware was built WITHOUT AP_DDS.\n'
            'The /ap/* DDS interface is not available on this board as '
            'flashed. Either flash a build configured with --enable-dds, or '
            'use the MAVROS path.'
        )
    elif int(dds['DDS_ENABLE']) == 0:
        print(
            'AP_DDS is COMPILED IN but DDS_ENABLE is 0 (disabled).\n'
            'This is a parameter change, not a reflash.'
        )
    else:
        print('AP_DDS is compiled in and DDS_ENABLE is set.')
        if dds_ports:
            ports = ', '.join(dds_ports)
            print(f'DDS serial transport configured on: {ports}')
        else:
            print(
                'No serial port is set to protocol 45 (DDS/XRCE). '
                'If using serial transport rather than UDP, one must be set.'
            )

    print(
        '\nNothing was armed, no mode was changed, and no parameter was '
        'written.'
    )
    return 0


if __name__ == '__main__':
    sys.exit(main())
