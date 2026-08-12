#!/usr/bin/env python3
"""Launch the ArduPilot adapter node."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    """Generate launch description for ArduPilot adapter."""
    pkg_share = get_package_share_directory('space_ardupilot_interface')
    default_config = os.path.join(pkg_share, 'config', 'adapter.yaml')

    use_sim_time = LaunchConfiguration('use_sim_time')
    config_file = LaunchConfiguration('config_file')

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation clock',
        ),
        DeclareLaunchArgument(
            'config_file',
            default_value=default_config,
            description='Path to adapter configuration file',
        ),
        Node(
            package='space_ardupilot_interface',
            executable='ardupilot_adapter',
            name='space_ardupilot_adapter',
            output='screen',
            parameters=[
                config_file,
                {'use_sim_time': use_sim_time},
            ],
        ),
    ])
