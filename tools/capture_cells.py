#!/usr/bin/env python3
"""
Capture measured terrain cells to an .npz for offline rendering.

Kept separate from rendering so a single drive can feed several figures without
re-running the simulation.
"""
import struct
import sys
import time

import numpy as np
import rclpy
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import PointCloud2

TOPIC = sys.argv[1] if len(sys.argv) > 1 else '/terrain/traversability'
SECONDS = float(sys.argv[2]) if len(sys.argv) > 2 else 30.0
OUT = sys.argv[3] if len(sys.argv) > 3 else 'measured_cells.npz'

FIELDS = ('x', 'y', 'z', 'traversability', 'slope_penalty',
          'roughness_penalty', 'step_penalty', 'uncertainty_penalty',
          'confidence')


class Cap(Node):
    """Accumulate every cell the pipeline emits, plus the rover path."""

    def __init__(self):
        super().__init__('cell_capture')
        qos = QoSProfile(reliability=ReliabilityPolicy.BEST_EFFORT,
                         history=HistoryPolicy.KEEP_LAST, depth=5)
        self.rows = []
        self.path = []
        self.frames = 0
        self.create_subscription(PointCloud2, TOPIC, self._cloud, qos)
        self.create_subscription(Odometry, '/odom', self._odom, qos)

    def _cloud(self, msg):
        self.frames += 1
        off = {f.name: f.offset for f in msg.fields}
        step = msg.point_step
        for i in range(msg.width * msg.height):
            base = i * step
            vals = [
                struct.unpack_from('<f', msg.data, base + off[name])[0]
                for name in FIELDS
            ]
            valid = struct.unpack_from('<B', msg.data, base + off['valid'])[0]
            limit = struct.unpack_from(
                '<B', msg.data, base + off['limiting_factor']
            )[0]
            self.rows.append(vals + [float(valid), float(limit)])

    def _odom(self, msg):
        p = msg.pose.pose.position
        self.path.append((p.x, p.y, p.z))


def main():
    """Capture for SECONDS and write the npz."""
    rclpy.init()
    node = Cap()
    start = time.time()
    while time.time() - start < SECONDS:
        rclpy.spin_once(node, timeout_sec=0.2)
    rows = np.array(node.rows) if node.rows else np.empty((0, 11))
    path = np.array(node.path) if node.path else np.empty((0, 3))
    frames = node.frames
    node.destroy_node()
    rclpy.shutdown()

    print(f'frames {frames}  cells {len(rows)}  odom {len(path)}')
    if not len(rows):
        sys.exit('no cells captured')
    valid = rows[:, 9] > 0.5
    print(f'valid {int(valid.sum())} / {len(rows)}')
    np.savez_compressed(
        OUT, rows=rows, path=path, frames=frames,
        columns=np.array(FIELDS + ('valid', 'limiting_factor')),
    )
    print(f'wrote {OUT}')


if __name__ == '__main__':
    main()
