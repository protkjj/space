#!/usr/bin/env python3
"""
Estimate wheel slip: encoder motion vs a wheel-independent velocity.

This is the rover's signature measurement (mission doc section 1). Geometry
alone cannot separate a safe 15 deg slope from a sinking one; only the slip a
rover actually experiences can. We publish

    lambda = (V_wheel - V_actual) / V_wheel

where ``V_wheel`` is integrated from the wheel joints (the encoder analogue,
inflated by slip) and ``V_actual`` is a wheel-INDEPENDENT velocity. In
simulation ``V_actual`` is Gazebo's ground-truth pose odometry, which never
looks at the wheels, so section 1.3's non-circularity holds. On hardware,
point ``actual_odom_topic`` at the OAK-D VIO (``/vio/odom``); the node code
does not change.

The output is a *relative* slip indicator, not a calibrated measurement.
"""

from diagnostic_msgs.msg import DiagnosticArray, DiagnosticStatus, KeyValue
from geometry_msgs.msg import Vector3Stamped
from nav_msgs.msg import Odometry
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import JointState
from space_mission.slip_math import compute_slip, wheel_linear_speed
from std_msgs.msg import Header


class SlipEstimatorNode(Node):
    """Compare encoder velocity against VIO velocity to expose terrain slip."""

    def __init__(self):
        super().__init__('slip_estimator')
        defaults = {
            'joint_states_topic': '/joint_states',
            # Sim: ground-truth /odom (wheel-independent). HW: /vio/odom.
            'actual_odom_topic': '/odom',
            'output_topic': '/slip/estimate',
            'diagnostics_topic': '/slip/diagnostics',
            # Keep in sync with space_rover.urdf.xacro (CAD: 140 mm diameter).
            'wheel_radius': 0.070,
            'left_wheel_joints': [
                'left_front_wheel_joint', 'left_rear_wheel_joint',
            ],
            'right_wheel_joints': [
                'right_front_wheel_joint', 'right_rear_wheel_joint',
            ],
            'min_wheel_speed': 0.03,
            'max_input_age': 0.3,
            'publish_rate': 10.0,
            'slip_ema_alpha': 0.3,
        }
        for name, value in defaults.items():
            self.declare_parameter(name, value)

        self._wheel_radius = float(self.get_parameter('wheel_radius').value)
        self._left = list(self.get_parameter('left_wheel_joints').value)
        self._right = list(self.get_parameter('right_wheel_joints').value)
        self._min_wheel_speed = float(
            self.get_parameter('min_wheel_speed').value
        )
        self._max_age = float(self.get_parameter('max_input_age').value)
        self._alpha = float(self.get_parameter('slip_ema_alpha').value)
        publish_rate = float(self.get_parameter('publish_rate').value)
        if publish_rate <= 0.0:
            raise ValueError('publish_rate must be positive')

        sensor_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )
        self._slip_pub = self.create_publisher(
            Vector3Stamped, self.get_parameter('output_topic').value, 10
        )
        self._diag_pub = self.create_publisher(
            DiagnosticArray,
            self.get_parameter('diagnostics_topic').value,
            10,
        )
        self.create_subscription(
            JointState,
            self.get_parameter('joint_states_topic').value,
            self._on_joint_states,
            sensor_qos,
        )
        self.create_subscription(
            Odometry,
            self.get_parameter('actual_odom_topic').value,
            self._on_actual_odom,
            sensor_qos,
        )

        self._v_wheel = None
        self._v_wheel_time = None
        self._v_actual = None
        self._v_actual_time = None
        self._slip_ema = None
        self.create_timer(1.0 / publish_rate, self._update)
        self.get_logger().info(
            'Slip estimator ready: encoder(/joint_states) vs '
            f"actual({self.get_parameter('actual_odom_topic').value}) "
            '-> /slip/estimate'
        )

    def _on_joint_states(self, message: JointState) -> None:
        if not message.velocity:
            return
        speeds = dict(zip(message.name, message.velocity))
        left = [speeds[j] for j in self._left if j in speeds]
        right = [speeds[j] for j in self._right if j in speeds]
        if not left and not right:
            return
        self._v_wheel = wheel_linear_speed(left, right, self._wheel_radius)
        self._v_wheel_time = self.get_clock().now()

    def _on_actual_odom(self, message: Odometry) -> None:
        # Forward speed in the body frame; the twist child frame is the base.
        self._v_actual = float(message.twist.twist.linear.x)
        self._v_actual_time = self.get_clock().now()

    def _is_fresh(self, stamp) -> bool:
        if stamp is None:
            return False
        age = (self.get_clock().now() - stamp).nanoseconds * 1e-9
        return age <= self._max_age

    def _update(self) -> None:
        fresh = self._is_fresh(self._v_wheel_time) and self._is_fresh(
            self._v_actual_time
        )
        if not fresh:
            state = 'waiting' if self._v_wheel is None else 'stale_inputs'
            self._publish_diagnostics(state, None)
            return

        lam = compute_slip(
            self._v_wheel, self._v_actual, self._min_wheel_speed
        )
        if lam is None:
            self._publish_diagnostics('idle_low_speed', None)
            return

        # EMA smoothing: this is a relative indicator, so damp per-frame noise.
        if self._slip_ema is None:
            self._slip_ema = lam
        else:
            self._slip_ema = (
                self._alpha * lam + (1.0 - self._alpha) * self._slip_ema
            )

        now = self.get_clock().now().to_msg()
        estimate = Vector3Stamped()
        estimate.header = Header(stamp=now, frame_id='base_footprint')
        estimate.vector.x = self._slip_ema  # smoothed slip ratio
        estimate.vector.y = self._v_wheel   # encoder speed (m/s)
        estimate.vector.z = self._v_actual  # actual speed (m/s)
        self._slip_pub.publish(estimate)
        self._publish_diagnostics('ok', self._slip_ema)

    def _publish_diagnostics(self, state: str, slip) -> None:
        ok = state == 'ok'
        status = DiagnosticStatus(
            level=DiagnosticStatus.OK if ok else DiagnosticStatus.WARN,
            name='slip_estimator',
            message=(
                f'slip={slip:.3f} (relative indicator)'
                if slip is not None
                else f'no slip estimate ({state})'
            ),
            values=[
                KeyValue(key='state', value=state),
                KeyValue(
                    key='v_wheel',
                    value=('nan' if self._v_wheel is None
                           else f'{self._v_wheel:.3f}'),
                ),
                KeyValue(
                    key='v_actual',
                    value=('nan' if self._v_actual is None
                           else f'{self._v_actual:.3f}'),
                ),
                KeyValue(
                    key='slip_ratio',
                    value=('nan' if slip is None else f'{slip:.3f}'),
                ),
            ],
        )
        self._diag_pub.publish(
            DiagnosticArray(
                header=Header(stamp=self.get_clock().now().to_msg()),
                status=[status],
            )
        )


def main(args=None):
    """Run the slip estimator."""
    rclpy.init(args=args)
    node = SlipEstimatorNode()
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
