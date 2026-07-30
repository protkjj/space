#!/usr/bin/env python3
"""
Sample the arena from a grid of survey poses to build a coverage map.

WHY THIS IS NOT CHEATING, AND WHAT IT DOES SKIP
-----------------------------------------------
Every cell in the resulting map is produced by the real perception pipeline from
a real rendered depth image: the camera observes the terrain from each pose and
`terrain_pointcloud_filter -> local_elevation_map -> terrain_feature ->
terrain_traversability` runs unchanged. What is skipped is LOCOMOTION -- the
rover is placed at each pose instead of driving there.

That matters because this rover cannot actually traverse the whole arena: it
high-centres on the crater rims (30 mm chassis clearance against ~200 mm relief,
verified against the old collision box in docs/pending.md). A driven traverse
reaches ~1.1 m and 8.7% coverage. So a survey answers "what would the map look
like with coverage" while a driven run answers "how far can it get" -- two
different questions, and figures from this script must say which one they show.

Placement heights come from the CAD ground-truth grid, not a fixed number: the
rover is set 0.10 m above the local surface so it settles onto terrain instead of
being dropped inside it. Poses where it ends up tipped are counted and reported
rather than quietly averaged in.
"""
import argparse
import math
import subprocess
import sys
import time

import numpy as np
import rclpy
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy


def set_pose(world, name, x, y, z, yaw):
    """Place the model, returning True when Gazebo acknowledges."""
    req = (f'name: "{name}", position: {{x: {x}, y: {y}, z: {z}}}, '
           f'orientation: {{x: 0, y: 0, z: {math.sin(yaw / 2.0)}, '
           f'w: {math.cos(yaw / 2.0)}}}')
    out = subprocess.run(
        ['gz', 'service', '-s', f'/world/{world}/set_pose',
         '--reqtype', 'gz.msgs.Pose', '--reptype', 'gz.msgs.Boolean',
         '--timeout', '4000', '--req', req],
        capture_output=True, text=True,
    )
    return 'true' in out.stdout


class Attitude(Node):
    """Read back where the rover actually settled."""

    def __init__(self):
        super().__init__('survey_attitude')
        qos = QoSProfile(reliability=ReliabilityPolicy.BEST_EFFORT,
                         history=HistoryPolicy.KEEP_LAST, depth=1)
        self.latest = None
        self.create_subscription(Odometry, '/odom', self._cb, qos)

    def _cb(self, msg):
        q = msg.pose.pose.orientation
        p = msg.pose.pose.position
        pitch = math.degrees(math.asin(
            max(-1.0, min(1.0, 2.0 * (q.w * q.y - q.z * q.x)))))
        roll = math.degrees(math.atan2(
            2.0 * (q.w * q.x + q.y * q.z), 1.0 - 2.0 * (q.x * q.x + q.y * q.y)))
        self.latest = (p.x, p.y, p.z, pitch, roll)

    def wait(self, seconds):
        """Spin for `seconds` and return the last attitude seen."""
        end = time.time() + seconds
        while time.time() < end:
            rclpy.spin_once(self, timeout_sec=0.1)
        return self.latest


def surface_height(truth, x, y):
    """Return the CAD surface height at (x, y), or None outside the grid."""
    res = float(truth['resolution'])
    ix = int((x - float(truth['min_x'])) / res)
    iy = int((y - float(truth['min_y'])) / res)
    if not (0 <= ix < int(truth['nx']) and 0 <= iy < int(truth['ny'])):
        return None
    value = truth['elevation'][iy, ix]
    return None if not np.isfinite(value) else float(value)


def main(argv=None):
    """Walk a grid of poses, pausing at each for the pipeline to observe."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--truth', required=True)
    parser.add_argument('--world', default='arena_terrain_v04')
    parser.add_argument('--model', default='space_rover')
    parser.add_argument('--spacing', type=float, default=0.8)
    parser.add_argument('--margin', type=float, default=0.45,
                        help='keep poses this far inside the arena edge')
    parser.add_argument('--yaws', type=int, default=4)
    parser.add_argument('--settle', type=float, default=1.2)
    parser.add_argument('--observe', type=float, default=1.0)
    parser.add_argument('--clearance', type=float, default=0.10)
    parser.add_argument('--max-tilt', type=float, default=25.0)
    args = parser.parse_args(argv)

    truth = np.load(args.truth)
    res = float(truth['resolution'])
    min_x, min_y = float(truth['min_x']), float(truth['min_y'])
    max_x = min_x + int(truth['nx']) * res
    max_y = min_y + int(truth['ny']) * res

    xs = np.arange(min_x + args.margin, max_x - args.margin, args.spacing)
    ys = np.arange(min_y + args.margin, max_y - args.margin, args.spacing)
    yaws = [2.0 * math.pi * i / args.yaws for i in range(args.yaws)]
    print(f'arena x {min_x:+.2f}..{max_x:+.2f}  y {min_y:+.2f}..{max_y:+.2f}')
    print(f'{len(xs)} x {len(ys)} poses x {len(yaws)} yaws = '
          f'{len(xs) * len(ys) * len(yaws)} samples, '
          f'~{len(xs) * len(ys) * len(yaws) * (args.settle + args.observe) / 60.0:.1f} min')

    rclpy.init()
    att = Attitude()
    placed = tipped = skipped = 0
    try:
        for iy, y in enumerate(ys):
            # Serpentine so consecutive poses are adjacent, which keeps the
            # settle transient small.
            row = xs if iy % 2 == 0 else xs[::-1]
            for x in row:
                height = surface_height(truth, x, y)
                if height is None:
                    skipped += 1
                    continue
                for yaw in yaws:
                    if not set_pose(args.world, args.model, float(x), float(y),
                                    height + args.clearance, yaw):
                        skipped += 1
                        continue
                    state = att.wait(args.settle)
                    if state is None:
                        skipped += 1
                        continue
                    if max(abs(state[3]), abs(state[4])) > args.max_tilt:
                        tipped += 1
                    att.wait(args.observe)
                    placed += 1
            print(f'  row y={y:+.2f} done  placed {placed}  tipped {tipped}  '
                  f'skipped {skipped}', flush=True)
    finally:
        att.destroy_node()
        rclpy.shutdown()

    print(f'placed {placed}, of which tipped beyond {args.max_tilt} deg: '
          f'{tipped} ({100.0 * tipped / max(placed, 1):.0f}%)')
    print(f'skipped {skipped}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
