#!/usr/bin/env python3
"""Minimal PX4 bridge skeleton.

This is intentionally small. The rover can run in simulation without it, and
hardware work should update this once the Pixhawk firmware path is confirmed.
"""

import math

from geometry_msgs.msg import Twist
from px4_msgs.msg import OffboardControlMode, TrajectorySetpoint, VehicleCommand
import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import UInt8


PX4_QOS = QoSProfile(
    reliability=ReliabilityPolicy.BEST_EFFORT,
    durability=DurabilityPolicy.TRANSIENT_LOCAL,
    history=HistoryPolicy.KEEP_LAST,
    depth=1,
)


class PX4Bridge(Node):
    MODE_ROVER = 0
    MODE_HOLD = 1

    def __init__(self):
        super().__init__('space_px4_bridge')

        self._pub_cmd = self.create_publisher(
            VehicleCommand, '/fmu/in/vehicle_command', PX4_QOS
        )
        self._pub_offboard = self.create_publisher(
            OffboardControlMode, '/fmu/in/offboard_control_mode', PX4_QOS
        )
        self._pub_setpoint = self.create_publisher(
            TrajectorySetpoint, '/fmu/in/trajectory_setpoint', PX4_QOS
        )

        self.create_subscription(UInt8, '/space/mode', self._on_mode, 10)
        self.create_subscription(Twist, '/cmd_vel', self._on_cmd_vel, 10)

        self._mode = self.MODE_ROVER
        self.create_timer(0.1, self._publish_offboard_heartbeat)
        self.get_logger().info('PX4 bridge skeleton started')

    def _now_us(self) -> int:
        return int(self.get_clock().now().nanoseconds / 1000)

    def _on_mode(self, msg: UInt8):
        self._mode = msg.data

    def _on_cmd_vel(self, msg: Twist):
        if self._mode != self.MODE_ROVER:
            return

        setpoint = TrajectorySetpoint()
        setpoint.timestamp = self._now_us()
        setpoint.velocity[0] = float(msg.linear.x)
        setpoint.velocity[1] = 0.0
        setpoint.velocity[2] = math.nan
        setpoint.yawspeed = float(msg.angular.z)
        setpoint.position = [math.nan, math.nan, math.nan]
        setpoint.yaw = math.nan
        self._pub_setpoint.publish(setpoint)

    def _publish_offboard_heartbeat(self):
        if self._mode != self.MODE_ROVER:
            return

        msg = OffboardControlMode()
        msg.timestamp = self._now_us()
        msg.position = False
        msg.velocity = True
        msg.acceleration = False
        msg.attitude = False
        msg.body_rate = False
        self._pub_offboard.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = PX4Bridge()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
