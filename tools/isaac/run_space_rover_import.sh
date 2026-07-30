#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
ROS_WS="${REPO_ROOT}/ros2_ws"
ISAACSIM_ROOT="${ISAACSIM_ROOT:-/home/kj/IsaacSim/isaacsim}"

URDF_OUT="${SPACE_ROVER_URDF:-${ROS_WS}/build/isaac/space_rover.urdf}"
USD_OUT="${SPACE_ROVER_USD:-${ROS_WS}/build/isaac/space_rover_friction_test.usd}"

if [[ ! -x "${ISAACSIM_ROOT}/python.sh" ]]; then
  echo "Isaac Sim python.sh not found: ${ISAACSIM_ROOT}/python.sh" >&2
  echo "Set ISAACSIM_ROOT to your Isaac Sim install directory." >&2
  exit 1
fi

"${SCRIPT_DIR}/generate_space_rover_urdf.sh" "${URDF_OUT}"
"${ISAACSIM_ROOT}/python.sh" "${SCRIPT_DIR}/import_space_rover.py" \
  --urdf "${URDF_OUT}" \
  --usd "${USD_OUT}" \
  "$@"

