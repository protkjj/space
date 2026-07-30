#!/usr/bin/env python3
"""Launch the arena baseline and optional perception/navigation components."""

import math
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    LogInfo,
    OpaqueFunction,
)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from nav2_common.launch import RewrittenYaml
from space_description.rover_geometry import footprint_string, load_geometry


# RViz cannot render the Gazebo world directly, so arena_marker_publisher draws
# the ground-truth arena as a mesh marker. Each world needs the transform that
# matches how its model.sdf places the mesh (STEP-derived slope is in mm and
# rotated; the terrain STL is already in metres and axis-aligned).
ARENA_MARKER_PRESETS = {
    'arena_test_slope_v04': {
        'mesh_resource': (
            'package://space_gazebo/models/arena_test_slope_v04/'
            'meshes/arena_visual.stl'
        ),
        'scale': [0.001, 0.001, 0.001],
        'position': [-0.8, -2.0, 0.0],
        'orientation_rpy': [math.pi / 2.0, 0.0, 0.0],
    },
    'arena_terrain_v04': {
        'mesh_resource': (
            'package://space_gazebo/models/arena_terrain_v04/'
            'meshes/arena_visual.stl'
        ),
        'scale': [1.0, 1.0, 1.0],
        'position': [0.0, 0.0, 0.0],
        'orientation_rpy': [0.0, 0.0, 0.0],
    },
}


def _arena_marker_node(context, *args, **kwargs):
    """Pick the arena marker preset that matches the launched world."""
    world = LaunchConfiguration('world').perform(context)
    key = os.path.splitext(os.path.basename(world))[0]
    preset = ARENA_MARKER_PRESETS.get(key)
    if preset is None:
        # Unknown world: assume a same-named model whose mesh is already in
        # metres and axis-aligned (the convention new arenas should follow).
        preset = {
            'mesh_resource': (
                f'package://space_gazebo/models/{key}/meshes/arena_visual.stl'
            ),
            'scale': [1.0, 1.0, 1.0],
            'position': [0.0, 0.0, 0.0],
            'orientation_rpy': [0.0, 0.0, 0.0],
        }
    return [
        Node(
            package='space_gazebo',
            executable='arena_marker_publisher',
            output='screen',
            parameters=[
                {'use_sim_time': LaunchConfiguration('use_sim_time')},
                preset,
            ],
        )
    ]


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')
    use_rviz = LaunchConfiguration('use_rviz')
    use_navigation = LaunchConfiguration('use_navigation')
    use_perception = LaunchConfiguration('use_perception')
    use_traversability_layer = LaunchConfiguration(
        'use_traversability_layer'
    )
    bringup_share = get_package_share_directory('space_bringup')
    gazebo_share = get_package_share_directory('space_gazebo')
    mission_share = get_package_share_directory('space_mission')
    navigation_share = get_package_share_directory('space_navigation')
    perception_share = get_package_share_directory('space_perception')
    nav2_params_file = os.path.join(
        bringup_share, 'config', 'navigation', 'nav2_params.yaml'
    )
    # Footprint comes from the CAD, not from nav2_params.yaml. Both costmaps
    # carried footprints sized to the pre-51b34ac chassis -- oversized by up to
    # 60 mm -- which silently discards gaps the rover can actually pass, and
    # judging passable gaps is part of the mission.
    rover_footprint = footprint_string(load_geometry())
    nav2_params = RewrittenYaml(
        source_file=nav2_params_file,
        param_rewrites={
            (
                'local_costmap.local_costmap.ros__parameters.'
                'traversability_layer.enabled'
            ): use_traversability_layer,
            (
                'global_costmap.global_costmap.ros__parameters.'
                'traversability_layer.enabled'
            ): use_traversability_layer,
            'local_costmap.local_costmap.ros__parameters.footprint': (
                rover_footprint
            ),
            'global_costmap.global_costmap.ros__parameters.footprint': (
                rover_footprint
            ),
        },
        convert_types=True,
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gazebo_share, 'launch', 'gazebo.launch.py')
        ),
        launch_arguments={
            name: LaunchConfiguration(name)
            for name in (
                'use_sim_time', 'world', 'spawn_x', 'spawn_y',
                'spawn_z', 'spawn_yaw', 'headless'
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
        Node(
            package='space_navigation',
            executable='goal_navigator',
            name='space_goal_navigator',
            output='screen',
            parameters=[
                os.path.join(
                    navigation_share,
                    'config',
                    'goal_navigator.yaml',
                ),
                {'use_sim_time': use_sim_time},
            ],
            condition=IfCondition(use_navigation),
        ),
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_navigation',
            output='screen',
            parameters=[
                {
                    'use_sim_time': use_sim_time,
                    'autostart': True,
                    'bond_timeout': 0.0,
                    'node_names': [
                        'controller_server',
                        'planner_server',
                        'behavior_server',
                        'bt_navigator',
                    ],
                }
            ],
            condition=IfCondition(use_navigation),
        ),
    ]

    return LaunchDescription(
        [
            DeclareLaunchArgument('use_sim_time', default_value='true'),
            DeclareLaunchArgument('use_rviz', default_value='true'),
            DeclareLaunchArgument(
                'headless', default_value='false',
                description=(
                    'Run Gazebo without its GUI. Pair with use_rviz:=false '
                    'where no GL context exists.'
                ),
            ),
            DeclareLaunchArgument(
                'use_navigation',
                default_value='true',
                description=(
                    'Start odom-anchored Nav2 and point-and-click goals.'
                ),
            ),
            DeclareLaunchArgument('use_perception', default_value='true'),
            DeclareLaunchArgument(
                'use_traversability_layer',
                default_value='true',
                description=(
                    'Enable terrain costs in both Nav2 costmaps.'
                ),
            ),
            DeclareLaunchArgument(
                'world',
                default_value='arena_terrain_v04.sdf',
                description=(
                    'Gazebo world file. The default is the non-flat '
                    'competition terrain.'
                ),
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
            LogInfo(
                msg=(
                    'Simulation uses a temporary direct Gazebo DiffDrive '
                    'backend; ArduPilot is intentionally not started.'
                )
            ),
            LogInfo(
                msg=['Gazebo world selected: ', LaunchConfiguration('world')]
            ),
            LogInfo(
                msg=(
                    'Keyboard control: focus the Gazebo 3D view, then hold '
                    'the arrow keys to drive. Press Space to stop.'
                )
            ),
            gazebo,
            terrain_perception,
            Node(
                package='space_mission',
                executable='traversability_fusion_node',
                name='mission_traversability_fusion',
                output='screen',
                parameters=[
                    os.path.join(
                        mission_share,
                        'config',
                        'mission.yaml',
                    ),
                    {'use_sim_time': use_sim_time},
                ],
            ),
            # Signature measurement: encoder(/joint_states) vs wheel-independent
            # actual velocity (sim: ground-truth /odom) -> /slip/estimate.
            Node(
                package='space_mission',
                executable='slip_estimator',
                name='slip_estimator',
                output='screen',
                parameters=[
                    os.path.join(
                        mission_share,
                        'config',
                        'slip.yaml',
                    ),
                    {'use_sim_time': use_sim_time},
                ],
            ),
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
            OpaqueFunction(function=_arena_marker_node),
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
