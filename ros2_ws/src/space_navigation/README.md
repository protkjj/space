# space_navigation

Gazebo의 로버를 RViz 또는 좌표 명령으로 목표 지점까지 자율주행시키는
ROS 2 패키지입니다. 기존 `space_bringup`의 Nav2 구성을 사용하며,
SmacPlanner2D가 장애물 비용지도에서 최단 비용 경로를 계획하고 DWB가
그 경로를 추종합니다. 시뮬레이션의 절대 `odom` 좌표계를 사용하므로
온라인 SLAM 보정 때문에 지정한 목표가 움직이지 않습니다.

## 빌드

```bash
cd ~/Desktop/space
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --packages-up-to space_navigation
source install/setup.bash
```

## 실행 및 목표 지정

```bash
ros2 launch space_bringup simulation.launch.py
```

Gazebo와 RViz가 켜지면 RViz 상단의 `2D Goal Pose` 도구로 지형 위 목표
위치를 클릭하고 드래그해 최종 방향을 정합니다.
점만 지정하려면 `Publish Point` 도구를 사용할 수도 있습니다.
기본 월드는 실제 시각·충돌 메시를 가진 `arena_terrain_v04.sdf`입니다.
터미널에 `Gazebo world selected: arena_terrain_v04.sdf`가 표시되는지
확인할 수 있습니다.

좌표로 직접 목표를 보낼 수도 있습니다.

```bash
ros2 run space_navigation send_goal 1.0 0.5 0.0
```

인자는 순서대로 `x`, `y`, `yaw(rad)`이며 기본 좌표계는 `odom`입니다.
진행 상태는 다음 명령으로 확인할 수 있습니다.

```bash
ros2 topic echo /space_goal_navigator/navigation_status
```

새 목표를 보내면 Nav2가 기존 주행을 선점하고 새 목표로 재계획합니다.
`/plan`에는 전역 최단 비용 경로가, `/local_plan`에는 로컬 추종 경로가
발행됩니다. Navigation은 Perception을 직접 구독하지 않고
`space_mission`의 `/mission/traversability`만 사용합니다. 현재 Mission은
카메라 기반 경사도·거칠기·단차를 전달하며, 이후 슬립률과 중형 로버
변환 결과를 같은 인터페이스에 융합합니다.
