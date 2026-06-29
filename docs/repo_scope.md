# 레포 범위

## 원본 방향에서 가져온 것

- ROS 2 Jazzy 워크스페이스 구조
- Gazebo Harmonic 기반 시뮬레이션 흐름
- 스키드스티어 로버와 `/cmd_vel` 제어 방식
- RGB-D 카메라 토픽을 이용한 영상/거리 정보
- IMU + 오도메트리 EKF 설정
- Nav2 launch/config 구조
- Pixhawk 연동을 위한 PX4 bridge 개념

## 새 레포에서 제거한 것

- 병원/창고/카페 등 대형 Gazebo 월드
- 대형 모델 라이브러리와 STL 중심 환경 자산
- 기존 YOLO 데이터셋과 학습된 모델 바이너리
- 드론/VTOL 동작을 주 목표로 하는 코드
- 변형 arm 펌웨어와 서보 시퀀싱
- baseline의 물리 LiDAR 의존성

## 새 레포로 분리한 이유

원본 레포에서 파일을 삭제해도 Git 히스토리와 Git LFS 저장소에는 대형 자산이 남습니다. 그래서 원본은 참고용 clone으로 두고, 우주로버 챌린지에 필요한 코드만 선별해 새 repo를 시작합니다.
