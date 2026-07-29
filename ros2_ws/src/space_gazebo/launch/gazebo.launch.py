#!/usr/bin/env python3
"""Launch the temporary direct-drive Gazebo simulation backend."""

import os

from ament_index_python.packages import (
    get_package_prefix,
    get_package_share_directory,
)
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    OpaqueFunction,
    SetEnvironmentVariable,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def _launch_setup(context):
    use_sim_time = LaunchConfiguration('use_sim_time')
    world_name = LaunchConfiguration('world').perform(context)
    spawn_x = LaunchConfiguration('spawn_x')
    spawn_y = LaunchConfiguration('spawn_y')
    spawn_z = LaunchConfiguration('spawn_z')
    spawn_yaw = LaunchConfiguration('spawn_yaw')

    description_share = get_package_share_directory('space_description')
    gazebo_share = get_package_share_directory('space_gazebo')
    gazebo_prefix = get_package_prefix('space_gazebo')
    ros_gz_sim_share = get_package_share_directory('ros_gz_sim')

    robot_xacro = os.path.join(
        gazebo_share, 'urdf', 'space_rover.gazebo.urdf.xacro'
    )
    world_file = (
        world_name
        if os.path.isabs(world_name)
        else os.path.join(
            gazebo_share,
            'worlds',
            world_name if world_name.endswith('.sdf') else f'{world_name}.sdf',
        )
    )
    bridge_config = os.path.join(
        gazebo_share, 'config', 'ros_gz_bridge.yaml'
    )
    gui_config = os.path.join(
        gazebo_share, 'config', 'rover_gui.config'
    )
    robot_description = ParameterValue(
        Command(['xacro ', robot_xacro]), value_type=str
    )

    resource_paths = [
        os.path.join(gazebo_share, 'models'),
        os.path.dirname(description_share),
        os.path.dirname(gazebo_share),
    ]
    existing_resource_path = os.environ.get('GZ_SIM_RESOURCE_PATH')
    if existing_resource_path:
        resource_paths.append(existing_resource_path)
    gui_plugin_paths = [os.path.join(gazebo_prefix, 'lib')]
    existing_gui_plugin_path = os.environ.get('GZ_GUI_PLUGIN_PATH')
    if existing_gui_plugin_path:
        gui_plugin_paths.append(existing_gui_plugin_path)

    return [
        SetEnvironmentVariable(
            'GZ_SIM_RESOURCE_PATH', os.pathsep.join(resource_paths)
        ),
        SetEnvironmentVariable(
            'GZ_GUI_PLUGIN_PATH', os.pathsep.join(gui_plugin_paths)
        ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(ros_gz_sim_share, 'launch', 'gz_sim.launch.py')
            ),
            launch_arguments={
                'gz_args': f'-r --gui-config {gui_config} {world_file}'
            }.items(),
        ),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[
                {
                    'robot_description': robot_description,
                    'use_sim_time': use_sim_time,
                }
            ],
        ),
        Node(
            package='ros_gz_sim',
            executable='create',
            arguments=[
                '-topic',
                'robot_description',
                '-name',
                'space_rover',
                '-x',
                spawn_x,
                '-y',
                spawn_y,
                '-z',
                spawn_z,
                '-Y',
                spawn_yaw,
            ],
            output='screen',
        ),
        Node(
            package='ros_gz_bridge',
            executable='parameter_bridge',
            name='ros_gz_bridge',
            output='screen',
            parameters=[{'config_file': bridge_config}],
        ),
    ]


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument('use_sim_time', default_value='true'),
            DeclareLaunchArgument(
                'world', default_value='arena_terrain_v04.sdf'
            ),
            DeclareLaunchArgument('spawn_x', default_value='-1.2'),
            DeclareLaunchArgument('spawn_y', default_value='-1.6'),
            DeclareLaunchArgument(
                'spawn_z',
                default_value='0.23',
                description=(
                    'Terrain-world default height; override when selecting '
                    'a world with a different surface elevation.'
                ),
            ),
            DeclareLaunchArgument('spawn_yaw', default_value='0.0'),
            OpaqueFunction(function=_launch_setup),
        ]
    )
