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

import math

from diagnostic_msgs.msg import DiagnosticArray, DiagnosticStatus, KeyValue
from nav_msgs.msg import Odometry
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import JointState
from space_mission.slip_math import compute_slip, wheel_linear_speed
from space_msgs.msg import SlipEstimate
from std_msgs.msg import Header


class SlipEstimatorNode(Node):
    """Compare encoder velocity against VIO velocity to expose terrain slip."""

    def __init__(self):
        super().__init__('slip_estimator')
        defaults = {
            'joint_states_topic': '/joint_states',
            # Sim: ground-truth /odom (wheel-independent). HW: /vio/odom.
            'actual_odom_topic': '/odom',
            'output_topic': '/slip',
            'diagnostics_topic': '/slip/diagnostics',
            # Which producer supplies v_actual. Typed into the message so a
            # consumer can enforce CLAUDE.md 1.3: 'ekf' fuses wheel encoders,
            # which makes the slip ratio circular -- and that failure is
            # invisible at runtime, the arithmetic still succeeds.
            'actual_source': 'sim_ground_truth',
            # Forward-velocity variance at which quality reaches zero. A
            # PLACEHOLDER until a real VIO reports its covariance scale
            # (docs/pending.md).
            'quality_variance_scale': 0.01,
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
        self._quality_scale = float(
            self.get_parameter('quality_variance_scale').value
        )
        if self._quality_scale <= 0.0:
            raise ValueError('quality_variance_scale must be positive')
        self._source = self._resolve_source(
            str(self.get_parameter('actual_source').value)
        )

        sensor_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )
        self._slip_pub = self.create_publisher(
            SlipEstimate, self.get_parameter('output_topic').value, 10
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
        self._v_actual_quality = 0.0
        self._slip_ema = None
        self.create_timer(1.0 / publish_rate, self._update)
        self.get_logger().info(
            'Slip estimator ready: encoder(/joint_states) vs '
            f"actual({self.get_parameter('actual_odom_topic').value}) "
            f"-> {self.get_parameter('output_topic').value}"
        )
        if self._source == SlipEstimate.SOURCE_EKF:
            self.get_logger().error(
                'actual_source=ekf makes the slip ratio CIRCULAR: '
                'robot_localization fuses wheel encoders, so v_actual is not '
                'wheel-independent (CLAUDE.md 1.3). Publishing anyway so the '
                'source field warns consumers, but this is not a valid setup.'
            )

    _SOURCES = {
        'unknown': SlipEstimate.SOURCE_UNKNOWN,
        'sim_ground_truth': SlipEstimate.SOURCE_SIM_GROUND_TRUTH,
        'vio': SlipEstimate.SOURCE_VIO,
        'ekf': SlipEstimate.SOURCE_EKF,
    }

    def _resolve_source(self, name):
        """Map the ``actual_source`` parameter onto the message enum."""
        try:
            return self._SOURCES[name]
        except KeyError:
            raise ValueError(
                f'actual_source must be one of {sorted(self._SOURCES)}, '
                f'got {name!r}'
            ) from None

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
        self._v_actual_quality = self._quality_from_covariance(message)

    def _quality_from_covariance(self, message: Odometry) -> float:
        """
        Return confidence in ``v_actual``, in ``[0, 1]``.

        Derived from the forward-velocity variance the producer reports
        (``twist.covariance[0]``). Gazebo ground truth leaves it at zero,
        which is honest: the pose IS exact, so quality is 1.0. A real VIO
        fills it in, and quality falls as the variance approaches
        ``quality_variance_scale``.

        A status-topic hook belongs here once a VIO node exists -- the
        tracking state it reports is a better signal than covariance alone,
        and this is the single place that would need to change.
        """
        variance = float(message.twist.covariance[0])
        if not math.isfinite(variance) or variance <= 0.0:
            return 1.0
        return float(
            max(0.0, min(1.0, 1.0 - variance / self._quality_scale))
        )

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
            self._publish_invalid()
            self._publish_diagnostics(state, None)
            return

        lam = compute_slip(
            self._v_wheel, self._v_actual, self._min_wheel_speed
        )
        if lam is None:
            # A stationary rover has no defined slip. Say so explicitly rather
            # than going silent: a consumer cannot distinguish silence from a
            # dead node, but valid=false is unambiguous.
            self._publish_invalid()
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
        estimate = SlipEstimate()
        estimate.header = Header(stamp=now, frame_id='base_footprint')
        estimate.slip_ratio = float(self._slip_ema)
        estimate.v_wheel = float(self._v_wheel)
        estimate.v_actual = float(self._v_actual)
        estimate.valid = True
        estimate.quality = float(self._v_actual_quality)
        estimate.source = self._source
        self._slip_pub.publish(estimate)
        self._publish_diagnostics('ok', self._slip_ema)

    def _publish_invalid(self) -> None:
        """
        Publish ``valid=False`` with a NaN ratio.

        NaN rather than zero so a consumer that ignores ``valid`` fails loudly
        instead of acting on a fabricated "no slip" reading.
        """
        estimate = SlipEstimate()
        estimate.header = Header(
            stamp=self.get_clock().now().to_msg(), frame_id='base_footprint'
        )
        estimate.slip_ratio = float('nan')
        estimate.v_wheel = float(self._v_wheel or 0.0)
        estimate.v_actual = float(self._v_actual or 0.0)
        estimate.valid = False
        estimate.quality = float(self._v_actual_quality)
        estimate.source = self._source
        self._slip_pub.publish(estimate)

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
