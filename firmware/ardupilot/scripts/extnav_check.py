#!/usr/bin/env python3
"""
Check whether the DDS link can carry external odometry well enough to aid.

GPS-denied operation was demonstrated on SITL, where DDS runs over UDP with
bandwidth to spare. On hardware the link is a serial port that was already
measured as saturated in the outbound direction: /ap/clock and /ap/status
arrive at 0 Hz while about 64% of the nominal publishing rate is discarded.

Transforms on /ap/tf travel the other way, companion computer to autopilot,
and nothing has measured that direction. If it is also constrained, samples
will miss the EKF's 20 ms spacing requirement or stall for the five seconds
that ends aiding, and the indoor plan fails on hardware while continuing to
pass in simulation.

This publishes correctly stamped odometry and reports whether the autopilot
announces `EKF3 IMU0 is using external nav data`, which is the point aiding
actually begins. It does not arm, change mode, or write any parameter.

Prerequisites, which this checks and reports rather than setting:

    EK3_SRC1_POSXY = 6      EK3_SRC1_VELZ  = 0      VISO_TYPE = 1
    EK3_SRC1_YAW   = 6      EK3_SRC1_VELXY = 6

Usage::

    ./extnav_check.py                       # 60 s, default endpoints
    ./extnav_check.py --seconds 120
    ./extnav_check.py --mavlink /dev/ttyACM0
"""

import argparse
import sys
import threading
import time

try:
    from pymavlink import mavutil
except ImportError:
    sys.exit(
        'pymavlink is not installed.\n'
        '  python3 -m pip install --user --break-system-packages pymavlink'
    )

try:
    from builtin_interfaces.msg import Time as TimeMsg
    from geometry_msgs.msg import TransformStamped
    import rclpy
    from rclpy.node import Node
    from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
    from tf2_msgs.msg import TFMessage
except ImportError as exc:
    sys.exit(f'ROS 2 environment is not sourced: {exc}')


FEED_HZ = 20.0
STAMP_LAG_SEC = 0.05
MIN_STAMP_GAP_MS = 20
AIDING_MARKER = 'using external nav'
STOPPED_MARKER = 'stopped aiding'

REQUIRED_PARAMS = {
    'EK3_SRC1_POSXY': 6.0,
    'EK3_SRC1_VELXY': 6.0,
    'EK3_SRC1_YAW': 6.0,
    'EK3_SRC1_VELZ': 0.0,
    'VISO_TYPE': 1.0,
}


def parse_args():
    """Return parsed command-line options."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mavlink', default='/dev/ttyACM0',
                        help='MAVLink endpoint, for status text and origin')
    parser.add_argument('--baud', type=int, default=115200)
    parser.add_argument('--seconds', type=float, default=60.0,
                        help='how long to feed odometry')
    return parser.parse_args()


class Autopilot:
    """
    MAVLink side channel. Refuses to run blind.

    Exactly one thread reads the connection. pymavlink is not thread safe,
    and an earlier version had a status-text reader and a parameter reader
    both calling recv_match on the same link: the reader thread consumed the
    PARAM_VALUE replies, so every parameter read returned None and the check
    reported correctly-set parameters as missing. Reading from two places
    also produced spurious "device reports readiness to read but returned no
    data" failures. The reader now dispatches to both consumers instead.
    """

    def __init__(self, endpoint, baud):
        """Open the link and start the single reader."""
        self.texts = []
        self.params = {}
        self._lock = threading.Lock()
        if endpoint.startswith(('udp:', 'tcp:')):
            self.conn = mavutil.mavlink_connection(endpoint, source_system=231)
        else:
            self.conn = mavutil.mavlink_connection(
                endpoint, baud=baud, source_system=231)
        if self.conn.wait_heartbeat(timeout=20) is None:
            sys.exit(
                f'no heartbeat on {endpoint}. Without status text this cannot '
                'tell "aiding never started" from "nothing was listening", so '
                'it will not guess.'
            )
        threading.Thread(target=self._pump, daemon=True).start()

    def _pump(self):
        while True:
            msg = self.conn.recv_match(
                type=['STATUSTEXT', 'PARAM_VALUE'], blocking=True, timeout=0.5)
            if msg is None:
                continue
            if msg.get_type() == 'STATUSTEXT':
                with self._lock:
                    self.texts.append((time.time(), msg.text))
                print(f'    AP: {msg.text}', flush=True)
            else:
                name = msg.param_id
                if isinstance(name, bytes):
                    name = name.decode('ascii', 'replace')
                with self._lock:
                    self.params[name.strip('\x00')] = msg.param_value

    def since(self, when):
        """Return status text received at or after a given time."""
        with self._lock:
            return [text for stamp, text in self.texts if stamp >= when]

    def get_param(self, name, timeout=4.0):
        """Request one parameter and wait for the reader to deliver it."""
        with self._lock:
            self.params.pop(name, None)
        deadline = time.time() + timeout
        while time.time() < deadline:
            self.conn.mav.param_request_read_send(
                self.conn.target_system, self.conn.target_component,
                name.encode(), -1)
            waited = time.time() + 1.0
            while time.time() < waited:
                with self._lock:
                    if name in self.params:
                        return self.params[name]
                time.sleep(0.02)
        return None

    def set_origin(self):
        """Give the EKF an origin. Reads nothing back; harmless if repeated."""
        self.conn.mav.set_gps_global_origin_send(
            self.conn.target_system,
            int(-35.363262 * 1e7), int(149.165237 * 1e7), int(584.0 * 1000))


class Feeder(Node):
    """Publish odom to base_link stamped in the autopilot's own time base."""

    def __init__(self):
        """Set up the time subscription and the transform publisher."""
        super().__init__('extnav_check')
        best_effort = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE, depth=1)
        reliable = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE, depth=10)
        self.ap_time = None
        self.ap_time_local = None
        self.time_msgs = 0
        # /ap/time, not /ap/clock: same time base, but /ap/clock was measured
        # at 0 Hz over the serial transport.
        self.create_subscription(TimeMsg, '/ap/time', self._on_time, reliable)
        self.tf_pub = self.create_publisher(TFMessage, '/ap/tf', best_effort)
        self.last_stamp_ms = -1
        self.sent = 0
        self.skipped = 0

    def _on_time(self, msg):
        self.ap_time = msg.sec + msg.nanosec * 1e-9
        self.ap_time_local = time.time()
        self.time_msgs += 1

    def ap_now(self):
        """Return the autopilot's current time, extrapolated."""
        if self.ap_time is None:
            return None
        return self.ap_time + (time.time() - self.ap_time_local)

    def publish(self, x):
        """Publish one transform, never emitting a stamp that does not move."""
        now = self.ap_now()
        if now is None:
            return
        stamp = now - STAMP_LAG_SEC
        stamp_ms = int(stamp * 1000)
        if stamp_ms - self.last_stamp_ms < MIN_STAMP_GAP_MS:
            self.skipped += 1
            return
        self.last_stamp_ms = stamp_ms

        transform = TransformStamped()
        transform.header.stamp.sec = int(stamp)
        transform.header.stamp.nanosec = int((stamp - int(stamp)) * 1e9)
        # Compared with strcmp, so a namespace prefix is silently ignored.
        transform.header.frame_id = 'odom'
        transform.child_frame_id = 'base_link'
        transform.transform.translation.x = x
        transform.transform.rotation.w = 1.0
        self.tf_pub.publish(TFMessage(transforms=[transform]))
        self.sent += 1

    def feed(self, seconds, autopilot):
        """Feed odometry, re-sending the origin early, and report progress."""
        start = time.time()
        end = start + seconds
        next_tf = 0.0
        next_note = start + 10.0
        while time.time() < end:
            rclpy.spin_once(self, timeout_sec=0.005)
            now = time.time()
            if now >= next_tf:
                # A slow, smooth, monotonic track. Never jump: the DDS path
                # hardcodes reset_counter to 0, so a discontinuity cannot be
                # announced and simply looks impossible.
                self.publish(0.05 * (now - start))
                next_tf = now + 1.0 / FEED_HZ
            if now - start < 3.0 and int((now - start) * 2) % 2 == 0:
                autopilot.set_origin()
            if now >= next_note:
                print(f'  {now - start:.0f}s: sent {self.sent}, '
                      f'{self.time_msgs} /ap/time messages')
                next_note = now + 10.0


def main():
    """Feed odometry and report whether the EKF starts using it."""
    args = parse_args()
    rclpy.init()
    node = Feeder()

    print(f'connecting to {args.mavlink}')
    autopilot = Autopilot(args.mavlink, args.baud)

    print('\n--- required parameters ---')
    wrong = []
    for name, expected in REQUIRED_PARAMS.items():
        value = autopilot.get_param(name)
        ok = value is not None and abs(value - expected) < 1e-6
        print(f'  {name}: {value} (want {expected}) {"ok" if ok else "WRONG"}')
        if not ok:
            wrong.append(name)
    if wrong:
        print(f'\n  {len(wrong)} parameter(s) not set for external nav.')
        print('  Set them and reboot before reading anything below as a '
              'transport result.')

    # VISO_TYPE is @RebootRequired. AP_VisualOdom is initialised once at boot,
    # so setting it and not rebooting leaves the driver null and every
    # transform is discarded without a word. A run that reports the parameter
    # as correct can still be measuring a vehicle that cannot receive.
    print('\n  Note: VISO_TYPE takes effect only after a reboot. If it was')
    print('  just changed, reboot before trusting a "no aiding" result.')

    print('\nwaiting for /ap/time ...')
    deadline = time.time() + 20
    while time.time() < deadline and node.ap_time is None:
        rclpy.spin_once(node, timeout_sec=0.1)
    if node.ap_time is None:
        print('FAIL: no /ap/time. The DDS link is not delivering.')
        return 1
    print(f'  autopilot time base {node.ap_time:.1f}s, '
          f'wall clock {time.time():.0f}')

    print(f'\n--- feeding /ap/tf for {args.seconds:.0f}s ---')
    started = time.time()
    node.feed(args.seconds, autopilot)

    texts = autopilot.since(started)
    aiding = [t for t in texts if AIDING_MARKER in t.lower()]
    stopped = [t for t in texts if STOPPED_MARKER in t.lower()]
    expected_sends = args.seconds * FEED_HZ

    print('\n' + '=' * 60)
    print('RESULT')
    print('=' * 60)
    print(f'  transforms published : {node.sent} '
          f'(about {expected_sends:.0f} expected)')
    print(f'  skipped for spacing  : {node.skipped}')
    print(f'  /ap/time received    : {node.time_msgs}')
    print(f'  aiding started       : {"YES" if aiding else "no"}')
    print(f'  aiding stopped again : {"yes" if stopped else "no"}')

    if aiding and not stopped:
        print('\n  The serial link carries external odometry well enough to '
              'aid.')
    elif aiding and stopped:
        print('\n  Aiding started and then dropped. The link delivers, but '
              'not steadily\n  enough to hold; treat the indoor path as '
              'unproven on hardware.')
    else:
        print('\n  Aiding never started. Either the parameters above are '
              'wrong, or the\n  inbound direction of this link cannot carry '
              'the feed.')

    node.destroy_node()
    rclpy.shutdown()
    return 0


if __name__ == '__main__':
    sys.exit(main())
