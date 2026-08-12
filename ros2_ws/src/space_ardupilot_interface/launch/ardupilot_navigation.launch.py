#!/usr/bin/env python3
"""
Bring up navigation with ArduPilot as the motion authority.

This is the Milestone A command chain, with no simulator backend in it:

    Nav2 -> /cmd_vel_in -> command safety -> /cmd_vel_safe
         -> ardupilot_adapter -> /ap/cmd_vel -> AP_DDS -> the vehicle

and the estimate flowing the other way:

    ArduPilot EKF3 -> /ap/pose/filtered -> ardupilot_odometry
                   -> /odom and odom -> base_footprint -> Nav2

`robot_localization` is deliberately absent. ArduPilot's EKF3 is already
fusing the IMU with whatever position source is configured, and on this rover
wheel odometry is sent *to* the autopilot, so a second filter here would fuse
the same information twice. Milestone A asks for one authoritative publisher
per transform; on this path that is ArduPilot, by way of
`ardupilot_odometry`.

**The costmaps have no sensor input in this launch.** Nav2 will plan and
follow paths through empty space. Obstacle avoidance requires a `/scan` or
traversability source, which comes from the camera and is not started here.
Use this to exercise the command and estimate chain, not to demonstrate
autonomous obstacle avoidance.
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


# Package and executable are listed explicitly rather than derived from the
# node name: nav2 does not name them consistently, and behavior_server lives
# in nav2_behaviors rather than nav2_behavior.
NAV2_SERVERS = [
    ('nav2_controller', 'controller_server'),
    ('nav2_planner', 'planner_server'),
    ('nav2_behaviors', 'behavior_server'),
    ('nav2_bt_navigator', 'bt_navigator'),
]
NAV2_NODE_NAMES = [name for _, name in NAV2_SERVERS]


def generate_launch_description():
    """Assemble the ArduPilot-authoritative navigation stack."""
    interface_share = get_package_share_directory('space_ardupilot_interface')
    description_share = get_package_share_directory('space_description')
    bringup_share = get_package_share_directory('space_bringup')

    xacro_file = os.path.join(
        description_share, 'urdf', 'space_rover.urdf.xacro')
    adapter_config = os.path.join(
        interface_share, 'config', 'adapter.yaml')
    nav2_params = os.path.join(
        bringup_share, 'config', 'navigation', 'nav2_params.yaml')

    use_sim_time = LaunchConfiguration('use_sim_time')
    use_navigation = LaunchConfiguration('use_navigation')
    manage_vehicle = LaunchConfiguration('manage_vehicle')

    robot_description = ParameterValue(
        Command(['xacro ', xacro_file]), value_type=str)

    nav2_nodes = [
        Node(
            package=package,
            executable=name,
            name=name,
            output='screen',
            parameters=[nav2_params, {'use_sim_time': use_sim_time}],
            # Nav2 writes to /cmd_vel; everything on this rover reaches the
            # motors through the safety node, so it is renamed here rather
            # than given a path of its own.
            remappings=[('/cmd_vel', '/cmd_vel_in')],
            condition=IfCondition(use_navigation),
        )
        for package, name in NAV2_SERVERS
    ]

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time', default_value='false',
            description='Use simulation clock'),
        DeclareLaunchArgument(
            'use_navigation', default_value='true',
            description='Start the Nav2 servers'),
        DeclareLaunchArgument(
            'manage_vehicle', default_value='false',
            description='Let the adapter run pre-arm, mode switch and arming'),

        # base_footprint -> base_link and every sensor frame below it.
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[
                {'robot_description': robot_description},
                {'use_sim_time': use_sim_time},
            ],
        ),

        # odom -> base_footprint, from the autopilot's own estimate.
        Node(
            package='space_ardupilot_interface',
            executable='ardupilot_odometry',
            name='space_ardupilot_odometry',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time}],
        ),

        # Clipping, the driving-mode gate, and the stale-command watchdog.
        Node(
            package='space_controller',
            executable='command_safety_node',
            name='space_command_safety',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time}],
        ),

        # /cmd_vel_safe -> /ap/cmd_vel.
        Node(
            package='space_ardupilot_interface',
            executable='ardupilot_adapter',
            name='space_ardupilot_adapter',
            output='screen',
            parameters=[
                adapter_config,
                {'use_sim_time': use_sim_time},
                {'manage_vehicle': manage_vehicle},
            ],
        ),

        *nav2_nodes,

        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_navigation',
            output='screen',
            parameters=[{
                'use_sim_time': use_sim_time,
                'autostart': True,
                'node_names': NAV2_NODE_NAMES,
            }],
            condition=IfCondition(use_navigation),
        ),
    ])
