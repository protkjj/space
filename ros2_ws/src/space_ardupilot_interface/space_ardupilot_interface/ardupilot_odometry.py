#!/usr/bin/env python3
"""
Publish ArduPilot's own estimate as ROS odometry and the odom transform.

Navigation needs `/odom` and an `odom` to `base_footprint` transform. On the
ArduPilot path those come from the autopilot's EKF3, which is already fusing
the IMU with whatever position source is configured, rather than from a second
filter on this side.

Running `robot_localization` here as well would be a mistake, not just
redundancy. On this rover wheel odometry is sent *to* the autopilot as
external navigation, so its estimate already contains that information;
fusing the result again alongside the same wheel data would count it twice.
The fused covariance would shrink while the true error stayed where it was,
and the vehicle would report rising confidence exactly as it drifted. That
failure is silent, which is why the authority is kept singular here:

    encoders -> extnav_publisher -> /ap/tf -> ArduPilot EKF3
                                                  |
                                                  v
                                    this node -> /odom + TF -> Nav2

A chain, with no path back. Milestone A asks for one authoritative publisher
per transform, and on this path that publisher is ArduPilot.

Two details about the frames:

* ArduPilot reports position in `base_link`, and the URDF fixes
  `base_footprint` to `base_link` with a translation and no rotation. The
  attitude therefore belongs on this transform, which also keeps the roll and
  pitch the terrain work needs.
* The reported altitude is above sea level, not above the odom origin. The
  first sample is taken as that origin so the frame starts at zero, which is
  what `odom` means. Orientation is left absolute, so headings stay meaningful
  against east and north rather than against wherever the rover happened to
  be pointing at startup.
"""

import math
from typing import Optional

from geometry_msgs.msg import PoseStamped, TransformStamped, TwistStamped
from nav_msgs.msg import Odometry
import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from tf2_msgs.msg import TFMessage


NANOSECONDS_PER_SECOND = 1_000_000_000


def _positive(name: str, value: float) -> float:
    """Validate a finite, strictly positive parameter."""
    if not math.isfinite(value) or value <= 0.0:
        raise ValueError(f'{name} must be finite and greater than zero')
    return value


class ArduPilotOdometry(Node):
    """Republish the autopilot's estimate as `/odom` and the odom transform."""

    def __init__(self):
        """Declare parameters, wire the topics, and start the publish timer."""
        super().__init__('space_ardupilot_odometry')

        self.declare_parameter('pose_topic', '/ap/pose/filtered')
        self.declare_parameter('twist_topic', '/ap/twist/filtered')
        self.declare_parameter('odom_topic', '/odom')
        self.declare_parameter('tf_topic', '/tf')
        self.declare_parameter('odom_frame', 'odom')
        self.declare_parameter('base_frame', 'base_footprint')
        self.declare_parameter('publish_rate_hz', 30.0)
        self.declare_parameter('pose_timeout_sec', 1.0)
        self.declare_parameter('publish_tf', True)

        self._odom_frame = str(self.get_parameter('odom_frame').value)
        self._base_frame = str(self.get_parameter('base_frame').value)
        self._publish_tf = bool(self.get_parameter('publish_tf').value)

        publish_rate_hz = _positive(
            'publish_rate_hz',
            float(self.get_parameter('publish_rate_hz').value))
        self._pose_timeout_ns = int(
            _positive('pose_timeout_sec',
                      float(self.get_parameter('pose_timeout_sec').value))
            * NANOSECONDS_PER_SECOND)

        # /ap/pose/filtered and /ap/twist/filtered are BEST_EFFORT on the
        # builds measured; a RELIABLE subscription would not match.
        autopilot_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE, depth=1)

        self._origin: Optional[tuple] = None
        self._pose: Optional[PoseStamped] = None
        self._twist: Optional[TwistStamped] = None
        self._pose_time_ns: Optional[int] = None
        self._last_warning = ''
        self._published = 0

        self.create_subscription(
            PoseStamped, str(self.get_parameter('pose_topic').value),
            self._on_pose, autopilot_qos)
        self.create_subscription(
            TwistStamped, str(self.get_parameter('twist_topic').value),
            self._on_twist, autopilot_qos)

        self._odom_publisher = self.create_publisher(
            Odometry, str(self.get_parameter('odom_topic').value), 10)
        self._tf_publisher = self.create_publisher(
            TFMessage, str(self.get_parameter('tf_topic').value), 10)

        self.create_timer(1.0 / publish_rate_hz, self._on_publish_timer)

        self.get_logger().info(
            f'ArduPilot odometry ready at {publish_rate_hz:.1f} Hz: '
            f'{self._odom_frame} -> {self._base_frame}')
        if self._publish_tf:
            self.get_logger().warn(
                f'This node is the authority for {self._odom_frame} -> '
                f'{self._base_frame}. Do not run robot_localization or any '
                'other publisher of that transform alongside it.')

    def _now_ns(self) -> int:
        return self.get_clock().now().nanoseconds

    def _on_pose(self, message: PoseStamped) -> None:
        """Record the latest pose, taking the first as the odom origin."""
        if self._origin is None:
            position = message.pose.position
            # Reported altitude is above sea level; odom starts at zero.
            self._origin = (position.x, position.y, position.z)
            self.get_logger().info(
                f'odom origin set at ({position.x:.2f}, {position.y:.2f}, '
                f'{position.z:.2f}) in the autopilot frame')
        self._pose = message
        self._pose_time_ns = self._now_ns()

    def _on_twist(self, message: TwistStamped) -> None:
        """Record the latest velocity."""
        self._twist = message

    def _warn_once(self, text: str) -> None:
        """Log a warning only when it changes."""
        if text != self._last_warning:
            self._last_warning = text
            self.get_logger().warn(text)

    def _on_publish_timer(self) -> None:
        """Publish odometry and the transform from the latest estimate."""
        if self._pose is None or self._origin is None:
            self._warn_once('waiting for the autopilot pose')
            return

        now_ns = self._now_ns()
        if now_ns - self._pose_time_ns > self._pose_timeout_ns:
            # Republishing a stale pose would assert the rover is where it was
            # rather than admit the estimate has stopped arriving. Navigation
            # planning against a frozen pose is worse than planning against
            # none, because nothing downstream can tell.
            self._warn_once(
                'autopilot pose is stale; stopping odometry and TF')
            return
        self._last_warning = ''

        position = self._pose.pose.position
        orientation = self._pose.pose.orientation
        stamp = self.get_clock().now().to_msg()

        x = position.x - self._origin[0]
        y = position.y - self._origin[1]
        z = position.z - self._origin[2]

        odometry = Odometry()
        odometry.header.stamp = stamp
        odometry.header.frame_id = self._odom_frame
        odometry.child_frame_id = self._base_frame
        odometry.pose.pose.position.x = x
        odometry.pose.pose.position.y = y
        odometry.pose.pose.position.z = z
        odometry.pose.pose.orientation = orientation
        if self._twist is not None:
            odometry.twist.twist = self._twist.twist
        self._odom_publisher.publish(odometry)

        if not self._publish_tf:
            return

        transform = TransformStamped()
        transform.header.stamp = stamp
        transform.header.frame_id = self._odom_frame
        transform.child_frame_id = self._base_frame
        transform.transform.translation.x = x
        transform.transform.translation.y = y
        transform.transform.translation.z = z
        transform.transform.rotation = orientation
        self._tf_publisher.publish(TFMessage(transforms=[transform]))
        self._published += 1


def main(args=None):
    """Run the ArduPilot odometry bridge."""
    rclpy.init(args=args)
    node = ArduPilotOdometry()
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
