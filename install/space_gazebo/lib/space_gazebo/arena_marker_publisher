#!/usr/bin/env python3
"""Publish the installed arena visual mesh as a transient-local RViz marker."""

import math

import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from visualization_msgs.msg import Marker


class ArenaMarkerPublisher(Node):
    """Publish one configurable static mesh marker."""

    def __init__(self):
        super().__init__('arena_marker_publisher')
        defaults = {
            'frame_id': 'odom',
            'mesh_resource': (
                'package://space_gazebo/models/arena_test_slope_v04/'
                'meshes/arena_visual.stl'
            ),
            'scale': [0.001, 0.001, 0.001],
            'position': [-0.8, -2.0, 0.0],
            'orientation_rpy': [math.pi / 2.0, 0.0, 0.0],
        }
        for name, value in defaults.items():
            self.declare_parameter(name, value)
        qos = QoSProfile(
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )
        self.publisher = self.create_publisher(
            Marker, '/arena/visualization_marker', qos
        )
        self.timer = self.create_timer(1.0, self.publish_marker)
        self.publish_marker()

    def publish_marker(self):
        marker = Marker()
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.header.frame_id = self.get_parameter('frame_id').value
        marker.ns = 'arena'
        marker.id = 0
        marker.type = Marker.MESH_RESOURCE
        marker.action = Marker.ADD
        marker.mesh_resource = self.get_parameter('mesh_resource').value
        marker.mesh_use_embedded_materials = False
        position = self.get_parameter('position').value
        scale = self.get_parameter('scale').value
        roll, pitch, yaw = self.get_parameter('orientation_rpy').value
        marker.pose.position.x, marker.pose.position.y, marker.pose.position.z = position
        cr, sr = math.cos(roll / 2), math.sin(roll / 2)
        cp, sp = math.cos(pitch / 2), math.sin(pitch / 2)
        cy, sy = math.cos(yaw / 2), math.sin(yaw / 2)
        marker.pose.orientation.w = cr * cp * cy + sr * sp * sy
        marker.pose.orientation.x = sr * cp * cy - cr * sp * sy
        marker.pose.orientation.y = cr * sp * cy + sr * cp * sy
        marker.pose.orientation.z = cr * cp * sy - sr * sp * cy
        marker.scale.x, marker.scale.y, marker.scale.z = scale
        marker.color.r, marker.color.g, marker.color.b, marker.color.a = (
            0.55, 0.50, 0.40, 1.0
        )
        self.publisher.publish(marker)


def main(args=None):
    rclpy.init(args=args)
    node = ArenaMarkerPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
