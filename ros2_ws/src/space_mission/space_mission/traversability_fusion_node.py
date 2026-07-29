#!/usr/bin/env python3
"""Own the boundary between perception measurements and mission products."""

from diagnostic_msgs.msg import DiagnosticArray, DiagnosticStatus, KeyValue
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import PointCloud2
from std_msgs.msg import Header


class TraversabilityFusionNode(Node):
    """
    Publish the mission-owned traversability product.

    The first implementation forwards visual traversability unchanged while
    observing its elevation and feature inputs. Slip and medium-rover transfer
    models can be fused here without reconnecting Navigation to Perception.
    """

    def __init__(self):
        super().__init__('mission_traversability_fusion')
        defaults = {
            'elevation_topic': '/terrain/elevation_points',
            'feature_topic': '/terrain/features',
            'visual_traversability_topic': '/terrain/traversability',
            'output_topic': '/mission/traversability',
            'diagnostics_topic': '/mission/diagnostics',
        }
        for name, value in defaults.items():
            self.declare_parameter(name, value)

        sensor_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )
        self._output = self.create_publisher(
            PointCloud2,
            self.get_parameter('output_topic').value,
            sensor_qos,
        )
        self._diagnostics = self.create_publisher(
            DiagnosticArray,
            self.get_parameter('diagnostics_topic').value,
            10,
        )
        self.create_subscription(
            PointCloud2,
            self.get_parameter('elevation_topic').value,
            self._on_elevation,
            sensor_qos,
        )
        self.create_subscription(
            PointCloud2,
            self.get_parameter('feature_topic').value,
            self._on_features,
            sensor_qos,
        )
        self.create_subscription(
            PointCloud2,
            self.get_parameter('visual_traversability_topic').value,
            self._on_visual_traversability,
            sensor_qos,
        )

        self._elevation_received = False
        self._features_received = False
        self._visual_received = False
        self._published_count = 0
        self.create_timer(1.0, self._publish_diagnostics)
        self.get_logger().info(
            'Mission traversability boundary ready: '
            '/terrain/traversability -> /mission/traversability '
            '(visual-only fusion stage)'
        )

    def _on_elevation(self, _: PointCloud2) -> None:
        self._elevation_received = True

    def _on_features(self, _: PointCloud2) -> None:
        self._features_received = True

    def _on_visual_traversability(self, message: PointCloud2) -> None:
        self._visual_received = True
        self._output.publish(message)
        self._published_count += 1

    def _publish_diagnostics(self) -> None:
        ready = (
            self._elevation_received
            and self._features_received
            and self._visual_received
        )
        status = DiagnosticStatus(
            level=(
                DiagnosticStatus.OK if ready else DiagnosticStatus.WARN
            ),
            name='mission_traversability_fusion',
            message=(
                'publishing visual-only mission traversability'
                if ready
                else 'waiting for perception inputs'
            ),
            values=[
                KeyValue(
                    key='elevation_received',
                    value=str(self._elevation_received),
                ),
                KeyValue(
                    key='features_received',
                    value=str(self._features_received),
                ),
                KeyValue(
                    key='visual_traversability_received',
                    value=str(self._visual_received),
                ),
                KeyValue(
                    key='published_count',
                    value=str(self._published_count),
                ),
                KeyValue(key='fusion_stage', value='visual_only'),
            ],
        )
        self._diagnostics.publish(
            DiagnosticArray(
                header=Header(stamp=self.get_clock().now().to_msg()),
                status=[status],
            )
        )


def main(args=None):
    """Run the mission traversability fusion boundary."""
    rclpy.init(args=args)
    node = TraversabilityFusionNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
