#!/usr/bin/env python3
"""Transform, crop, and voxel-filter measured terrain point clouds."""

from copy import deepcopy
import time

from diagnostic_msgs.msg import DiagnosticArray, DiagnosticStatus, KeyValue
import numpy as np
import rclpy
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from rclpy.time import Time
from sensor_msgs.msg import PointCloud2

from space_perception.pointcloud_utils import (
    cloud_xyz_numpy,
    create_xyz_cloud,
    transform_to_matrix,
)
from space_perception.terrain_processing import filter_terrain_points
from std_msgs.msg import Header
from tf2_ros import Buffer, TransformException, TransformListener


class TerrainPointcloudFilterNode(Node):
    """Rate-limited, vectorized terrain point-cloud filter."""

    def __init__(self):
        super().__init__('terrain_pointcloud_filter_node')
        defaults = {
            'input_topic': '/camera/points',
            'output_topic': '/terrain/filtered_points',
            'target_frame': 'odom',
            'base_frame': 'base_footprint',
            'publish_rate': 5.0,
            'voxel_size': 0.03,
            'min_range': 0.15,
            'max_range': 4.0,
            'crop_min_x': 0.10,
            'crop_max_x': 3.60,
            'crop_min_y': -2.0,
            'crop_max_y': 2.0,
            'crop_min_z': -0.60,
            'crop_max_z': 1.20,
            'remove_rover_body': True,
            'rover_exclusion_min_x': -0.25,
            'rover_exclusion_max_x': 0.30,
            'rover_exclusion_min_y': -0.25,
            'rover_exclusion_max_y': 0.25,
            'rover_exclusion_min_z': -0.15,
            'rover_exclusion_max_z': 0.35,
        }
        for name, value in defaults.items():
            self.declare_parameter(name, value)
        self._target = self.get_parameter('target_frame').value
        self._base = self.get_parameter('base_frame').value
        rate = float(self.get_parameter('publish_rate').value)
        if rate <= 0.0:
            raise ValueError('publish_rate must be greater than zero')
        self._tf_buffer = Buffer()
        self._tf_listener = TransformListener(self._tf_buffer, self)
        sensor_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )
        self._publisher = self.create_publisher(
            PointCloud2, self.get_parameter('output_topic').value, sensor_qos
        )
        self._diagnostics = self.create_publisher(
            DiagnosticArray, '/terrain/diagnostics', 10
        )
        self.create_subscription(
            PointCloud2,
            self.get_parameter('input_topic').value,
            self._cloud_callback,
            sensor_qos,
        )
        self._latest = None
        self._last_stamp = None
        self._last_warning_wall = 0.0
        self._last_log_wall = time.monotonic()
        self._started_wall = time.monotonic()
        self._processed = 0
        self._raw_count = 0
        self._valid_count = 0
        self._filtered_count = 0
        self._duration_ms = 0.0
        self._tf_available = False
        self.create_timer(1.0 / rate, self._process_latest)
        self.get_logger().info(
            f'Filtering {self.get_parameter("input_topic").value} into '
            f'{self._target} at up to {rate:.1f} Hz'
        )

    def _cloud_callback(self, message):
        self._latest = message

    def _warn_tf(self, message):
        now = time.monotonic()
        if now - self._last_warning_wall >= 5.0:
            self.get_logger().warning(f'Terrain cloud TF unavailable: {message}')
            self._last_warning_wall = now

    def _lookup_matrix(self, target, source, stamp):
        if target == source:
            return np.eye(4, dtype=np.float64)
        transform = self._tf_buffer.lookup_transform(
            target, source, stamp, timeout=Duration(seconds=0.05)
        )
        return transform_to_matrix(transform.transform)

    def _process_latest(self):
        message = self._latest
        if message is None:
            self._publish_diagnostics(False)
            return
        stamp_key = (message.header.stamp.sec, message.header.stamp.nanosec)
        if stamp_key == self._last_stamp:
            return
        started = time.perf_counter()
        try:
            stamp = Time.from_msg(message.header.stamp)
            target_from_sensor = self._lookup_matrix(
                self._target, message.header.frame_id, stamp
            )
            base_from_target = self._lookup_matrix(
                self._base, self._target, stamp
            )
            self._tf_available = True
        except (TransformException, ValueError) as error:
            self._tf_available = False
            self._warn_tf(error)
            self._publish_diagnostics(True)
            return

        points = cloud_xyz_numpy(message)
        self._raw_count = len(points)
        filtered, self._valid_count = filter_terrain_points(
            points,
            target_from_sensor,
            base_from_target,
            min_range=float(self.get_parameter('min_range').value),
            max_range=float(self.get_parameter('max_range').value),
            crop_min=np.array([
                self.get_parameter('crop_min_x').value,
                self.get_parameter('crop_min_y').value,
                self.get_parameter('crop_min_z').value,
            ]),
            crop_max=np.array([
                self.get_parameter('crop_max_x').value,
                self.get_parameter('crop_max_y').value,
                self.get_parameter('crop_max_z').value,
            ]),
            remove_rover_body=bool(
                self.get_parameter('remove_rover_body').value
            ),
            exclusion_min=np.array([
                self.get_parameter('rover_exclusion_min_x').value,
                self.get_parameter('rover_exclusion_min_y').value,
                self.get_parameter('rover_exclusion_min_z').value,
            ]),
            exclusion_max=np.array([
                self.get_parameter('rover_exclusion_max_x').value,
                self.get_parameter('rover_exclusion_max_y').value,
                self.get_parameter('rover_exclusion_max_z').value,
            ]),
            voxel_size=float(self.get_parameter('voxel_size').value),
        )
        header = Header(
            stamp=deepcopy(message.header.stamp), frame_id=self._target
        )
        self._publisher.publish(create_xyz_cloud(header, filtered))
        self._filtered_count = len(filtered)
        self._duration_ms = (time.perf_counter() - started) * 1000.0
        self._processed += 1
        self._last_stamp = stamp_key
        self._publish_diagnostics(True)
        now = time.monotonic()
        if now - self._last_log_wall >= 5.0:
            rate = self._processed / max(now - self._started_wall, 1e-9)
            self.get_logger().info(
                f'cloud raw={self._raw_count} valid={self._valid_count} '
                f'filtered={self._filtered_count} '
                f'processing={self._duration_ms:.2f} ms rate={rate:.2f} Hz'
            )
            self._last_log_wall = now

    def _publish_diagnostics(self, input_received):
        now = self.get_clock().now()
        age = -1.0
        if self._latest is not None:
            cloud_time = Time.from_msg(self._latest.header.stamp)
            age = max(0.0, (now - cloud_time).nanoseconds / 1e9)
        elapsed = max(time.monotonic() - self._started_wall, 1e-9)
        values = {
            'input_cloud_received': input_received,
            'tf_available': self._tf_available,
            'last_cloud_age_sec': f'{age:.3f}',
            'raw_point_count': self._raw_count,
            'valid_point_count': self._valid_count,
            'filtered_point_count': self._filtered_count,
            'processing_duration_ms': f'{self._duration_ms:.3f}',
            'processing_rate_hz': f'{self._processed / elapsed:.3f}',
        }
        status = DiagnosticStatus(
            level=(
                DiagnosticStatus.OK
                if input_received and self._tf_available
                else DiagnosticStatus.WARN
            ),
            name='terrain_pointcloud_filter',
            message='processing' if self._tf_available else 'waiting for data/TF',
            values=[
                KeyValue(key=key, value=str(value))
                for key, value in values.items()
            ],
        )
        self._diagnostics.publish(
            DiagnosticArray(header=Header(stamp=now.to_msg()), status=[status])
        )


def main(args=None):
    rclpy.init(args=args)
    node = TerrainPointcloudFilterNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
