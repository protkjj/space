#!/usr/bin/env python3
"""Publish one planar navigation goal from the command line."""

import argparse
import sys
import time

from geometry_msgs.msg import PoseStamped
import rclpy
from rclpy.node import Node
from rclpy.utilities import remove_ros_args

from space_navigation.navigation_math import yaw_to_quaternion


def _arguments(args):
    parser = argparse.ArgumentParser(
        description='Send a planar goal to the space rover.'
    )
    parser.add_argument('x', type=float, help='goal x coordinate in metres')
    parser.add_argument('y', type=float, help='goal y coordinate in metres')
    parser.add_argument(
        'yaw', type=float, nargs='?', default=0.0,
        help='final heading in radians (default: 0)',
    )
    parser.add_argument(
        '--frame', default='odom', help='goal frame (default: odom)'
    )
    parser.add_argument(
        '--topic', default='/goal_pose', help='goal topic'
    )
    return parser.parse_args(remove_ros_args(args=args)[1:])


def main(args=None):
    """Publish a goal after briefly waiting for the bridge subscriber."""
    raw_args = args if args is not None else sys.argv
    parsed = _arguments(raw_args)
    rclpy.init(args=raw_args)
    node = Node('space_send_goal')
    publisher = node.create_publisher(PoseStamped, parsed.topic, 10)

    deadline = time.monotonic() + 3.0
    while (
        publisher.get_subscription_count() == 0
        and time.monotonic() < deadline
    ):
        rclpy.spin_once(node, timeout_sec=0.1)

    goal = PoseStamped()
    goal.header.stamp = node.get_clock().now().to_msg()
    goal.header.frame_id = parsed.frame
    goal.pose.position.x = parsed.x
    goal.pose.position.y = parsed.y
    goal.pose.orientation.z, goal.pose.orientation.w = yaw_to_quaternion(
        parsed.yaw
    )
    publisher.publish(goal)
    node.get_logger().info(
        f'Published goal ({parsed.x:.2f}, {parsed.y:.2f}, '
        f'yaw={parsed.yaw:.2f}) in {parsed.frame}'
    )
    rclpy.spin_once(node, timeout_sec=0.2)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
