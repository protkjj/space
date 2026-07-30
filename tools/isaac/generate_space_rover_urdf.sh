#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
ROS_WS="${REPO_ROOT}/ros2_ws"
OUTPUT="${1:-${ROS_WS}/build/isaac/space_rover.urdf}"

mkdir -p "$(dirname "${OUTPUT}")"

# shellcheck disable=SC1091
set +u
source /opt/ros/jazzy/setup.bash
if [[ -f "${ROS_WS}/install/setup.bash" ]]; then
  # shellcheck disable=SC1091
  source "${ROS_WS}/install/setup.bash"
fi
set -u

xacro "${ROS_WS}/src/space_description/urdf/space_rover.urdf.xacro" > "${OUTPUT}"
echo "${OUTPUT}"
