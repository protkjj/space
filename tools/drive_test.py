"""Drive forward at a fixed speed and report how far the rover actually got."""
import math
import sys
import time

import rclpy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy

DUR = float(sys.argv[1]) if len(sys.argv) > 1 else 25.0
SPEED = float(sys.argv[2]) if len(sys.argv) > 2 else 0.10

qos = QoSProfile(reliability=ReliabilityPolicy.BEST_EFFORT,
                 history=HistoryPolicy.KEEP_LAST, depth=1)
rclpy.init()
node = Node('drive_test')
pub = node.create_publisher(Twist, '/cmd_vel_in', 10)
samples = []


def cb(msg):
    p = msg.pose.pose.position
    q = msg.pose.pose.orientation
    pitch = math.degrees(math.asin(max(-1.0, min(1.0, 2 * (q.w * q.y - q.z * q.x)))))
    samples.append((p.x, p.y, p.z, pitch))


node.create_subscription(Odometry, '/odom', cb, qos)
cmd = Twist()
cmd.linear.x = SPEED
t0 = time.time()
while time.time() - t0 < DUR:
    pub.publish(cmd)
    rclpy.spin_once(node, timeout_sec=0.05)
pub.publish(Twist())
for _ in range(10):
    rclpy.spin_once(node, timeout_sec=0.05)

if samples:
    x0, y0 = samples[0][0], samples[0][1]
    xn, yn, zn, pn = samples[-1]
    # furthest point reached, not just the final one
    far = max(math.hypot(s[0] - x0, s[1] - y0) for s in samples)
    print(f'  travelled {math.hypot(xn - x0, yn - y0):.3f} m  '
          f'furthest {far:.3f} m  end ({xn:+.3f},{yn:+.3f},{zn:+.3f})  '
          f'pitch {pn:+.1f} deg  samples {len(samples)}')
else:
    print('  no odom')
node.destroy_node()
rclpy.shutdown()
