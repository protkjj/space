"""Capture the traversability cloud and render a top-down map as PNG."""
import struct
import sys
import time

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import PointCloud2
from nav_msgs.msg import Odometry

TOPIC = sys.argv[1] if len(sys.argv) > 1 else '/terrain/traversability'
SECONDS = float(sys.argv[2]) if len(sys.argv) > 2 else 20.0
OUT = sys.argv[3] if len(sys.argv) > 3 else 'traversability_map.png'


def unpack(msg):
    step = msg.point_step
    data = msg.data
    off = {f.name: f.offset for f in msg.fields}
    n = msg.width * msg.height
    rows = []
    for i in range(n):
        b = i * step
        x, y, z, trav = struct.unpack_from('<4f', data, b + off['x'])
        slope, rough, stepp, unc = struct.unpack_from('<4f', data, b + off['slope_penalty'])
        valid = struct.unpack_from('<B', data, b + off['valid'])[0]
        limit = struct.unpack_from('<B', data, b + off['limiting_factor'])[0]
        rows.append((x, y, z, trav, slope, rough, stepp, unc, valid, limit))
    return rows


class Cap(Node):
    def __init__(self):
        super().__init__('map_capture')
        qos = QoSProfile(reliability=ReliabilityPolicy.BEST_EFFORT,
                         history=HistoryPolicy.KEEP_LAST, depth=5)
        self.rows = []
        self.path = []
        self.frame = ''
        self.msgs = 0
        self.create_subscription(PointCloud2, TOPIC, self._cb, qos)
        self.create_subscription(Odometry, '/odom', self._odom, qos)

    def _cb(self, msg):
        self.frame = msg.header.frame_id
        self.msgs += 1
        self.rows.extend(unpack(msg))

    def _odom(self, msg):
        p = msg.pose.pose.position
        self.path.append((p.x, p.y))


rclpy.init()
node = Cap()
t0 = time.time()
while time.time() - t0 < SECONDS:
    rclpy.spin_once(node, timeout_sec=0.2)
rows = np.array(node.rows) if node.rows else np.empty((0, 10))
path = np.array(node.path) if node.path else np.empty((0, 2))
frame = node.frame
msgs = node.msgs
node.destroy_node()
rclpy.shutdown()

print(f'messages {msgs}, points {len(rows)}, frame {frame!r}, odom samples {len(path)}')
if not len(rows):
    sys.exit('no data captured')

valid = rows[:, 8] > 0
v = rows[valid]
print(f'valid {len(v)} / {len(rows)}')
if not len(v):
    sys.exit('no valid cells')
print(f'traversability  min {v[:,3].min():.3f}  median {np.median(v[:,3]):.3f}  max {v[:,3].max():.3f}')
for i, name in ((4, 'slope'), (5, 'roughness'), (6, 'step'), (7, 'uncertainty')):
    print(f'  {name:12s} penalty  median {np.median(v[:,i]):.4f}  max {v[:,i].max():.4f}')
lim, cnt = np.unique(v[:, 9].astype(int), return_counts=True)
print('limiting factor counts:', dict(zip(lim.tolist(), cnt.tolist())))

fig, ax = plt.subplots(figsize=(9, 7), dpi=140)
sc = ax.scatter(v[:, 0], v[:, 1], c=v[:, 3], s=7, cmap='RdYlGn',
                vmin=0.6, vmax=1.0, marker='s', linewidths=0)
if len(path):
    ax.plot(path[:, 0], path[:, 1], '-', color='#1f4fd8', lw=1.8,
            label='rover path (/odom)')
    ax.plot(path[0, 0], path[0, 1], 'o', color='#1f4fd8', ms=7, label='start')
    ax.plot(path[-1, 0], path[-1, 1], '*', color='#111', ms=15, label='end')
    ax.legend(loc='upper left', fontsize=9, framealpha=0.9)
cb = fig.colorbar(sc, ax=ax)
cb.set_label('traversability score (higher = easier)')
ax.set_xlabel('x [m]')
ax.set_ylabel('y [m]')
ax.set_title(f'Geometric traversability, arena_terrain_v04\n'
             f'{len(v)} valid cells from {msgs} frames, frame "{frame}"')
ax.set_aspect('equal')
ax.grid(alpha=0.25, ls=':')
fig.tight_layout()
fig.savefig(OUT)
print('wrote', OUT)
