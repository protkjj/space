# Isaac Sim Setup

This repo can generate a SPACE rover URDF from the ROS 2 xacro and import it
into an Isaac Sim USD stage with two test lanes:

- normal friction lane
- low-friction lane for salt-like low-traction patches

## Local Install

This machine currently has Isaac Sim under:

```bash
/home/kj/IsaacSim/isaacsim
```

Override the path when needed:

```bash
export ISAACSIM_ROOT=/path/to/isaacsim
```

## Check Environment

```bash
tools/isaac/check_env.sh
```

Expected baseline:

- Ubuntu 24.04
- ROS 2 Jazzy
- NVIDIA RTX GPU and current driver
- Isaac Sim `python.sh` and `isaac-sim.sh`

## Generate URDF

```bash
tools/isaac/generate_space_rover_urdf.sh
```

Default output:

```bash
ros2_ws/build/isaac/space_rover.urdf
```

## Import Rover Into Isaac USD

```bash
tools/isaac/run_space_rover_import.sh
```

Default output:

```bash
ros2_ws/build/isaac/space_rover_friction_test.usd
```

Open the generated stage:

```bash
/home/kj/IsaacSim/isaacsim/isaac-sim.sh ros2_ws/build/isaac/space_rover_friction_test.usd
```

For GUI import instead of headless import:

```bash
tools/isaac/run_space_rover_import.sh --gui
```

Enable the Isaac ROS 2 bridge extension during import:

```bash
tools/isaac/run_space_rover_import.sh --enable-ros2-bridge
```

## Notes

The generated USD is a first Isaac Sim migration target. It imports geometry,
inertias, joints, fixed camera frames, and creates low-friction terrain patches.
The next step is to replace the Gazebo DiffDrive path with Isaac-side wheel
joint drive control and ROS 2 bridge topics.

