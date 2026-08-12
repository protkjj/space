#!/usr/bin/env python3
"""
Drive one drivetrain side at a time to check output wiring and direction.

This uses ArduPilot's own ``MAV_CMD_DO_MOTOR_TEST``, which spins a single
motor group without arming the vehicle. With a direct PWM throttle type the
autopilot skips its RC-calibration check, so the only prerequisites are a
booted board and a safety switch that is not engaged. No arming, GPS,
compass, or position estimate is involved, which is what makes this usable
indoors on a partially assembled rover.

Motor group numbers come from ``AP_MotorsUGV::motor_test_order`` at the
pinned revision: 3 is ThrottleLeft and 4 is ThrottleRight.

**Raise the wheels off the ground before running this.** The rover is
commanded to move; it simply is not commanded to go anywhere in particular.

Usage::

    ./motor_bench_test.py                       # guided, one step at a time
    ./motor_bench_test.py --device /dev/ttyACM0
    ./motor_bench_test.py --pwm 1600 --seconds 2
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


# AP_MotorsUGV::motor_test_order at the pinned revision.
THROTTLE_LEFT = 3
THROTTLE_RIGHT = 4

# Rover/motor_test.cpp: 0=percent, 1=direct PWM, 2=pilot passthrough.
# Type 1 is used deliberately: it is the one that skips the RC-calibration
# check, and it says exactly what will be sent to the output.
THROTTLE_TYPE_PWM = 1

# Rover/motor_test.cpp MOTOR_TEST_PWM_MAX.
PWM_MAX = 2200
PWM_NEUTRAL = 1500


def parse_args():
    """Return parsed command-line options."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--device', default='/dev/ttyACM0',
                        help='MAVLink serial device (not the DDS one)')
    parser.add_argument('--baud', type=int, default=115200)
    parser.add_argument('--pwm', type=int, default=1600,
                        help='PWM to send; 1500 is neutral')
    parser.add_argument('--seconds', type=float, default=3.0,
                        help='how long each group runs')
    return parser.parse_args()


def connect(device, baud):
    """Open the link and wait for the autopilot."""
    print(f'connecting to {device}')
    conn = mavutil.mavlink_connection(device, baud=baud, source_system=243)
    if conn.wait_heartbeat(timeout=20) is None:
        sys.exit(f'no heartbeat from {device}')
    print(f'connected: system={conn.target_system}')
    return conn


def drain_text(conn, seconds):
    """Print any STATUSTEXT for a while, so refusals are quoted not guessed."""
    deadline = time.time() + seconds
    while time.time() < deadline:
        msg = conn.recv_match(type='STATUSTEXT', blocking=True, timeout=0.5)
        if msg is not None:
            print(f'    autopilot: {msg.text}')


def run_group(conn, group, label, pwm, seconds):
    """Spin one motor group and report the autopilot's response."""
    print(f'\n--- {label} (group {group}) at pwm {pwm} for {seconds:.0f}s ---')
    conn.mav.command_long_send(
        conn.target_system, conn.target_component,
        mavutil.mavlink.MAV_CMD_DO_MOTOR_TEST, 0,
        group,                # motor instance
        THROTTLE_TYPE_PWM,    # throttle type
        pwm,                  # throttle value
        seconds,              # timeout
        0, 0, 0,
    )
    ack = conn.recv_match(type='COMMAND_ACK', blocking=True, timeout=5)
    if ack is None:
        print('    no COMMAND_ACK received')
    else:
        accepted = ack.result == mavutil.mavlink.MAV_RESULT_ACCEPTED
        print(f'    result: {ack.result} '
              f'({"ACCEPTED" if accepted else "REFUSED"})')
    drain_text(conn, seconds + 1.0)


def main():
    """Walk through each side, pausing for the operator to look."""
    args = parse_args()
    if not 1000 <= args.pwm <= PWM_MAX:
        sys.exit(f'--pwm must be between 1000 and {PWM_MAX}')

    print(__doc__.split('Usage')[0].strip())
    print()
    reply = input('Are the wheels off the ground? [yes/N] ').strip().lower()
    if reply not in ('y', 'yes'):
        sys.exit('Aborted. Raise the wheels first.')

    conn = connect(args.device, args.baud)

    steps = (
        (THROTTLE_LEFT, 'LEFT side'),
        (THROTTLE_RIGHT, 'RIGHT side'),
    )
    for group, label in steps:
        input(f'\n>>> press Enter to run {label}, then watch which wheels '
              'turn and which way')
        run_group(conn, group, label, args.pwm, args.seconds)

    print('\n--- what to record ---')
    print('  Which physical wheels turned for LEFT, and for RIGHT.')
    print('  Whether each side turned forward or backward.')
    print('  If a side is reversed, correct it with SERVOn_REVERSED for that')
    print('  output rather than by swapping the function assignment.')
    print('  If the sides are swapped, the ThrottleLeft/ThrottleRight outputs')
    print('  do not match the physical wiring.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
