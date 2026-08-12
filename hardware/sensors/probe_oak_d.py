#!/usr/bin/env python3
"""
Read an OAK-D's own calibration and report what it says.

Every camera node needs intrinsics, a baseline, distortion coefficients and a
camera-to-IMU transform. Those are per-unit values burned into the device's
EEPROM at the factory, not properties of the model, so they cannot be taken
from a datasheet and must not be guessed. This reads them off the device that
will actually be used and writes them where the rest of the repository can
refer to them.

**Read-only.** It opens the device, reads calibration and device identity, and
closes. It does not flash, reset, or modify calibration, and it never starts a
pipeline.

Written against depthai 3.8.0. The 3.x API is not compatible with 2.x, so
examples found for 2.x will not run here.

Usage::

    ./probe_oak_d.py
    ./probe_oak_d.py --json hardware/sensors/oak_d_calibration.json
"""

import argparse
import json
import sys

try:
    import depthai as dai
except ImportError:
    sys.exit(
        'depthai is not installed.\n'
        '  python3 -m pip install --user --break-system-packages depthai'
    )


def parse_args():
    """Return parsed command-line options."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--json',
        help='write the calibration to this path so it can be committed')
    return parser.parse_args()


def report_identity(device):
    """Print what the device says it is, and return it as a dict."""
    print('--- device ---')
    identity = {}
    for label, getter in (
        ('name', 'getDeviceName'),
        ('product', 'getProductName'),
        ('platform', 'getPlatformAsString'),
        ('device_id', 'getDeviceId'),
    ):
        try:
            value = getattr(device, getter)()
            identity[label] = str(value)
            print(f'  {label:12s} {value}')
        except Exception as exc:
            print(f'  {label:12s} unavailable: {exc}')

    try:
        speed = device.getUsbSpeed()
        identity['usb_speed'] = str(speed)
        print(f'  {"usb_speed":12s} {speed}')
        if 'SUPER' not in str(speed).upper():
            print('    NOTE: not USB3. Bandwidth limits resolution and rate.')
    except Exception as exc:
        print(f'  {"usb_speed":12s} unavailable: {exc}')

    return identity


def report_cameras(device):
    """Print the connected image sensors, and return them as a list."""
    print('\n--- connected cameras ---')
    cameras = []
    try:
        features = device.getConnectedCameraFeatures()
    except Exception as exc:
        print(f'  could not enumerate: {exc}')
        return cameras

    for feature in features:
        entry = {
            'socket': str(feature.socket),
            'sensor': getattr(feature, 'sensorName', ''),
            'width': getattr(feature, 'width', None),
            'height': getattr(feature, 'height', None),
        }
        # Which sockets carry the stereo pair is a per-board fact, and the
        # camera node has to address them by socket rather than by guess.
        print(f'  {entry["socket"]:28s} {entry["sensor"]:12s} '
              f'{entry["width"]}x{entry["height"]}')
        cameras.append(entry)
    return cameras


def report_imu(device):
    """Print the IMU the board reports, if it has one."""
    print('\n--- imu ---')
    try:
        imu = device.getConnectedIMU()
    except Exception as exc:
        print(f'  unavailable: {exc}')
        return ''
    if not imu:
        print('  none reported. Visual-inertial odometry is not possible '
              'on this unit.')
        return ''
    print(f'  {imu}')
    return str(imu)


def socket_for(name):
    """Return the CameraBoardSocket enum member for a socket name."""
    return getattr(dai.CameraBoardSocket, name, None)


def report_calibration(device, cameras):
    """Read the factory calibration and return it as a dict."""
    print('\n--- calibration ---')
    try:
        calib = device.getCalibration()
    except Exception as exc:
        print(f'  could not read calibration: {exc}')
        print('  Without this the camera node has no intrinsics, and '
              'intrinsics must not be invented.')
        return {}

    result = {'cameras': {}}

    for entry in cameras:
        # str(socket) prints as 'CameraBoardSocket.CAM_B'; take the member.
        name = entry['socket'].rsplit('.', 1)[-1]
        socket = socket_for(name)
        if socket is None:
            print(f'  {name}: not a recognised socket, skipping')
            continue

        record = {}
        print(f'\n  [{name}] {entry["sensor"]}')

        try:
            width = entry.get('width')
            height = entry.get('height')
            if width and height:
                intrinsics = calib.getCameraIntrinsics(socket, width, height)
                record['resolution'] = [width, height]
            else:
                intrinsics = calib.getCameraIntrinsics(socket)
            record['intrinsics'] = [list(row) for row in intrinsics]
            fx = intrinsics[0][0]
            fy = intrinsics[1][1]
            cx = intrinsics[0][2]
            cy = intrinsics[1][2]
            res = record.get('resolution')
            suffix = f' at {res[0]}x{res[1]}' if res else ''
            print(f'    fx {fx:.2f}  fy {fy:.2f}  '
                  f'cx {cx:.2f}  cy {cy:.2f}{suffix}')
        except Exception as exc:
            print(f'    intrinsics unavailable: {exc}')

        try:
            model = calib.getDistortionModel(socket)
            coeffs = calib.getDistortionCoefficients(socket)
            record['distortion_model'] = str(model)
            record['distortion'] = list(coeffs)
            shown = ', '.join(f'{c:.5f}' for c in coeffs[:8])
            print(f'    distortion {model}: {shown}')
            if len(coeffs) > 8:
                print(f'      (+{len(coeffs) - 8} more coefficients)')
        except Exception as exc:
            print(f'    distortion unavailable: {exc}')

        try:
            fov = calib.getFov(socket)
            record['fov_deg'] = fov
            print(f'    horizontal fov {fov:.1f} deg')
        except Exception as exc:
            print(f'    fov unavailable: {exc}')

        try:
            # The transform from this camera to the IMU is what a
            # visual-inertial estimator needs; without it the two streams
            # cannot be placed in a common frame.
            extrinsics = calib.getCameraToImuExtrinsics(socket)
            record['camera_to_imu'] = [list(row) for row in extrinsics]
            translation = [extrinsics[i][3] for i in range(3)]
            pretty = ', '.join(f'{v:.2f}' for v in translation)
            print(f'    camera->imu translation (cm): {pretty}')
        except Exception as exc:
            print(f'    camera->imu unavailable: {exc}')

        result['cameras'][name] = record

    try:
        # The default arguments name the stereo pair for this board, so the
        # baseline comes back without having to assert which sockets they are.
        baseline_cm = calib.getBaselineDistance()
        result['baseline_cm'] = baseline_cm
        print(f'\n  stereo baseline: {baseline_cm:.3f} cm '
              f'({baseline_cm / 100.0:.5f} m)')
    except Exception as exc:
        print(f'\n  baseline unavailable: {exc}')

    return result


def main():
    """Read one OAK-D's calibration and report it."""
    args = parse_args()

    print('Searching for a device...')
    try:
        device = dai.Device()
    except Exception as exc:
        print(f'could not open a device: {exc}')
        print('\nCheck that the camera is plugged in, and that the udev rules')
        print('are installed. Without a device this reports nothing, which is')
        print('the correct outcome: these values cannot be guessed.')
        return 1

    try:
        identity = report_identity(device)
        cameras = report_cameras(device)
        imu = report_imu(device)
        calibration = report_calibration(device, cameras)
    finally:
        try:
            device.close()
        except Exception:
            pass

    if args.json:
        payload = {
            'depthai_version': dai.__version__,
            'device': identity,
            'cameras': cameras,
            'imu': imu,
            'calibration': calibration,
        }
        with open(args.json, 'w') as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write('\n')
        print(f'\nwrote {args.json}')

    print('\n' + '=' * 58)
    print('These are this unit\'s own values. Any camera node should read')
    print('them from the device or from the file written here, rather than')
    print('carrying numbers copied from a datasheet.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
