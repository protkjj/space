# Sensors

## OAK-D Pro W

A Luxonis OAK-D Pro W is the intended source for depth perception, and
possibly later for visual-inertial odometry. The unit exists and has been
detected on the Jetson; nothing beyond that has been validated.

### Read off the unit

`probe_oak_d.py` was run against the device on the Jetson and its output is in
`oak_d_calibration.json`:

| | |
| --- | --- |
| Model | OAK-D-PRO-W-97, RVC2, device id `19443010F1B62D7E00` |
| IMU | **BNO086** |
| Cameras | CAM_A OV9782 (colour), CAM_B and CAM_C OV9282, all 1280x800 |
| Stereo baseline | 7.500 cm |
| Field of view | 127 degrees, the wide variant |
| Link | **USB 2.0 (HIGH)**, not SuperSpeed |

The camera-to-IMU translations are self-consistent: CAM_C is at -0.01 cm and
CAM_B at -7.57 cm, a 7.56 cm separation that agrees with the 7.500 cm baseline
reported independently, and CAM_A sits between them at -3.79 cm. Two values
that were not derived from each other agree, which is the kind of check worth
doing before trusting a calibration.

### The distortion model is not plumb_bob

The device reports `CameraModel.Perspective` but supplies **fourteen**
distortion coefficients for every camera, with a large k1 (4.19, 6.82, 7.87).
That is OpenCV's full rational plus thin-prism plus tilt model:
k1 k2 p1 p2 k3 k4 k5 k6 s1 s2 s3 s4 tx ty.

`sensor_msgs/msg/CameraInfo`'s usual `plumb_bob` model carries five. Taking the
first five and calling it plumb_bob would discard k4-k6, which on a 127 degree
lens is not a rounding error: it shows up later as depth that curves at the
edges of the frame. A camera node must declare `rational_polynomial` and pass
the first eight, or handle all fourteen.

Whether the remaining six are near enough to zero to drop has **not** been
checked yet.

### Not established

- achievable frame rate over the link actually in use
- whether `depthai-ros` has a usable ROS 2 Jazzy release
- whether the camera is mounted, and at what transform from `base_link`
- whether the six thin-prism and tilt coefficients are negligible

### The link is running at USB 2

The device reports `UsbSpeed.HIGH`, and on the Jetson the 10 Gbps bus is empty
while the camera sits on the 480 Mbps one. Calibration reads fine either way,
but stereo at 1280x800 plus IMU does not fit comfortably in 480 Mbps, so
resolution or rate would have to be cut.

The usual cause is the cable: an OAK-D needs a USB3 cable to negotiate
SuperSpeed, and a USB2 cable in a USB3 port still enumerates at HIGH. Worth
swapping before building anything on top of the current bandwidth, since the
ceiling roughly quintuples if it is only the cable.

## Visual-inertial odometry

`depthai` 3.8.0 ships VIO in the stock wheel. Verified on the development
laptop against the installed package, without a camera attached:

```text
dai.node.BasaltVIO      inputs left, right, imu   output transform
dai.node.RTABMapVIO     input depth               output transform
dai.node.RTABMapSLAM
```

`BasaltVIO.transform` carries `dai.TransformData`, which offers
`getTranslation()` and `getQuaternion()` — the two things `extnav_publisher`
already needs to publish `/ap/tf`. The node also exposes `setImuExtrinsics`,
which is where the camera-to-IMU transform above belongs, and
`setLocalTransform` for the camera-to-body transform.

So VIO here is a wiring problem rather than an implementation one. That is a
much better starting position than writing an estimator, and it is worth
saying plainly that **it has not been run**: a host-only pipeline proves these
nodes construct, and construction does not prove they produce a pose on this
unit at a usable rate.

`XLinkOut` no longer exists in 3.x (`hasattr` returns False), and device nodes
cannot be created in a host-only pipeline, so the device half of any pipeline
can only be checked with the camera present.

### Isaac ROS is not an option on this Jetson

NVIDIA's cuVSLAM ships in Isaac ROS 4.x, which is the Jazzy line and requires
Jetson Thor, x86_64, or DGX Spark. Orin's supported path remains Isaac ROS 3.2
on JetPack 6 with Humble. The camera is not the obstacle; the platform is.

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
