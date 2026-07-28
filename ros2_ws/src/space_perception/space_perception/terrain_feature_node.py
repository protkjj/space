#!/usr/bin/env python3
"""Publish measured local terrain features from elevation grid cells."""

from copy import deepcopy
import time

from diagnostic_msgs.msg import DiagnosticArray, DiagnosticStatus, KeyValue
from geometry_msgs.msg import Point
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import PointCloud2

from space_perception.latest_data import sample_disposition
from space_perception.pointcloud_utils import (
    create_feature_cloud,
    elevation_cloud_numpy,
)
from space_perception.terrain_features import (
    compute_terrain_features,
    FeatureConfig,
    FeatureStats,
)
from std_msgs.msg import ColorRGBA, Header
from visualization_msgs.msg import Marker, MarkerArray


class TerrainFeatureNode(Node):
    """Compute geometric features without terrain-safety interpretation."""

    def __init__(self):
        super().__init__('terrain_feature_node')
        defaults = {
            'input_topic': '/terrain/elevation_points',
            'output_topic': '/terrain/features',
            'target_frame': 'odom',
            'grid_resolution': 0.05,
            'feature_radius': 0.15,
            'minimum_neighbors': 5,
            'minimum_adjacent_neighbors': 2,
            'maximum_neighbors': 32,
            'plane_fit_method': 'svd',
            'maximum_condition_number': 100.0,
            'maximum_fit_residual': 0.05,
            'roughness_method': 'median_absolute_residual',
            'step_neighborhood_cells': 1,
            'confidence_min_point_count': 2,
            'confidence_target_point_count': 8,
            'confidence_variance_scale': 0.02,
            'confidence_residual_scale': 0.02,
            'publish_rate': 5.0,
            'diagnostics_topic': '/terrain/feature_diagnostics',
            'marker_alpha': 0.80,
            'slope_visual_maximum': 0.6,
            'roughness_visual_maximum': 0.05,
            'step_visual_maximum': 0.10,
            'maximum_input_age': 1.0,
            'drop_stale_input': True,
            'process_latest_only': True,
        }
        for name, value in defaults.items():
            self.declare_parameter(name, value)
        self._target_frame = self.get_parameter('target_frame').value
        self._config = FeatureConfig(**{
            name: self.get_parameter(name).value
            for name in FeatureConfig.__dataclass_fields__
        })
        rate = float(self.get_parameter('publish_rate').value)
        if rate <= 0.0:
            raise ValueError('publish_rate must be positive')
        # Validate configuration before the first cloud arrives.
        compute_terrain_features(np.empty((0, 5)), self._config)
        sensor_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )
        self._feature_publisher = self.create_publisher(
            PointCloud2, self.get_parameter('output_topic').value, sensor_qos
        )
        self._marker_publishers = {
            'slope': self.create_publisher(
                MarkerArray, '/terrain/slope_markers', 5
            ),
            'roughness': self.create_publisher(
                MarkerArray, '/terrain/roughness_markers', 5
            ),
            'step_height': self.create_publisher(
                MarkerArray, '/terrain/step_markers', 5
            ),
        }
        self._diagnostic_publisher = self.create_publisher(
            DiagnosticArray,
            self.get_parameter('diagnostics_topic').value,
            10,
        )
        self.create_subscription(
            PointCloud2,
            self.get_parameter('input_topic').value,
            self._cloud_callback,
            sensor_qos,
        )
        self._latest = None
        self._last_stamp = None
        self._input_received = False
        self._output_published = False
        self._duration_ms = 0.0
        self._marker_duration_ms = {
            'slope': 0.0, 'roughness': 0.0, 'step_height': 0.0
        }
        self._processed = 0
        self._duplicate_drops = 0
        self._stale_drops = 0
        self._started_wall = time.monotonic()
        self._last_warning_wall = 0.0
        self._stats = FeatureStats(0, 0, 0, 0, 0, 0, 0.0, 0.0, 0.0)
        self.get_logger().info(
            f'Terrain features radius={self._config.feature_radius:.2f} m '
            f'at {rate:.1f} Hz'
        )

    def _cloud_callback(self, message):
        self._latest = message
        self._input_received = True
        self._update(message)

    def _warn_throttled(self, message):
        now = time.monotonic()
        if now - self._last_warning_wall >= 5.0:
            self.get_logger().warning(message)
            self._last_warning_wall = now

    def _update(self, message=None):
        message = message if message is not None else self._latest
        if message is None:
            self._publish_diagnostics()
            return
        stamp_key = (message.header.stamp.sec, message.header.stamp.nanosec)
        stamp_ns = message.header.stamp.sec * 1_000_000_000
        stamp_ns += message.header.stamp.nanosec
        last_ns = None
        if self._last_stamp is not None:
            last_ns = self._last_stamp[0] * 1_000_000_000
            last_ns += self._last_stamp[1]
        disposition = sample_disposition(
            stamp_ns,
            last_ns,
            self.get_clock().now().nanoseconds,
            float(self.get_parameter('maximum_input_age').value),
            bool(self.get_parameter('drop_stale_input').value),
        )
        if disposition == 'duplicate':
            self._duplicate_drops += 1
            return
        if disposition == 'stale':
            self._stale_drops += 1
            self._last_stamp = stamp_key
            self._output_published = False
            self._publish_diagnostics()
            return
        if message.header.frame_id != self._target_frame:
            self._warn_throttled(
                f'Expected elevation frame {self._target_frame}, received '
                f'{message.header.frame_id}; cloud skipped'
            )
            self._output_published = False
            self._publish_diagnostics()
            return
        started = time.perf_counter()
        try:
            rows = elevation_cloud_numpy(message)
            features, self._stats = compute_terrain_features(
                rows, self._config
            )
        except (TypeError, ValueError) as error:
            self._warn_throttled(f'Invalid elevation cloud skipped: {error}')
            self._output_published = False
            self._last_stamp = stamp_key
            self._publish_diagnostics()
            return
        header = Header(
            stamp=deepcopy(message.header.stamp),
            frame_id=message.header.frame_id,
        )
        self._feature_publisher.publish(create_feature_cloud(header, features))
        mappings = (
            ('slope', 3, 'slope_visual_maximum'),
            ('roughness', 4, 'roughness_visual_maximum'),
            ('step_height', 5, 'step_visual_maximum'),
        )
        for name, column, maximum_parameter in mappings:
            marker_started = time.perf_counter()
            markers = self._create_markers(
                header,
                features,
                name,
                column,
                float(self.get_parameter(maximum_parameter).value),
            )
            self._marker_publishers[name].publish(markers)
            self._marker_duration_ms[name] = (
                time.perf_counter() - marker_started
            ) * 1000.0
        self._last_stamp = stamp_key
        self._processed += 1
        self._output_published = True
        self._duration_ms = (time.perf_counter() - started) * 1000.0
        self._publish_diagnostics()

    def _create_markers(self, header, features, namespace, column, maximum):
        delete = Marker(
            header=header, ns=namespace, id=0, action=Marker.DELETEALL
        )
        marker = Marker(
            header=header,
            ns=namespace,
            id=1,
            type=Marker.CUBE_LIST,
            action=Marker.ADD,
        )
        marker.pose.orientation.w = 1.0
        marker.scale.x = self._config.grid_resolution
        marker.scale.y = self._config.grid_resolution
        marker.scale.z = 0.012
        alpha = float(self.get_parameter('marker_alpha').value)
        span = max(maximum, np.finfo(float).eps)
        for row in features:
            value = float(np.clip(row[column] / span, 0.0, 1.0))
            marker.points.append(
                Point(x=float(row[0]), y=float(row[1]), z=float(row[2]))
            )
            marker.colors.append(ColorRGBA(
                r=value,
                g=1.0 - abs(2.0 * value - 1.0),
                b=1.0 - value,
                a=alpha,
            ))
        return MarkerArray(markers=[delete, marker])

    def _cloud_age(self):
        if self._latest is None:
            return 0.0
        stamp_ns = (
            self._latest.header.stamp.sec * 1_000_000_000
            + self._latest.header.stamp.nanosec
        )
        return max(
            (self.get_clock().now().nanoseconds - stamp_ns) / 1e9, 0.0
        )

    def _publish_diagnostics(self):
        elapsed = max(time.monotonic() - self._started_wall, 1e-9)
        received = self._input_received
        status = DiagnosticStatus(
            level=DiagnosticStatus.OK if received else DiagnosticStatus.WARN,
            name='terrain_feature_node',
            message='processing' if received else 'waiting for elevation cloud',
            values=[
                KeyValue(key='input_elevation_cloud_received',
                         value=str(received)),
                KeyValue(key='input_cloud_age_seconds',
                         value=f'{self._cloud_age():.3f}'),
                KeyValue(key='elevation_cell_count',
                         value=str(self._stats.input_cells)),
                KeyValue(key='valid_feature_cell_count',
                         value=str(self._stats.valid_cells)),
                KeyValue(key='rejected_insufficient_neighbors',
                         value=str(self._stats.rejected_neighbors)),
                KeyValue(key='rejected_poor_plane_fit',
                         value=str(self._stats.rejected_plane_fit)),
                KeyValue(key='median_neighbor_count',
                         value=f'{self._stats.median_neighbor_count:.3f}'),
                KeyValue(key='median_neighborhood_coverage',
                         value=f'{self._stats.median_coverage:.3f}'),
                KeyValue(key='median_plane_residual_m',
                         value=f'{self._stats.median_plane_residual:.6f}'),
                KeyValue(key='processing_duration_ms',
                         value=f'{self._duration_ms:.3f}'),
                KeyValue(key='effective_processing_rate_hz',
                         value=f'{self._processed / elapsed:.3f}'),
                KeyValue(key='output_cloud_published',
                         value=str(self._output_published)),
                KeyValue(key='duplicate_input_drop_count',
                         value=str(self._duplicate_drops)),
                KeyValue(key='stale_input_drop_count',
                         value=str(self._stale_drops)),
                *[
                    KeyValue(
                        key=f'{name}_marker_duration_ms',
                        value=f'{duration:.3f}',
                    )
                    for name, duration in self._marker_duration_ms.items()
                ],
            ],
        )
        self._diagnostic_publisher.publish(DiagnosticArray(
            header=Header(stamp=self.get_clock().now().to_msg()),
            status=[status],
        ))


def main(args=None):
    rclpy.init(args=args)
    node = TerrainFeatureNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
