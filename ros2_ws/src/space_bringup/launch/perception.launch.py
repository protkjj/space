#!/usr/bin/env python3
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='space_perception',
            executable='depth_overlay_node',
            name='depth_overlay_node',
            output='screen',
        ),
    ])
