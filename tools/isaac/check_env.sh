#!/usr/bin/env bash
set -euo pipefail

ISAACSIM_ROOT="${ISAACSIM_ROOT:-/home/kj/IsaacSim/isaacsim}"

echo "== OS =="
lsb_release -a

echo
echo "== ROS 2 =="
if [[ -f /opt/ros/jazzy/setup.bash ]]; then
  set +u
  # shellcheck disable=SC1091
  source /opt/ros/jazzy/setup.bash
  set -u
  echo "ROS_DISTRO=${ROS_DISTRO:-unset}"
else
  echo "ROS 2 Jazzy setup file not found at /opt/ros/jazzy/setup.bash"
fi

echo
echo "== NVIDIA GPU =="
if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
else
  echo "nvidia-smi not found"
fi

echo
echo "== Isaac Sim =="
if [[ -x "${ISAACSIM_ROOT}/python.sh" && -x "${ISAACSIM_ROOT}/isaac-sim.sh" ]]; then
  echo "ISAACSIM_ROOT=${ISAACSIM_ROOT}"
  if [[ -f "${ISAACSIM_ROOT}/VERSION" ]]; then
    echo "VERSION=$(<"${ISAACSIM_ROOT}/VERSION")"
  fi
else
  echo "Isaac Sim launch scripts not found under ${ISAACSIM_ROOT}"
fi
