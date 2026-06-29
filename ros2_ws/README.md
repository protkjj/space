# ROS 2 워크스페이스

이 워크스페이스는 우주로버 챌린지용 소프트웨어를 작게 시작하기 위한 구조입니다.

## 패키지

| 패키지 | 역할 |
| --- | --- |
| `space_description` | 경량 로버 URDF, Gazebo 플러그인, 시작용 경기장 world |
| `space_bringup` | 시뮬레이션, bridge, EKF, depth-to-scan, Nav2 launch |
| `space_controller` | 로버 모드용 휠 명령 게이트 |
| `space_perception` | 카메라 조종 보조용 depth overlay |
| `space_px4_interface` | 선택적 PX4 uORB bridge 골격 |

## 핵심 패키지 빌드

PX4 메시지가 아직 준비되지 않았다면 아래처럼 핵심 로버 패키지만 먼저 빌드합니다.

```bash
colcon build --symlink-install \
  --packages-select space_description space_bringup space_controller space_perception
```

PX4 연동 환경까지 준비되면 전체 빌드를 실행합니다.

```bash
colcon build --symlink-install
```

## 기본 실행

```bash
source install/setup.bash
ros2 launch space_bringup navigation.launch.py
```

기본 실행은 primitive URDF 로버와 시작용 경기장 world를 사용합니다. 실제 CAD가 확정되기 전까지는 이 모델로 Nav2, depth camera, 조종 보조, 경로주행 구조를 먼저 검증합니다.
