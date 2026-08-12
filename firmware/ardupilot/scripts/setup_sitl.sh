#!/usr/bin/env bash
#
# Verify the Rover SITL toolchain and optionally start it.
#
# This script does not install anything. It checks each prerequisite that the
# DDS path actually needs, reports exactly which one is missing, and prints the
# command that fixes it. Every step it checks was executed by hand first; see
# ../README.md for the validation record and for what is still unvalidated.
#
# Usage:
#   ./setup_sitl.sh --check     # verify the environment only
#   ./setup_sitl.sh --run       # verify, then start Rover SITL
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION_FILE="${SCRIPT_DIR}/../version.txt"
ARDUPILOT_DIR="${ARDUPILOT_DIR:-$HOME/ardupilot}"

RED=$'\033[0;31m'; GREEN=$'\033[0;32m'; YELLOW=$'\033[1;33m'; NC=$'\033[0m'
ok()   { echo "${GREEN}[ ok ]${NC} $*"; }
warn() { echo "${YELLOW}[warn]${NC} $*"; }
fail() { echo "${RED}[fail]${NC} $*"; FAILURES=$((FAILURES + 1)); }

FAILURES=0
MODE=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --check) MODE="check"; shift ;;
        --run)   MODE="run";   shift ;;
        *) echo "unknown argument: $1"; echo "usage: $0 --check | --run"; exit 2 ;;
    esac
done

if [[ -z "$MODE" ]]; then
    echo "usage: $0 --check | --run"
    exit 2
fi

# ---------------------------------------------------------------- version pin

if [[ ! -f "$VERSION_FILE" ]]; then
    fail "version file not found: $VERSION_FILE"
    exit 1
fi

SITL_TAG=$(awk '/^\[SITL\]/{f=1} f&&/^tag:/{print $2; exit}' "$VERSION_FILE")
SITL_COMMIT=$(awk '/^\[SITL\]/{f=1} f&&/^commit:/{print $2; exit}' "$VERSION_FILE")

if [[ -z "${SITL_TAG:-}" || "$SITL_TAG" == "UNPINNED" ]]; then
    fail "no SITL version pinned in $VERSION_FILE"
    exit 1
fi
ok "pinned SITL version: $SITL_TAG ($SITL_COMMIT)"

# ------------------------------------------------------------ ardupilot source

if [[ ! -d "$ARDUPILOT_DIR/.git" ]]; then
    fail "ArduPilot source not found at $ARDUPILOT_DIR"
    echo "      git clone --recurse-submodules https://github.com/ArduPilot/ardupilot.git $ARDUPILOT_DIR"
else
    CURRENT_COMMIT=$(git -C "$ARDUPILOT_DIR" rev-parse HEAD)
    if [[ "$CURRENT_COMMIT" == "$SITL_COMMIT" ]]; then
        ok "ArduPilot checkout matches the pin"
    else
        fail "ArduPilot is at $CURRENT_COMMIT, pin expects $SITL_COMMIT"
        echo "      git -C $ARDUPILOT_DIR checkout $SITL_TAG"
        echo "      git -C $ARDUPILOT_DIR submodule update --init --recursive"
    fi
fi

# -------------------------------------------------------------- microxrceddsgen
#
# Required to build with DDS. Needs a JRE newer than 8; Gradle fails with
# "class file version 55.0" against Java 8. The branch must match the ArduPilot
# release: v4.7.0 for 4.7 and later, v4.5.1 for earlier ones.
#
# Note the flag spelling differs between tools: waf accepts --enable-dds and
# --enable-DDS, but sim_vehicle.py in 4.7 only accepts --enable-DDS.

if command -v microxrceddsgen >/dev/null 2>&1; then
    ok "microxrceddsgen found"
else
    fail "microxrceddsgen not on PATH (required to build with DDS)"
    echo "      ArduPilot 4.7 and later need the v4.7.0 branch; v4.5.1 is for"
    echo "      earlier releases only. Building the wrong branch fails late,"
    echo "      during IDL generation, not at configure time."
    echo "      git clone --recurse-submodules --branch v4.7.0 \\"
    echo "        https://github.com/ardupilot/Micro-XRCE-DDS-Gen.git \\"
    echo "        ~/Micro-XRCE-DDS-Gen-4.7"
    echo "      cd ~/Micro-XRCE-DDS-Gen-4.7 && ./gradlew assemble"
    echo "      export PATH=\$PATH:\$HOME/Micro-XRCE-DDS-Gen-4.7/scripts"
    echo "      (needs a JRE newer than 8: sudo update-alternatives --config java)"
fi

# -------------------------------------------------------------------- SITL build

SITL_BIN="$ARDUPILOT_DIR/build/sitl/bin/ardurover"
if [[ -x "$SITL_BIN" ]]; then
    ok "ardurover SITL binary present"
else
    fail "SITL binary not built: $SITL_BIN"
    echo "      cd $ARDUPILOT_DIR"
    echo "      ./waf configure --board sitl --enable-DDS && ./waf rover"
fi

# ------------------------------------------------------------------- XRCE agent

if command -v MicroXRCEAgent >/dev/null 2>&1; then
    ok "MicroXRCEAgent found"
else
    fail "MicroXRCEAgent not on PATH"
    echo "      sudo snap install micro-xrce-dds-agent --edge"
fi

# ------------------------------------------------------------------ sim_vehicle

if command -v sim_vehicle.py >/dev/null 2>&1; then
    ok "sim_vehicle.py on PATH"
else
    fail "sim_vehicle.py not on PATH"
    echo "      export PATH=\$PATH:$ARDUPILOT_DIR/Tools/autotest"
fi

# --------------------------------------------------------------------- MAVProxy
#
# sim_vehicle.py starts MAVProxy by default and exits if MAVProxy dies. On a
# host where a user-local NumPy 2.x shadows the system NumPy, MAVProxy's
# matplotlib import raises and takes SITL down with it. This is a host
# environment issue, not an ArduPilot one, so it is reported as a warning and
# the caller is told how to run without MAVProxy.

# Checking "import MAVProxy" is not sufficient: that succeeds even when
# mavproxy.py cannot start. mavproxy.py imports matplotlib near the top, so
# the matplotlib import is what actually has to work.
if ! python3 -c "import MAVProxy" >/dev/null 2>&1; then
    warn "MAVProxy is not installed; sim_vehicle.py will exit immediately."
    echo "      python3 -m pip install --user MAVProxy"
elif ! python3 -c "import matplotlib" >/dev/null 2>&1; then
    warn "MAVProxy is installed but its matplotlib import fails, so"
    echo "      sim_vehicle.py will exit as soon as MAVProxy starts."
    python3 -c "import matplotlib" 2>&1 | tail -1 | sed 's/^/      /'
    echo "      Common cause: a user-local NumPy shadowing the system NumPy."
    echo "      Compare: python3 -c 'import numpy; print(numpy.__file__)'"
    echo "      Workaround: run SITL with --no-mavproxy and attach any MAVLink"
    echo "      client to tcp:127.0.0.1:5760 (SITL blocks on SERIAL0 until one"
    echo "      connects)."
else
    ok "MAVProxy startup imports resolve"
fi

# --------------------------------------------------------------- ardupilot_msgs
#
# Needed only for the arming and mode-switch services, not for /ap/cmd_vel.

if [[ -d "$ARDUPILOT_DIR/Tools/ros2/install/ardupilot_msgs" ]]; then
    ok "ardupilot_msgs built"
else
    warn "ardupilot_msgs not built (needed for /ap/arm_motors and /ap/mode_switch)"
    echo "      cd $ARDUPILOT_DIR/Tools/ros2"
    echo "      colcon build --packages-select ardupilot_msgs"
fi

# ------------------------------------------------------------------ gazebo plugin
#
# Not required to exercise the DDS command path; required for the
# ArduPilot-authoritative Gazebo simulation that Milestone A ultimately needs.

if [[ -n "${GZ_SIM_SYSTEM_PLUGIN_PATH:-}" ]]; then
    ok "GZ_SIM_SYSTEM_PLUGIN_PATH set"
else
    warn "GZ_SIM_SYSTEM_PLUGIN_PATH is unset (ArduPilot Gazebo plugin not on the path)"
fi

echo
if (( FAILURES > 0 )); then
    echo "${RED}${FAILURES} required item(s) missing.${NC}"
    exit 1
fi
echo "${GREEN}All required items present.${NC}"

if [[ "$MODE" == "check" ]]; then
    exit 0
fi

# -------------------------------------------------------------------------- run
#
# No parameter file is passed. No validated SITL .param export exists yet; see
# ../README.md. Do not add one here by copying assumed defaults.

echo
echo "Start the XRCE agent in another terminal if it is not already running:"
echo "  MicroXRCEAgent udp4 -p 2019"
echo
echo "Starting Rover SITL (${SITL_TAG})..."
cd "$ARDUPILOT_DIR"
exec sim_vehicle.py -v Rover --enable-DDS --console --map
