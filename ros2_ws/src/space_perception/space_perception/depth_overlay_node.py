#!/usr/bin/env python3
"""Publish a camera image with depth cues for camera-only teleoperation."""

import math
from typing import Optional

import cv2
from cv_bridge import CvBridge
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import Image
from std_msgs.msg import Float32


class DepthOverlayNode(Node):
    def __init__(self):
        super().__init__('depth_overlay_node')

        self.declare_parameter('rgb_topic', '/camera/image_raw')
        self.declare_parameter('depth_topic', '/camera/depth_image_raw')
        self.declare_parameter('overlay_topic', '/camera/teleop_overlay')
        self.declare_parameter('nearest_topic', '/teleop/nearest_depth_m')
        self.declare_parameter('max_display_range_m', 5.0)

        self._bridge = CvBridge()
        self._latest_depth: Optional[np.ndarray] = None
        self._max_range = float(self.get_parameter('max_display_range_m').value)

        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )

        self._overlay_pub = self.create_publisher(
            Image, self.get_parameter('overlay_topic').value, 10
        )
        self._nearest_pub = self.create_publisher(
            Float32, self.get_parameter('nearest_topic').value, 10
        )

        self.create_subscription(
            Image, self.get_parameter('depth_topic').value, self._on_depth, qos
        )
        self.create_subscription(
            Image, self.get_parameter('rgb_topic').value, self._on_rgb, qos
        )

        self.get_logger().info('Depth overlay node started')

    def _on_depth(self, msg: Image):
        try:
            depth = self._bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')
        except Exception as exc:
            self.get_logger().warn(f'Could not decode depth image: {exc}')
            return
        self._latest_depth = np.asarray(depth)

    def _depth_meters(self, depth: np.ndarray) -> np.ndarray:
        depth = depth.astype(np.float32)
        if depth.size and np.nanmedian(depth) > 20.0:
            depth = depth / 1000.0
        return depth

    def _on_rgb(self, msg: Image):
        try:
            image = self._bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        except Exception as exc:
            self.get_logger().warn(f'Could not decode RGB image: {exc}')
            return

        h, w = image.shape[:2]
        overlay = image.copy()

        left = int(w * 0.35)
        right = int(w * 0.65)
        top = int(h * 0.40)
        bottom = int(h * 0.70)

        cv2.rectangle(overlay, (left, top), (right, bottom), (0, 220, 255), 2)
        cv2.line(overlay, (w // 2, 0), (w // 2, h), (255, 255, 255), 1)
        cv2.line(overlay, (0, h // 2), (w, h // 2), (255, 255, 255), 1)

        nearest = math.nan
        center_depth = math.nan

        if self._latest_depth is not None:
            depth = self._depth_meters(self._latest_depth)
            if depth.shape[:2] != (h, w):
                depth = cv2.resize(depth, (w, h), interpolation=cv2.INTER_NEAREST)

            valid = depth[np.isfinite(depth)]
            valid = valid[(valid > 0.05) & (valid < self._max_range)]
            if valid.size:
                nearest = float(np.percentile(valid, 5))

            center_roi = depth[top:bottom, left:right]
            center_valid = center_roi[np.isfinite(center_roi)]
            center_valid = center_valid[(center_valid > 0.05) & (center_valid < self._max_range)]
            if center_valid.size:
                center_depth = float(np.median(center_valid))

        color = (0, 255, 0)
        if math.isfinite(center_depth) and center_depth < 0.6:
            color = (0, 0, 255)
        elif math.isfinite(center_depth) and center_depth < 1.0:
            color = (0, 165, 255)

        cv2.rectangle(overlay, (0, 0), (w, 64), (0, 0, 0), -1)
        cv2.putText(
            overlay,
            f'CENTER {center_depth:.2f} m' if math.isfinite(center_depth) else 'CENTER --',
            (12, 26),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            color,
            2,
        )
        cv2.putText(
            overlay,
            f'NEAREST {nearest:.2f} m' if math.isfinite(nearest) else 'NEAREST --',
            (12, 54),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2,
        )

        self._nearest_pub.publish(Float32(data=nearest if math.isfinite(nearest) else -1.0))
        self._overlay_pub.publish(self._bridge.cv2_to_imgmsg(overlay, encoding='bgr8'))


def main(args=None):
    rclpy.init(args=args)
    node = DepthOverlayNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
