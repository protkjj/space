#!/usr/bin/env python3
"""
Read wheel encoders from the RoboClaws and publish the counts.

The encoders are wired to the motor controllers rather than to the Pixhawk, so
this is the only way to obtain wheel odometry. The counts published here feed
`extnav_publisher`, which turns them into the transform ArduPilot navigates
from.

**This node only reads.** It never sends a motion or configuration command,
and the protocol module it uses cannot frame one. ArduPilot owns motion
through the RC/PWM link; a second writer would be two controllers driving the
same motors with no arbitration. It is also deliberately off the command path,
so a controller that stops answering degrades the estimate and never the
ability to stop.

Each side of a skid-steer rover has two motors on one controller, and their
counts are averaged. Averaging is not just noise reduction: on a skid vehicle
the two wheels on a side are mechanically coupled through the ground, so a
large disagreement between them means one is slipping or an encoder has
failed, and that disagreement is published as a diagnostic rather than hidden.
"""

import math
from typing import Optional

import rclpy
from rclpy.node import Node
from space_ardupilot_interface.roboclaw_protocol import (
    CMD_GET_ENCODERS,
    DEFAULT_ADDRESS,
    expected_reply_length,
    parse_encoders,
    read_request,
)
from std_msgs.msg import Float32MultiArray

try:
    import serial
except ImportError:  # pragma: no cover - depends on the host
    serial = None


NANOSECONDS_PER_SECOND = 1_000_000_000


def _positive(name: str, value: float) -> float:
    """Validate a finite, strictly positive parameter."""
    if not math.isfinite(value) or value <= 0.0:
        raise ValueError(f'{name} must be finite and greater than zero')
    return value


class ControllerLink:
    """One read-only serial link to a RoboClaw."""

    def __init__(self, device: str, baud: int, address: int, timeout: float):
        """Open the port. Raises if the port cannot be opened."""
        if serial is None:
            raise ImportError(
                'pyserial is not installed; install python3-serial'
            )
        self.device = device
        self.address = address
        self.port = serial.Serial(device, baud, timeout=timeout)
        self.bad_replies = 0
        self.reads = 0

    def read_encoders(self) -> Optional[tuple]:
        """
        Return (encoder1, encoder2), or None if the reply did not verify.

        A reply that fails its CRC is discarded rather than repaired. A
        misframed count would otherwise produce a plausible pose that nothing
        downstream could tell was wrong.
        """
        request = read_request(CMD_GET_ENCODERS, self.address)
        try:
            self.port.reset_input_buffer()
            self.port.write(request)
            reply = self.port.read(expected_reply_length(CMD_GET_ENCODERS))
        except Exception:
            self.bad_replies += 1
            return None

        counts = parse_encoders(request, reply)
        self.reads += 1
        if counts is None:
            self.bad_replies += 1
        return counts

    def close(self):
        """Close the port if it is open."""
        try:
            self.port.close()
        except Exception:
            pass


class RoboClawReader(Node):
    """Poll both controllers and publish averaged per-side encoder counts."""

    def __init__(self):
        """Declare parameters, open the links, and start polling."""
        super().__init__('space_roboclaw_reader')

        self.declare_parameter('left_device', '/dev/ttyACM0')
        self.declare_parameter('right_device', '/dev/ttyACM1')
        self.declare_parameter('baud', 115200)
        self.declare_parameter('address', DEFAULT_ADDRESS)
        self.declare_parameter('serial_timeout_sec', 0.05)
        self.declare_parameter('poll_rate_hz', 50.0)
        self.declare_parameter('counts_topic', '/wheel_counts')
        self.declare_parameter('average_both_motors', True)
        self.declare_parameter('disagreement_warn_counts', 2000.0)

        baud = int(self.get_parameter('baud').value)
        address = int(self.get_parameter('address').value)
        timeout = _positive(
            'serial_timeout_sec',
            float(self.get_parameter('serial_timeout_sec').value))
        poll_rate_hz = _positive(
            'poll_rate_hz',
            float(self.get_parameter('poll_rate_hz').value))

        self._average = bool(
            self.get_parameter('average_both_motors').value)
        self._disagreement_limit = float(
            self.get_parameter('disagreement_warn_counts').value)

        left_device = str(self.get_parameter('left_device').value)
        right_device = str(self.get_parameter('right_device').value)
        if left_device == right_device:
            raise ValueError(
                'left_device and right_device must differ; each controller '
                'is on its own USB device'
            )

        self._left = ControllerLink(left_device, baud, address, timeout)
        self._right = ControllerLink(right_device, baud, address, timeout)

        self._publisher = self.create_publisher(
            Float32MultiArray,
            str(self.get_parameter('counts_topic').value),
            10,
        )
        self._last_warning = ''
        self.create_timer(1.0 / poll_rate_hz, self._on_poll)
        self.create_timer(5.0, self._on_report)

        self.get_logger().info(
            f'RoboClaw reader ready at {poll_rate_hz:.0f} Hz: '
            f'left {left_device}, right {right_device}, '
            f'address 0x{address:02x}'
        )
        self.get_logger().info(
            'Read-only: this node never commands a motor.'
        )

    def _warn_once(self, text: str) -> None:
        """Log a warning only when it changes."""
        if text != self._last_warning:
            self._last_warning = text
            self.get_logger().warn(text)

    def _side_count(self, counts, label) -> float:
        """Reduce one controller's two encoders to a single side count."""
        first, second = counts
        if not self._average:
            return float(first)
        disagreement = abs(first - second)
        if disagreement > self._disagreement_limit:
            # Two wheels on one side are coupled through the ground, so a
            # large disagreement is slip or a failed encoder, not motion.
            self._warn_once(
                f'{label} encoders disagree by {disagreement} counts; '
                'one wheel may be slipping or an encoder may have failed'
            )
        return 0.5 * (first + second)

    def _on_poll(self) -> None:
        """Read both controllers and publish one counts message."""
        left = self._left.read_encoders()
        right = self._right.read_encoders()

        if left is None or right is None:
            # Publishing a partial or stale reading would be a claim about
            # where the rover is. Staying quiet lets the consumer time out.
            missing = 'left' if left is None else 'right'
            if left is None and right is None:
                missing = 'both controllers'
            self._warn_once(f'no verified encoder reply from {missing}')
            return
        self._last_warning = ''

        message = Float32MultiArray()
        message.data = [
            self._side_count(left, 'left'),
            self._side_count(right, 'right'),
        ]
        self._publisher.publish(message)

    def _on_report(self) -> None:
        """Report link quality, so a marginal cable is visible."""
        for link, label in ((self._left, 'left'), (self._right, 'right')):
            if link.reads == 0:
                continue
            bad_fraction = link.bad_replies / max(link.reads, 1)
            if bad_fraction > 0.05:
                self.get_logger().warn(
                    f'{label} controller: {link.bad_replies} of {link.reads} '
                    f'replies failed verification ({bad_fraction:.0%})'
                )

    def destroy_node(self):
        """Close both links on shutdown."""
        self._left.close()
        self._right.close()
        return super().destroy_node()


def main(args=None):
    """Run the RoboClaw encoder reader."""
    rclpy.init(args=args)
    node = RoboClawReader()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            node.destroy_node()
            rclpy.try_shutdown()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()
