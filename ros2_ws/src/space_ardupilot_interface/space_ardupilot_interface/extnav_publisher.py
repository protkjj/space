#!/usr/bin/env python3
"""
Publish wheel odometry to ArduPilot as external navigation.

ArduPilot's EKF will accept an external position estimate on ``/ap/tf`` and
navigate from it with no GPS, which is what the indoor arena needs. Getting it
accepted turned out to depend on several things that fail silently when they
are wrong, so they are enforced here rather than left to the caller:

* **Stamp in ArduPilot's time base.** It publishes that on ``/ap/time``. A ROS
  wall-clock stamp is a different epoch, lands outside the fusion horizon, and
  is discarded without a message. ``/ap/clock`` carries the same time but was
  measured at 0 Hz over the serial link, so it is not usable as the source.
* **Advance the stamp by at least 20 ms.** Closer samples are dropped by the
  EKF, judged on the sender's stamp rather than on arrival.
* **Never stop.** Aiding ends after roughly five seconds without a fused
  sample, and restarting it is not automatic.
* **Never jump.** The DDS path hardcodes the reset counter to zero, so a
  discontinuity cannot be announced as intentional and simply looks like
  impossible movement. This node refuses to publish a pose that moved further
  than the drivetrain could have.

Counts arrive on a topic rather than being read from the motor controller
here. The controller's reply layout has not yet been confirmed against a real
unit, and a parser written from a manual alone would be a guess in the one
place where a mistake is invisible: wrong counts produce a plausible pose that
is quietly wrong.
"""

import math

from builtin_interfaces.msg import Time as TimeMsg
from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import Odometry
import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from space_ardupilot_interface.wheel_odometry import (
    slip_ratio,
    WheelOdometry,
)
from std_msgs.msg import Float32MultiArray
from tf2_msgs.msg import TFMessage


NANOSECONDS_PER_SECOND = 1_000_000_000


def _positive(name: str, value: float) -> float:
    """Validate a finite, strictly positive parameter."""
    if not math.isfinite(value) or value <= 0.0:
        raise ValueError(f'{name} must be finite and greater than zero')
    return value


class ExternalNavPublisher(Node):
    """Integrate wheel counts and publish them where ArduPilot will use them."""

    def __init__(self):
        """Declare parameters, wire the topics, and start the publish timer."""
        super().__init__('space_extnav_publisher')

        self.declare_parameter('counts_topic', '/wheel_counts')
        self.declare_parameter('time_topic', '/ap/time')
        self.declare_parameter('tf_topic', '/ap/tf')
        self.declare_parameter('odom_topic', '/wheel_odom')
        self.declare_parameter('odom_frame', 'odom')
        self.declare_parameter('base_frame', 'base_link')

        # Measured from the built rover; see space_description.
        self.declare_parameter('wheel_radius_m', 0.060)
        self.declare_parameter('track_width_m', 0.225)
        self.declare_parameter('counts_per_revolution', 6400.0)
        self.declare_parameter('max_wheel_speed_mps', 1.0)

        self.declare_parameter('publish_rate_hz', 20.0)
        self.declare_parameter('stamp_lag_sec', 0.05)
        self.declare_parameter('min_stamp_gap_sec', 0.020)
        self.declare_parameter('counts_timeout_sec', 0.5)

        odom_frame = str(self.get_parameter('odom_frame').value)
        base_frame = str(self.get_parameter('base_frame').value)
        # AP_DDS compares these with strcmp, so a namespace prefix is ignored
        # in silence. Refuse the configuration rather than publish transforms
        # that will never be read.
        if odom_frame != 'odom' or base_frame != 'base_link':
            raise ValueError(
                'ArduPilot only consumes transforms named exactly '
                f'odom -> base_link, not {odom_frame} -> {base_frame}'
            )
        self._odom_frame = odom_frame
        self._base_frame = base_frame

        self._odometry = WheelOdometry(
            wheel_radius_m=float(
                self.get_parameter('wheel_radius_m').value),
            track_width_m=float(
                self.get_parameter('track_width_m').value),
            counts_per_revolution=float(
                self.get_parameter('counts_per_revolution').value),
            max_wheel_speed_mps=float(
                self.get_parameter('max_wheel_speed_mps').value),
        )

        publish_rate_hz = _positive(
            'publish_rate_hz',
            float(self.get_parameter('publish_rate_hz').value),
        )
        self._stamp_lag_sec = float(self.get_parameter('stamp_lag_sec').value)
        self._min_stamp_gap_sec = _positive(
            'min_stamp_gap_sec',
            float(self.get_parameter('min_stamp_gap_sec').value),
        )
        self._counts_timeout_ns = int(
            _positive(
                'counts_timeout_sec',
                float(self.get_parameter('counts_timeout_sec').value),
            ) * NANOSECONDS_PER_SECOND
        )

        best_effort = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE, depth=1)
        reliable = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE, depth=10)

        self._ap_time = None
        self._ap_time_local_ns = None
        self._last_stamp_ns = None
        self._last_counts_ns = None
        self._latest_sample = None
        self._published = 0
        self._skipped_spacing = 0
        self._last_warning = ''

        self.create_subscription(
            TimeMsg, str(self.get_parameter('time_topic').value),
            self._on_ap_time, reliable)
        self.create_subscription(
            Float32MultiArray, str(self.get_parameter('counts_topic').value),
            self._on_counts, 10)
        self._tf_publisher = self.create_publisher(
            TFMessage, str(self.get_parameter('tf_topic').value), best_effort)
        self._odom_publisher = self.create_publisher(
            Odometry, str(self.get_parameter('odom_topic').value), 10)

        self.create_timer(1.0 / publish_rate_hz, self._on_publish_timer)

        self.get_logger().info(
            f'External nav publisher ready at {publish_rate_hz:.1f} Hz: '
            f'{self._odom_frame} -> {self._base_frame}'
        )
        self.get_logger().info(
            f'wheel radius {self._odometry.wheel_radius_m} m, track '
            f'{self._odometry.track_width_m} m, '
            f'{self._odometry.metres_per_count * 1e6:.2f} um per count'
        )

    def _now_ns(self) -> int:
        return self.get_clock().now().nanoseconds

    def _on_ap_time(self, message) -> None:
        """Track ArduPilot's clock so transforms can be stamped in it."""
        self._ap_time = message.sec + message.nanosec * 1e-9
        self._ap_time_local_ns = self._now_ns()

    def _autopilot_now(self):
        """Return the autopilot's current time, extrapolated locally."""
        if self._ap_time is None:
            return None
        elapsed = (self._now_ns() - self._ap_time_local_ns)
        return self._ap_time + elapsed / NANOSECONDS_PER_SECOND

    def _on_counts(self, message) -> None:
        """Integrate one encoder reading."""
        if len(message.data) < 2:
            self._warn_once(
                'counts message needs at least [left, right]')
            return
        now_ns = self._now_ns()
        self._last_counts_ns = now_ns
        sample = self._odometry.update(
            int(message.data[0]), int(message.data[1]), now_ns)
        if sample is not None:
            self._latest_sample = sample

    def _warn_once(self, text: str) -> None:
        """Log a warning only when it changes, so it stays readable."""
        if text != self._last_warning:
            self._last_warning = text
            self.get_logger().warn(text)

    def _on_publish_timer(self) -> None:
        """Publish the current pose, if it is safe and useful to do so."""
        if self._latest_sample is None:
            self._warn_once('waiting for wheel counts')
            return

        now_ns = self._now_ns()
        if (self._last_counts_ns is not None
                and now_ns - self._last_counts_ns > self._counts_timeout_ns):
            # Republishing a frozen pose would tell the EKF the rover is
            # standing still, which is a claim, not an absence of one.
            self._warn_once(
                'wheel counts are stale; stopping the external nav feed'
            )
            return

        autopilot_time = self._autopilot_now()
        if autopilot_time is None:
            self._warn_once(
                'waiting for /ap/time; transforms stamped from any other '
                'clock are discarded by the EKF'
            )
            return

        stamp = autopilot_time - self._stamp_lag_sec
        stamp_ns = int(stamp * NANOSECONDS_PER_SECOND)
        if (self._last_stamp_ns is not None
                and stamp_ns - self._last_stamp_ns
                < self._min_stamp_gap_sec * NANOSECONDS_PER_SECOND):
            self._skipped_spacing += 1
            return
        self._last_stamp_ns = stamp_ns
        self._last_warning = ''

        sample = self._latest_sample
        transform = TransformStamped()
        transform.header.stamp.sec = int(stamp)
        transform.header.stamp.nanosec = int(
            (stamp - int(stamp)) * NANOSECONDS_PER_SECOND)
        transform.header.frame_id = self._odom_frame
        transform.child_frame_id = self._base_frame
        transform.transform.translation.x = sample.x
        transform.transform.translation.y = sample.y
        transform.transform.rotation.z = math.sin(sample.yaw * 0.5)
        transform.transform.rotation.w = math.cos(sample.yaw * 0.5)
        self._tf_publisher.publish(TFMessage(transforms=[transform]))
        self._published += 1

        odometry = Odometry()
        odometry.header.stamp = self.get_clock().now().to_msg()
        odometry.header.frame_id = self._odom_frame
        odometry.child_frame_id = self._base_frame
        odometry.pose.pose.position.x = sample.x
        odometry.pose.pose.position.y = sample.y
        odometry.pose.pose.orientation.z = math.sin(sample.yaw * 0.5)
        odometry.pose.pose.orientation.w = math.cos(sample.yaw * 0.5)
        odometry.twist.twist.linear.x = sample.linear_velocity
        odometry.twist.twist.angular.z = sample.angular_velocity
        self._odom_publisher.publish(odometry)


def main(args=None):
    """Run the external navigation publisher."""
    rclpy.init(args=args)
    node = ExternalNavPublisher()
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


__all__ = ['ExternalNavPublisher', 'main', 'slip_ratio']
