# space

우주로버 챌린지용 경량 스키드스티어 로버 워크스페이스입니다.

이 레포는 원본 `protkjj/drobot`에서 필요한 방향만 선별해서 새로 정리한 버전입니다. 원본 레포의 대형 Gazebo 월드, 병원/창고 모델, YOLO 학습 데이터, 드론/변형 로봇 중심 코드는 제외하고, 대회 준비에 필요한 최소 구조만 남겼습니다.

현재 남긴 핵심 범위는 다음과 같습니다.

- 4륜 스키드스티어 로버 모델
- RGB-D 카메라, IMU, 오도메트리 기반 시뮬레이션
- 물리 LiDAR 없이 depth camera를 `/scan`으로 변환하는 Nav2 구조
- Nav2 글로벌 플래너 + DWB 로컬 플래너
- 로버 모드용 휠 명령 게이트
- Pixhawk/PX4 연동을 위한 최소 bridge 골격
- 임무 요구조건과 하드웨어 결정을 기록하는 문서

원본 `drobot/` 폴더는 참고용 clone으로 같은 폴더 안에 남겨둘 수 있습니다. 새 repo에서는 `.gitignore`로 제외됩니다.

## 폴더 구조

```text
space/
├── docs/                  # 요구조건, 레포 범위, 설계 결정 문서
├── hardware/              # 구동계/전원 설계 메모
├── firmware/              # 향후 실기 펌웨어 자리
└── ros2_ws/
    └── src/
        ├── space_description/     # 로버 URDF, Gazebo 플러그인, 기본 경기장
        ├── space_bringup/         # launch, bridge, EKF, SLAM, Nav2 설정
        ├── space_controller/      # /cmd_vel 게이트 및 휠 제어 골격
        ├── space_perception/      # depth 기반 조종 보조 overlay
        └── space_px4_interface/   # PX4 연동 골격
```

## 빌드

```bash
cd ros2_ws
colcon build --symlink-install
source install/setup.bash
```

`space_px4_interface`는 `px4_msgs`가 필요합니다. PX4 환경이 아직 없다면 우선 로버 핵심 패키지만 빌드합니다.

```bash
colcon build --symlink-install \
  --packages-select space_description space_bringup space_controller space_perception
```

## 시뮬레이션 실행

```bash
source install/setup.bash
ros2 launch space_bringup navigation.launch.py
```

현재 경기장 world는 2.4 m 암석 구간, 3 m 모래 구간, 경사 구간을 표현하기 위한 시작점입니다. 실제 단차 높이, 경사각, 입자 깊이/입도 정보가 확정되면 이 world를 대회 조건에 맞게 다시 모델링합니다.
