#!/usr/bin/env python3
"""Build a measured, rover-centred local elevation grid."""

from copy import deepcopy
import time

from diagnostic_msgs.msg import DiagnosticArray, DiagnosticStatus, KeyValue
from geometry_msgs.msg import Point
import numpy as np
import rclpy
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from rclpy.time import Time
from sensor_msgs.msg import PointCloud2

from space_perception.pointcloud_utils import (
    cloud_xyz_numpy,
    create_elevation_cloud,
)
from space_perception.terrain_processing import (
    aggregate_elevation_cells,
    cells_to_array,
    retain_local_fresh_cells,
)
from std_msgs.msg import ColorRGBA, Header
from tf2_ros import Buffer, TransformException, TransformListener
from visualization_msgs.msg import Marker, MarkerArray


class LocalElevationMapNode(Node):
    """Maintain and publish measured local elevation cells."""

    def __init__(self):
        super().__init__('local_elevation_map_node')
        defaults = {
            'input_topic': '/terrain/filtered_points',
            'elevation_points_topic': '/terrain/elevation_points',
            'marker_topic': '/terrain/elevation_markers',
            'target_frame': 'odom',
            'base_frame': 'base_footprint',
            'grid_resolution': 0.05,
            'grid_length_x': 4.0,
            'grid_length_y': 4.0,
            'min_points_per_cell': 2,
            'elevation_statistic': 'median',
            'cell_timeout': 2.0,
            'publish_rate': 5.0,
            'marker_cell_thickness': 0.015,
            'min_visual_elevation': 0.0,
            'max_visual_elevation': 0.55,
            'marker_alpha': 0.75,
        }
        for name, value in defaults.items():
            self.declare_parameter(name, value)
        self._target = self.get_parameter('target_frame').value
        self._base = self.get_parameter('base_frame').value
        self._resolution = float(
            self.get_parameter('grid_resolution').value
        )
        rate = float(self.get_parameter('publish_rate').value)
        if self._resolution <= 0.0 or rate <= 0.0:
            raise ValueError('grid_resolution and publish_rate must be positive')
        self._tf_buffer = Buffer()
        self._tf_listener = TransformListener(self._tf_buffer, self)
        sensor_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )
        self._points_publisher = self.create_publisher(
            PointCloud2,
            self.get_parameter('elevation_points_topic').value,
            sensor_qos,
        )
        self._marker_publisher = self.create_publisher(
            MarkerArray, self.get_parameter('marker_topic').value, 5
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
        self._last_header = Header(frame_id=self._target)
        self._cells = {}
        self._duration_ms = 0.0
        self._marker_duration_ms = 0.0
        self._processed = 0
        self._started_wall = time.monotonic()
        self._last_log_wall = time.monotonic()
        self._last_warning_wall = 0.0
        self.create_timer(1.0 / rate, self._update)
        self.get_logger().info(
            f'Local elevation grid {self.get_parameter("grid_length_x").value}'
            f'x{self.get_parameter("grid_length_y").value} m at '
            f'{self._resolution:.3f} m resolution'
        )

    def _cloud_callback(self, message):
        self._latest = message

    def _rover_position(self, stamp):
        transform = self._tf_buffer.lookup_transform(
            self._target,
            self._base,
            stamp,
            timeout=Duration(seconds=0.05),
        )
        return (
            transform.transform.translation.x,
            transform.transform.translation.y,
        )

    def _update(self):
        message = self._latest
        if message is None:
            self._publish_diagnostics(False)
            return
        started = time.perf_counter()
        stamp_key = (message.header.stamp.sec, message.header.stamp.nanosec)
        stamp = Time.from_msg(message.header.stamp)
        try:
            center_x, center_y = self._rover_position(stamp)
        except TransformException as error:
            now = time.monotonic()
            if now - self._last_warning_wall >= 5.0:
                self.get_logger().warning(
                    f'Elevation grid rover TF unavailable: {error}'
                )
                self._last_warning_wall = now
            self._publish_diagnostics(True)
            return

        if stamp_key != self._last_stamp:
            measured = aggregate_elevation_cells(
                cloud_xyz_numpy(message),
                resolution=self._resolution,
                min_points=int(
                    self.get_parameter('min_points_per_cell').value
                ),
                statistic=self.get_parameter('elevation_statistic').value,
                stamp_ns=stamp.nanoseconds,
            )
            self._cells.update(measured)
            self._last_stamp = stamp_key
            self._last_header = Header(
                stamp=deepcopy(message.header.stamp), frame_id=self._target
            )
            self._processed += 1

        timeout_ns = int(
            float(self.get_parameter('cell_timeout').value) * 1e9
        )
        self._cells = retain_local_fresh_cells(
            self._cells,
            center_x=center_x,
            center_y=center_y,
            length_x=float(self.get_parameter('grid_length_x').value),
            length_y=float(self.get_parameter('grid_length_y').value),
            now_ns=self.get_clock().now().nanoseconds,
            timeout_ns=timeout_ns,
        )
        rows = cells_to_array(self._cells)
        self._points_publisher.publish(
            create_elevation_cloud(self._last_header, rows)
        )
        marker_started = time.perf_counter()
        markers = self._create_markers(self._last_header, rows)
        self._marker_duration_ms = (
            time.perf_counter() - marker_started
        ) * 1000.0
        self._marker_publisher.publish(markers)
        self._duration_ms = (time.perf_counter() - started) * 1000.0
        self._publish_diagnostics(True)
        now = time.monotonic()
        if now - self._last_log_wall >= 5.0:
            rate = self._processed / max(now - self._started_wall, 1e-9)
            self.get_logger().info(
                f'elevation cells={len(rows)} '
                f'processing={self._duration_ms:.2f} ms rate={rate:.2f} Hz'
            )
            self._last_log_wall = now

    def _create_markers(self, header, rows):
        delete = Marker(
            header=header,
            ns='terrain_elevation',
            id=0,
            action=Marker.DELETEALL,
        )
        marker = Marker(
            header=header,
            ns='terrain_elevation',
            id=1,
            type=Marker.CUBE_LIST,
            action=Marker.ADD,
        )
        marker.pose.orientation.w = 1.0
        minimum = float(self.get_parameter('min_visual_elevation').value)
        maximum = float(self.get_parameter('max_visual_elevation').value)
        span = max(maximum - minimum, 1e-9)
        thickness = float(
            self.get_parameter('marker_cell_thickness').value
        )
        alpha = float(self.get_parameter('marker_alpha').value)
        marker.scale.x = self._resolution
        marker.scale.y = self._resolution
        marker.scale.z = thickness
        for row in rows:
            normalized = float(np.clip((row[2] - minimum) / span, 0.0, 1.0))
            marker.points.append(
                Point(x=float(row[0]), y=float(row[1]), z=float(row[2]))
            )
            marker.colors.append(ColorRGBA(
                r=normalized,
                g=1.0 - abs(2.0 * normalized - 1.0),
                b=1.0 - normalized,
                a=alpha,
            ))
        return MarkerArray(markers=[delete, marker])

    def _publish_diagnostics(self, input_received):
        elapsed = max(time.monotonic() - self._started_wall, 1e-9)
        status = DiagnosticStatus(
            level=DiagnosticStatus.OK if input_received else DiagnosticStatus.WARN,
            name='local_elevation_map',
            message='processing' if input_received else 'waiting for cloud',
            values=[
                KeyValue(key='input_cloud_received', value=str(input_received)),
                KeyValue(
                    key='valid_elevation_cell_count',
                    value=str(len(self._cells)),
                ),
                KeyValue(
                    key='processing_duration_ms',
                    value=f'{self._duration_ms:.3f}',
                ),
                KeyValue(
                    key='processing_rate_hz',
                    value=f'{self._processed / elapsed:.3f}',
                ),
                KeyValue(
                    key='marker_construction_duration_ms',
                    value=f'{self._marker_duration_ms:.3f}',
                ),
            ],
        )
        self._diagnostics.publish(
            DiagnosticArray(
                header=Header(stamp=self.get_clock().now().to_msg()),
                status=[status],
            )
        )


def main(args=None):
    rclpy.init(args=args)
    node = LocalElevationMapNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
