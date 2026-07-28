#!/usr/bin/env python3
"""Launch the arena baseline and optional perception/navigation components."""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, LogInfo
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')
    use_rviz = LaunchConfiguration('use_rviz')
    use_navigation = LaunchConfiguration('use_navigation')
    use_perception = LaunchConfiguration('use_perception')
    bringup_share = get_package_share_directory('space_bringup')
    gazebo_share = get_package_share_directory('space_gazebo')
    perception_share = get_package_share_directory('space_perception')
    nav2_params = os.path.join(
        bringup_share, 'config', 'navigation', 'nav2_params.yaml'
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_share, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={
            name: LaunchConfiguration(name)
            for name in (
                'use_sim_time', 'world', 'spawn_x', 'spawn_y',
                'spawn_z', 'spawn_yaw'
            )
        }.items(),
    )
    terrain_perception = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                perception_share,
                'launch',
                'terrain_perception.launch.py',
            )
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'input_cloud_topic': '/camera/points',
            'target_frame': 'odom',
            'base_frame': 'base_footprint',
        }.items(),
        condition=IfCondition(use_perception),
    )
    navigation_nodes = [
        Node(
            package='slam_toolbox',
            executable='async_slam_toolbox_node',
            name='slam_toolbox',
            output='screen',
            parameters=[
                os.path.join(
                    bringup_share, 'config', 'common', 'slam_params.yaml'
                ),
                {'use_sim_time': use_sim_time},
            ],
            condition=IfCondition(use_navigation),
        ),
        Node(
            package='nav2_controller',
            executable='controller_server',
            name='controller_server',
            output='screen',
            parameters=[nav2_params, {'use_sim_time': use_sim_time}],
            remappings=[('/cmd_vel', '/cmd_vel_in')],
            condition=IfCondition(use_navigation),
        ),
        Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            output='screen',
            parameters=[nav2_params, {'use_sim_time': use_sim_time}],
            condition=IfCondition(use_navigation),
        ),
        Node(
            package='nav2_behaviors',
            executable='behavior_server',
            name='behavior_server',
            output='screen',
            parameters=[nav2_params, {'use_sim_time': use_sim_time}],
            remappings=[('/cmd_vel', '/cmd_vel_in')],
            condition=IfCondition(use_navigation),
        ),
        Node(
            package='nav2_bt_navigator',
            executable='bt_navigator',
            name='bt_navigator',
            output='screen',
            parameters=[nav2_params, {'use_sim_time': use_sim_time}],
            condition=IfCondition(use_navigation),
        ),
    ]

    return LaunchDescription(
        [
            DeclareLaunchArgument('use_sim_time', default_value='true'),
            DeclareLaunchArgument('use_rviz', default_value='true'),
            DeclareLaunchArgument('use_navigation', default_value='false'),
            DeclareLaunchArgument('use_perception', default_value='true'),
            DeclareLaunchArgument(
                'world', default_value='arena_test_slope_v04.sdf'
            ),
            DeclareLaunchArgument('spawn_x', default_value='-1.2'),
            DeclareLaunchArgument('spawn_y', default_value='-1.6'),
            DeclareLaunchArgument('spawn_z', default_value='0.12'),
            DeclareLaunchArgument('spawn_yaw', default_value='0.0'),
            LogInfo(
                msg=(
                    'Simulation uses a temporary direct Gazebo DiffDrive '
                    'backend; ArduPilot is intentionally not started.'
                )
            ),
            gazebo,
            terrain_perception,
            Node(
                package='space_controller',
                executable='command_safety_node',
                name='space_command_safety',
                output='screen',
                parameters=[{'use_sim_time': use_sim_time}],
            ),
            Node(
                package='robot_localization',
                executable='ekf_node',
                name='ekf_filter_node',
                output='screen',
                parameters=[
                    os.path.join(
                        bringup_share, 'config', 'common', 'ekf.yaml'
                    ),
                    {'use_sim_time': use_sim_time},
                ],
            ),
            Node(
                package='space_gazebo',
                executable='arena_marker_publisher',
                output='screen',
                parameters=[{'use_sim_time': use_sim_time}],
            ),
            Node(
                package='depthimage_to_laserscan',
                executable='depthimage_to_laserscan_node',
                name='depth_to_scan',
                output='screen',
                parameters=[
                    {
                        'use_sim_time': use_sim_time,
                        'scan_height': 24,
                        'range_min': 0.18,
                        'range_max': 5.0,
                        'output_frame': 'camera_link',
                    }
                ],
                remappings=[
                    ('depth', '/camera/depth_image_raw'),
                    ('depth_camera_info', '/camera/camera_info'),
                    ('scan', '/scan'),
                ],
                condition=IfCondition(use_perception),
            ),
            Node(
                package='space_perception',
                executable='depth_overlay_node',
                output='screen',
                parameters=[{'use_sim_time': use_sim_time}],
                condition=IfCondition(use_perception),
            ),
            *navigation_nodes,
            Node(
                package='rviz2',
                executable='rviz2',
                name='rviz2',
                output='screen',
                arguments=[
                    '-d',
                    os.path.join(
                        bringup_share, 'rviz', 'rover_simulation.rviz'
                    ),
                ],
                parameters=[{'use_sim_time': use_sim_time}],
                condition=IfCondition(use_rviz),
            ),
        ]
    )
