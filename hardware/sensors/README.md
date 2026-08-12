# Sensors

## OAK-D Pro W

A Luxonis OAK-D Pro W is the intended source for depth perception, and
possibly later for visual-inertial odometry. The unit exists and has been
detected on the Jetson; nothing beyond that has been validated.

### Established

| Fact | How it is known |
| --- | --- |
| The unit is present and enumerates on the Jetson | observed |
| Stereo pair uses OV9282 global-shutter sensors | reported by the device |
| USB2 is acceptable for 640x400 at 30 fps | judged sufficient for the intended use, not measured |
| `depthai` 3.8.0 is installed on the Jetson and on the development laptop | `depthai.__version__` |

### Not established

- the unit's own intrinsics, distortion coefficients, baseline, and
  camera-to-IMU transform
- achievable frame rate over the link actually in use
- whether `depthai-ros` has a usable ROS 2 Jazzy release
- whether the camera is mounted, and at what transform from `base_link`

None of these may be filled in from a datasheet. Calibration in particular is
per-unit and burned into the device at the factory, so a figure copied from
the product page is not this camera's figure.

### DepthAI 3.x is not 2.x

Version 3 broke the Python API. Pipelines are built with `pipeline.create(...)`
and started with `pipeline.start()`; the `XLinkOut` plumbing that appears in
almost every tutorial online belongs to 2.x and will not run here. Node types
live under `depthai.node.*`. Verify any example against the installed version
before adapting it.

### Reading the calibration

`probe_oak_d.py` reads the device's own calibration and prints it, and with
`--json` writes it where it can be committed and referenced:

```sh
./hardware/sensors/probe_oak_d.py --json hardware/sensors/oak_d_calibration.json
```

It is read-only: it opens the device, reads identity and calibration, and
closes. It never flashes, resets, or starts a pipeline.
