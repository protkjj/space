"""Capture /slip while driving and plot the signature measurement."""
import sys
import time

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from space_msgs.msg import SlipEstimate

SECONDS = float(sys.argv[1]) if len(sys.argv) > 1 else 30.0
OUT = sys.argv[2] if len(sys.argv) > 2 else 'slip_trace.png'


class Cap(Node):
    def __init__(self):
        super().__init__('slip_capture')
        qos = QoSProfile(reliability=ReliabilityPolicy.RELIABLE,
                         history=HistoryPolicy.KEEP_LAST, depth=50)
        self.rows = []
        self.create_subscription(SlipEstimate, '/slip', self._cb, qos)

    def _cb(self, m):
        t = m.header.stamp.sec + m.header.stamp.nanosec * 1e-9
        self.rows.append((t, m.slip_ratio, m.v_wheel, m.v_actual,
                          1.0 if m.valid else 0.0, m.quality, m.source))


rclpy.init()
node = Cap()
t0 = time.time()
while time.time() - t0 < SECONDS:
    rclpy.spin_once(node, timeout_sec=0.2)
rows = np.array(node.rows) if node.rows else np.empty((0, 7))
node.destroy_node()
rclpy.shutdown()

print(f'samples {len(rows)}')
if not len(rows):
    sys.exit('no data')

t = rows[:, 0] - rows[0, 0]
lam, vw, va, valid, qual, src = (rows[:, i] for i in range(1, 7))
ok = valid > 0.5
print(f'valid {int(ok.sum())}/{len(rows)}   source={int(src[0])}  quality={qual[0]:.2f}')
if ok.any():
    good = lam[ok & np.isfinite(lam)]
    print(f'slip: min {good.min():+.4f}  median {np.median(good):+.4f}  max {good.max():+.4f}')

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6.5), dpi=200, sharex=True)

ax1.plot(t[ok], vw[ok], lw=1.6, color='#c0392b',
         label='V_wheel  (encoder, slip-contaminated)')
ax1.plot(t[ok], va[ok], lw=1.6, color='#1f4fd8',
         label='V_actual (wheel-independent, Gazebo ground truth)')
ax1.set_ylabel('forward speed [m/s]')
ax1.legend(fontsize=9, loc='upper right', framealpha=0.9)
ax1.grid(alpha=0.25, ls=':')
ax1.set_title('Wheel slip: the measurement only a rover on the terrain can make')

ax2.plot(t[ok], lam[ok] * 100.0, lw=1.8, color='#111')
ax2.axhline(15, ls='--', lw=1.2, color='#2e8b2e', label='SAFE boundary, 15% (CLAUDE.md 1.4)')
ax2.axhline(40, ls='--', lw=1.2, color='#c0392b', label='HAZARD boundary, 40%')
ax2.fill_between(t[ok], 0, 15, color='#2e8b2e', alpha=0.07)
ax2.fill_between(t[ok], 40, 100, color='#c0392b', alpha=0.07)
ax2.set_ylabel('slip ratio $\\lambda$ [%]')
ax2.set_xlabel('time [s]')
ax2.set_ylim(-5, 105)
ax2.legend(fontsize=9, loc='upper left', framealpha=0.9)
ax2.grid(alpha=0.25, ls=':')

fig.tight_layout()
fig.savefig(OUT)
print('wrote', OUT)
