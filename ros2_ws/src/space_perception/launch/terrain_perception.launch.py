#!/usr/bin/env python3
"""Launch filtering, elevation mapping, and geometric terrain features."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    package_share = get_package_share_directory('space_perception')
    default_params = os.path.join(
        package_share, 'config', 'terrain_perception.yaml'
    )
    use_sim_time = LaunchConfiguration('use_sim_time')
    params_file = LaunchConfiguration('params_file')
    input_topic = LaunchConfiguration('input_cloud_topic')
    target_frame = LaunchConfiguration('target_frame')
    base_frame = LaunchConfiguration('base_frame')
    common_overrides = {
        'use_sim_time': use_sim_time,
        'target_frame': target_frame,
        'base_frame': base_frame,
    }
    return LaunchDescription(
        [
            DeclareLaunchArgument('use_sim_time', default_value='true'),
            DeclareLaunchArgument('params_file', default_value=default_params),
            DeclareLaunchArgument(
                'input_cloud_topic', default_value='/camera/points'
            ),
            DeclareLaunchArgument('target_frame', default_value='odom'),
            DeclareLaunchArgument('base_frame', default_value='base_footprint'),
            Node(
                package='space_perception',
                executable='terrain_pointcloud_filter_node',
                name='terrain_pointcloud_filter_node',
                output='screen',
                parameters=[
                    params_file,
                    common_overrides,
                    {'input_topic': input_topic},
                ],
            ),
            Node(
                package='space_perception',
                executable='local_elevation_map_node',
                name='local_elevation_map_node',
                output='screen',
                parameters=[params_file, common_overrides],
            ),
            Node(
                package='space_perception',
                executable='terrain_feature_node',
                name='terrain_feature_node',
                output='screen',
                parameters=[params_file, common_overrides],
            ),
            Node(
                package='space_perception',
                executable='terrain_traversability_node',
                name='terrain_traversability_node',
                output='screen',
                parameters=[params_file, {'use_sim_time': use_sim_time}],
            ),
        ]
    )
