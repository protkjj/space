#!/usr/bin/env python3
"""Route rover velocity commands to the simulated or real wheel driver.

Simulation path:
  /cmd_vel_in -> this node -> /cmd_vel -> Gazebo DiffDrive

Hardware path:
  replace the final publish section with RoboClaw serial/USB commands after
  motor, encoder, and driver sizing are fixed.
"""

from enum import IntEnum

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from std_msgs.msg import UInt8


class Mode(IntEnum):
    ROVER = 0
    HOLD = 1
    EMERGENCY = 2


def _clip(value: float, limit: float) -> float:
    if limit <= 0.0:
        return value
    return max(-limit, min(limit, value))


class WheelMotorDriver(Node):
    def __init__(self):
        super().__init__('space_wheel_motor_driver')

        self.declare_parameter('input_topic', '/cmd_vel_in')
        self.declare_parameter('output_topic', '/cmd_vel')
        self.declare_parameter('mode_topic', '/space/mode')
        self.declare_parameter('max_linear_mps', 0.30)
        self.declare_parameter('max_angular_radps', 0.80)

        input_topic = self.get_parameter('input_topic').value
        output_topic = self.get_parameter('output_topic').value
        mode_topic = self.get_parameter('mode_topic').value

        self._max_linear = float(self.get_parameter('max_linear_mps').value)
        self._max_angular = float(self.get_parameter('max_angular_radps').value)
        self._mode = Mode.ROVER

        self._cmd_pub = self.create_publisher(Twist, output_topic, 10)
        self.create_subscription(Twist, input_topic, self._on_cmd_vel, 10)
        self.create_subscription(UInt8, mode_topic, self._on_mode, 10)

        self.get_logger().info(
            f'Wheel driver ready: {input_topic} -> {output_topic}, mode={self._mode.name}'
        )

    def _on_mode(self, msg: UInt8):
        try:
            new_mode = Mode(msg.data)
        except ValueError:
            self.get_logger().warn(f'Ignoring unknown mode: {msg.data}')
            return

        if new_mode != self._mode:
            self.get_logger().info(f'Mode changed: {self._mode.name} -> {new_mode.name}')
            self._mode = new_mode
            if self._mode != Mode.ROVER:
                self._cmd_pub.publish(Twist())

    def _on_cmd_vel(self, msg: Twist):
        if self._mode != Mode.ROVER:
            self._cmd_pub.publish(Twist())
            return

        limited = Twist()
        limited.linear.x = _clip(msg.linear.x, self._max_linear)
        limited.angular.z = _clip(msg.angular.z, self._max_angular)
        self._cmd_pub.publish(limited)


def main(args=None):
    rclpy.init(args=args)
    node = WheelMotorDriver()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
