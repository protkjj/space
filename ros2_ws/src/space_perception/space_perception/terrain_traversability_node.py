#!/usr/bin/env python3
"""Publish interpretable prototype traversability from terrain features."""

from copy import deepcopy
import time

from diagnostic_msgs.msg import DiagnosticArray, DiagnosticStatus, KeyValue
from geometry_msgs.msg import Point
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import PointCloud2

from space_perception.pointcloud_utils import (
    create_traversability_cloud,
    feature_cloud_numpy,
)
from space_perception.traversability import (
    compute_traversability,
    TraversabilityConfig,
    TraversabilityStats,
)
from std_msgs.msg import ColorRGBA, Header
from visualization_msgs.msg import Marker, MarkerArray


class TerrainTraversabilityNode(Node):
    """Score feature cells without claiming safe or unsafe terrain."""

    def __init__(self):
        super().__init__('terrain_traversability_node')
        defaults = {
            'input_topic': '/terrain/features',
            'output_topic': '/terrain/traversability',
            'marker_topic': '/terrain/traversability_markers',
            'diagnostics_topic': '/terrain/traversability_diagnostics',
            'composition_mode': 'weighted_sum',
            'slope_free': float(np.deg2rad(5.0)),
            'slope_max': float(np.deg2rad(30.0)),
            'roughness_free': 0.002,
            'roughness_max': 0.025,
            'step_free': 0.005,
            'step_max': 0.056,
            'variance_free': 0.000025,
            'variance_max': 0.0004,
            'coverage_min': 0.60,
            'confidence_min': 0.10,
            'minimum_neighbors': 8,
            'weight_slope': 0.35,
            'weight_roughness': 0.20,
            'weight_step': 0.30,
            'weight_uncertainty': 0.15,
            'publish_rate': 5.0,
            'marker_alpha': 0.80,
            'grid_resolution': 0.05,
        }
        for name, value in defaults.items():
            self.declare_parameter(name, value)
        self._config = TraversabilityConfig(**{
            name: self.get_parameter(name).value
            for name in TraversabilityConfig.__dataclass_fields__
        })
        rate = float(self.get_parameter('publish_rate').value)
        self._grid_resolution = float(
            self.get_parameter('grid_resolution').value
        )
        if rate <= 0.0 or self._grid_resolution <= 0.0:
            raise ValueError('publish rate and grid resolution must be positive')
        compute_traversability(np.empty((0, 11)), self._config)
        sensor_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )
        self._output_publisher = self.create_publisher(
            PointCloud2, self.get_parameter('output_topic').value, sensor_qos
        )
        self._marker_publisher = self.create_publisher(
            MarkerArray, self.get_parameter('marker_topic').value, 5
        )
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
        self._marker_duration_ms = 0.0
        self._processed = 0
        self._started_wall = time.monotonic()
        self._last_warning_wall = 0.0
        self._stats = TraversabilityStats(
            0, 0, 0, np.nan, np.nan, np.nan,
            np.nan, np.nan, np.nan, np.nan, tuple([0] * 7)
        )
        self.create_timer(1.0 / rate, self._update)
        self.get_logger().info(
            f'Traversability mode={self._config.composition_mode} '
            f'at up to {rate:.1f} Hz'
        )

    def _cloud_callback(self, message):
        self._latest = message
        self._input_received = True

    def _warn_throttled(self, message):
        now = time.monotonic()
        if now - self._last_warning_wall >= 5.0:
            self.get_logger().warning(message)
            self._last_warning_wall = now

    def _update(self):
        message = self._latest
        if message is None:
            self._publish_diagnostics()
            return
        stamp_key = (message.header.stamp.sec, message.header.stamp.nanosec)
        if stamp_key == self._last_stamp:
            self._publish_diagnostics()
            return
        started = time.perf_counter()
        try:
            rows = feature_cloud_numpy(message)
            output, self._stats = compute_traversability(
                rows, self._config
            )
        except (TypeError, ValueError) as error:
            self._warn_throttled(f'Invalid feature cloud skipped: {error}')
            self._last_stamp = stamp_key
            self._output_published = False
            self._publish_diagnostics()
            return
        header = Header(
            stamp=deepcopy(message.header.stamp),
            frame_id=message.header.frame_id,
        )
        self._output_publisher.publish(
            create_traversability_cloud(header, output)
        )
        marker_started = time.perf_counter()
        markers = self._create_markers(header, output)
        self._marker_duration_ms = (
            time.perf_counter() - marker_started
        ) * 1000.0
        self._marker_publisher.publish(markers)
        self._last_stamp = stamp_key
        self._processed += 1
        self._output_published = True
        self._duration_ms = (time.perf_counter() - started) * 1000.0
        self._publish_diagnostics()

    def _create_markers(self, header, output):
        delete = Marker(
            header=header,
            ns='terrain_traversability',
            id=0,
            action=Marker.DELETEALL,
        )
        marker = Marker(
            header=header,
            ns='terrain_traversability',
            id=1,
            type=Marker.CUBE_LIST,
            action=Marker.ADD,
        )
        marker.pose.orientation.w = 1.0
        marker.scale.x = self._grid_resolution
        marker.scale.y = self._grid_resolution
        marker.scale.z = 0.014
        alpha = float(self.get_parameter('marker_alpha').value)
        for row in output[output[:, 9] == 1]:
            score = float(np.clip(row[3], 0.0, 1.0))
            marker.points.append(Point(
                x=float(row[0]), y=float(row[1]), z=float(row[2])
            ))
            marker.colors.append(ColorRGBA(
                r=1.0 - score,
                g=score,
                b=0.15 * (1.0 - abs(2.0 * score - 1.0)),
                a=alpha,
            ))
        return MarkerArray(markers=[delete, marker])

    def _input_age(self):
        if self._latest is None:
            return 0.0
        stamp_ns = (
            self._latest.header.stamp.sec * 1_000_000_000
            + self._latest.header.stamp.nanosec
        )
        return max(
            (self.get_clock().now().nanoseconds - stamp_ns) / 1e9, 0.0
        )

    @staticmethod
    def _format_stat(value):
        return 'nan' if not np.isfinite(value) else f'{value:.6f}'

    def _publish_diagnostics(self):
        elapsed = max(time.monotonic() - self._started_wall, 1e-9)
        labels = (
            'none', 'slope', 'roughness', 'step_height',
            'uncertainty', 'low_confidence', 'invalid'
        )
        values = [
            KeyValue(
                key='input_features_received',
                value=str(self._input_received),
            ),
            KeyValue(
                key='input_feature_age_seconds',
                value=f'{self._input_age():.3f}',
            ),
            KeyValue(key='input_cell_count',
                     value=str(self._stats.input_cells)),
            KeyValue(key='valid_scored_cell_count',
                     value=str(self._stats.valid_cells)),
            KeyValue(key='invalid_cell_count',
                     value=str(self._stats.invalid_cells)),
            KeyValue(key='median_traversability',
                     value=self._format_stat(
                         self._stats.median_traversability
                     )),
            KeyValue(key='minimum_traversability',
                     value=self._format_stat(
                         self._stats.minimum_traversability
                     )),
            KeyValue(key='maximum_traversability',
                     value=self._format_stat(
                         self._stats.maximum_traversability
                     )),
            KeyValue(key='median_slope_penalty',
                     value=self._format_stat(
                         self._stats.median_slope_penalty
                     )),
            KeyValue(key='median_roughness_penalty',
                     value=self._format_stat(
                         self._stats.median_roughness_penalty
                     )),
            KeyValue(key='median_step_penalty',
                     value=self._format_stat(
                         self._stats.median_step_penalty
                     )),
            KeyValue(key='median_uncertainty_penalty',
                     value=self._format_stat(
                         self._stats.median_uncertainty_penalty
                     )),
            *[
                KeyValue(
                    key=f'limiting_factor_{label}_count',
                    value=str(count),
                )
                for label, count in zip(
                    labels, self._stats.limiting_factor_counts
                )
            ],
            KeyValue(key='processing_duration_ms',
                     value=f'{self._duration_ms:.3f}'),
            KeyValue(key='marker_construction_duration_ms',
                     value=f'{self._marker_duration_ms:.3f}'),
            KeyValue(key='effective_output_rate_hz',
                     value=f'{self._processed / elapsed:.3f}'),
            KeyValue(key='active_composition_mode',
                     value=self._config.composition_mode),
            KeyValue(key='output_cloud_published',
                     value=str(self._output_published)),
        ]
        status = DiagnosticStatus(
            level=(
                DiagnosticStatus.OK
                if self._input_received else DiagnosticStatus.WARN
            ),
            name='terrain_traversability_node',
            message=(
                'scoring'
                if self._input_received else 'waiting for terrain features'
            ),
            values=values,
        )
        self._diagnostic_publisher.publish(DiagnosticArray(
            header=Header(stamp=self.get_clock().now().to_msg()),
            status=[status],
        ))


def main(args=None):
    rclpy.init(args=args)
    node = TerrainTraversabilityNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
