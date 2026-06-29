#!/usr/bin/env python3
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from ros_gz_bridge.actions import RosGzBridge


def launch_setup(context):
    use_sim_time = LaunchConfiguration('use_sim_time')
    world_name = context.launch_configurations.get('world', 'space_challenge_empty')
    spawn_x = LaunchConfiguration('spawn_x')
    spawn_y = LaunchConfiguration('spawn_y')
    spawn_z = LaunchConfiguration('spawn_z')

    desc_pkg = get_package_share_directory('space_description')
    bringup_pkg = get_package_share_directory('space_bringup')

    urdf_file = os.path.join(desc_pkg, 'urdf', 'space_rover.urdf.xacro')
    world_file = os.path.join(desc_pkg, 'worlds', f'{world_name}.sdf')

    robot_description = ParameterValue(Command(['xacro ', urdf_file]), value_type=str)

    nav2_params = os.path.join(bringup_pkg, 'config', 'navigation', 'nav2_params.yaml')
    ekf_params = os.path.join(bringup_pkg, 'config', 'common', 'ekf.yaml')
    slam_params = os.path.join(bringup_pkg, 'config', 'common', 'slam_params.yaml')
    bridge_config = os.path.join(bringup_pkg, 'config', 'common', 'ros_gz_bridge.yaml')

    gz_resource_path = SetEnvironmentVariable(
        'GZ_SIM_RESOURCE_PATH',
        os.pathsep.join([
            os.path.join(desc_pkg, '..'),
            os.environ.get('GZ_SIM_RESOURCE_PATH', ''),
        ])
    )

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f'-r {world_file}'}.items(),
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': use_sim_time,
        }],
    )

    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'space_rover',
            '-x', spawn_x,
            '-y', spawn_y,
            '-z', spawn_z,
        ],
        output='screen',
    )

    ros_gz_bridge = RosGzBridge(
        bridge_name='ros_gz_bridge',
        config_file=bridge_config,
    )

    depth_to_scan = Node(
        package='depthimage_to_laserscan',
        executable='depthimage_to_laserscan_node',
        name='depth_to_scan',
        output='screen',
        parameters=[{
            'scan_height': 24,
            'range_min': 0.18,
            'range_max': 5.0,
            'output_frame': 'camera_link',
        }],
        remappings=[
            ('depth', '/camera/depth_image_raw'),
            ('depth_camera_info', '/camera/camera_info'),
            ('scan', '/scan'),
        ],
    )

    ekf_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[ekf_params, {'use_sim_time': True}],
    )

    slam_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[slam_params, {'use_sim_time': True}],
    )

    controller_server = Node(
        package='nav2_controller',
        executable='controller_server',
        name='controller_server',
        output='screen',
        parameters=[nav2_params],
        remappings=[('/cmd_vel', '/cmd_vel_in')],
    )

    planner_server = Node(
        package='nav2_planner',
        executable='planner_server',
        name='planner_server',
        output='screen',
        parameters=[nav2_params],
    )

    behavior_server = Node(
        package='nav2_behaviors',
        executable='behavior_server',
        name='behavior_server',
        output='screen',
        parameters=[nav2_params],
    )

    bt_navigator = Node(
        package='nav2_bt_navigator',
        executable='bt_navigator',
        name='bt_navigator',
        output='screen',
        parameters=[nav2_params],
    )

    lifecycle_navigation = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_navigation',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'autostart': True,
            'node_names': [
                'controller_server',
                'planner_server',
                'behavior_server',
                'bt_navigator',
            ],
        }],
    )

    lifecycle_slam = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_slam',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'autostart': True,
            'node_names': ['slam_toolbox'],
        }],
    )

    wheel_driver = Node(
        package='space_controller',
        executable='wheel_motor_driver_node',
        name='space_wheel_motor_driver',
        output='screen',
        parameters=[{'use_sim_time': True}],
    )

    depth_overlay = Node(
        package='space_perception',
        executable='depth_overlay_node',
        name='depth_overlay_node',
        output='screen',
        parameters=[{'use_sim_time': True}],
    )

    return [
        gz_resource_path,
        gz_sim,
        robot_state_publisher,
        spawn_robot,
        ros_gz_bridge,
        depth_to_scan,
        ekf_node,
        slam_node,
        lifecycle_slam,
        controller_server,
        planner_server,
        behavior_server,
        bt_navigator,
        lifecycle_navigation,
        wheel_driver,
        depth_overlay,
    ]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('world', default_value='space_challenge_empty'),
        DeclareLaunchArgument('spawn_x', default_value='-2.3'),
        DeclareLaunchArgument('spawn_y', default_value='0.0'),
        DeclareLaunchArgument('spawn_z', default_value='0.18'),
        OpaqueFunction(function=launch_setup),
    ])
