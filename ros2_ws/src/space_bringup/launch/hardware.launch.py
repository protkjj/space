#!/usr/bin/env python3
"""Launch non-actuating Phase 1 hardware-side interface validation."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo
from launch.conditions import IfCondition
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    description_share = get_package_share_directory('space_description')
    robot_xacro = os.path.join(
        description_share, 'urdf', 'space_rover.urdf.xacro'
    )
    robot_description = ParameterValue(
        Command(['xacro ', robot_xacro]), value_type=str
    )

    start_perception = LaunchConfiguration('start_perception')
    start_command_safety = LaunchConfiguration('start_command_safety')

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                'start_perception',
                default_value='false',
                description='Start the camera depth overlay helper.',
            ),
            DeclareLaunchArgument(
                'start_command_safety',
                default_value='false',
                description=(
                    'Start interface validation only; /cmd_vel_safe has no '
                    'actuator consumer in Phase 1 hardware bringup.'
                ),
            ),
            LogInfo(
                msg=(
                    'WARNING: the ArduPilot hardware adapter is not '
                    'implemented in Phase 1; this launch cannot actuate '
                    'the rover.'
                )
            ),
            Node(
                package='robot_state_publisher',
                executable='robot_state_publisher',
                name='robot_state_publisher',
                output='screen',
                parameters=[
                    {
                        'robot_description': robot_description,
                        'use_sim_time': False,
                    }
                ],
            ),
            Node(
                package='space_perception',
                executable='depth_overlay_node',
                name='depth_overlay_node',
                output='screen',
                parameters=[{'use_sim_time': False}],
                condition=IfCondition(start_perception),
            ),
            Node(
                package='space_controller',
                executable='command_safety_node',
                name='space_command_safety',
                output='screen',
                parameters=[{'use_sim_time': False}],
                condition=IfCondition(start_command_safety),
            ),
        ]
    )
