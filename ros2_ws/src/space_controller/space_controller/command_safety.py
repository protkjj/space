#!/usr/bin/env python3
"""Clip rover commands and maintain a stateful stop-command watchdog."""

from dataclasses import dataclass
from enum import Enum
import math
from typing import Optional

from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node
from space_controller.modes import DriveMode
from std_msgs.msg import UInt8


NANOSECONDS_PER_SECOND = 1_000_000_000


class SafetyState(Enum):
    """Command-safety state independent of the selected actuator backend."""

    NORMAL = 'normal'
    STALE = 'stale'
    HOLD = 'hold'
    EMERGENCY = 'emergency'


@dataclass(frozen=True)
class CommandDecision:
    """Result of presenting a velocity command to the safety policy."""

    publish: bool
    linear_x: float = 0.0
    angular_z: float = 0.0
    recovered: bool = False


@dataclass(frozen=True)
class ModeDecision:
    """Result of presenting a UInt8 mode value to the safety policy."""

    accepted: bool
    changed: bool = False
    publish_stop: bool = False
    previous: Optional[DriveMode] = None
    current: Optional[DriveMode] = None


@dataclass(frozen=True)
class WatchdogDecision:
    """Result of one watchdog evaluation."""

    publish_stop: bool = False
    timed_out: bool = False


def _clip(value: float, limit: float) -> float:
    """Return ``value`` symmetrically limited by a validated limit."""
    return max(-limit, min(limit, value))


def _positive_seconds(name: str, value: float) -> int:
    """Validate a positive duration and convert it to integer nanoseconds."""
    if not math.isfinite(value) or value <= 0.0:
        raise ValueError(f'{name} must be greater than zero')
    nanoseconds = int(value * NANOSECONDS_PER_SECOND)
    if nanoseconds <= 0:
        raise ValueError(f'{name} must be at least one nanosecond')
    return nanoseconds


def _positive_limit(name: str, value: float) -> float:
    """Validate a finite, strictly positive command limit."""
    if not math.isfinite(value) or value <= 0.0:
        raise ValueError(f'{name} must be finite and greater than zero')
    return value


class CommandSafetyPolicy:
    """Deterministic state and timing policy used by the ROS node."""

    def __init__(
        self,
        *,
        max_linear_mps: float,
        max_angular_radps: float,
        command_timeout_sec: float,
        stop_publish_period_sec: float,
        start_time_ns: int,
    ):
        self.max_linear_mps = _positive_limit(
            'max_linear_mps', max_linear_mps
        )
        self.max_angular_radps = _positive_limit(
            'max_angular_radps', max_angular_radps
        )
        self.command_timeout_ns = _positive_seconds(
            'command_timeout_sec', command_timeout_sec
        )
        self.stop_publish_period_ns = _positive_seconds(
            'stop_publish_period_sec', stop_publish_period_sec
        )

        self.mode = DriveMode.ROVER
        self.state = SafetyState.NORMAL
        self.last_command_ns = start_time_ns
        self.last_stop_publish_ns: Optional[int] = None

    def accept_command(
        self, linear_x: float, angular_z: float, now_ns: int
    ) -> CommandDecision:
        """Accept and clip a command only while the rover is drive-enabled."""
        if self.mode != DriveMode.ROVER:
            return CommandDecision(publish=False)
        if not math.isfinite(linear_x) or not math.isfinite(angular_z):
            return CommandDecision(publish=False)

        recovered = self.state != SafetyState.NORMAL
        self.last_command_ns = now_ns
        self.last_stop_publish_ns = None
        self.state = SafetyState.NORMAL
        return CommandDecision(
            publish=True,
            linear_x=_clip(linear_x, self.max_linear_mps),
            angular_z=_clip(angular_z, self.max_angular_radps),
            recovered=recovered,
        )

    def change_mode(self, raw_mode: int, now_ns: int) -> ModeDecision:
        """Validate and apply a mode, forcing an immediate stop when needed."""
        try:
            new_mode = DriveMode(raw_mode)
        except ValueError:
            return ModeDecision(accepted=False)

        previous = self.mode
        if new_mode == previous:
            return ModeDecision(
                accepted=True,
                previous=previous,
                current=new_mode,
            )

        self.mode = new_mode
        if new_mode == DriveMode.ROVER:
            # A fresh driving command is required after HOLD or EMERGENCY.
            self.state = SafetyState.STALE
            return ModeDecision(
                accepted=True,
                changed=True,
                previous=previous,
                current=new_mode,
            )

        self.state = (
            SafetyState.HOLD
            if new_mode == DriveMode.HOLD
            else SafetyState.EMERGENCY
        )
        self.last_stop_publish_ns = now_ns
        return ModeDecision(
            accepted=True,
            changed=True,
            publish_stop=True,
            previous=previous,
            current=new_mode,
        )

    def evaluate_watchdog(self, now_ns: int) -> WatchdogDecision:
        """Update staleness and rate-limit periodic zero-command publication."""
        timed_out = False

        if now_ns < self.last_command_ns:
            # Simulated time can jump backwards when a world is reset.
            self.last_command_ns = now_ns

        if self.mode == DriveMode.ROVER and self.state == SafetyState.NORMAL:
            if now_ns - self.last_command_ns > self.command_timeout_ns:
                self.state = SafetyState.STALE
                timed_out = True

        if self.state == SafetyState.NORMAL:
            return WatchdogDecision(timed_out=timed_out)

        if (
            self.last_stop_publish_ns is not None
            and now_ns < self.last_stop_publish_ns
        ):
            self.last_stop_publish_ns = None

        stop_due = (
            self.last_stop_publish_ns is None
            or now_ns - self.last_stop_publish_ns
            >= self.stop_publish_period_ns
        )
        if stop_due:
            self.last_stop_publish_ns = now_ns

        return WatchdogDecision(
            publish_stop=stop_due,
            timed_out=timed_out,
        )


class CommandSafetyNode(Node):
    """ROS wrapper around the backend-neutral command-safety policy."""

    def __init__(self):
        super().__init__('space_command_safety')

        self.declare_parameter('input_topic', '/cmd_vel_in')
        self.declare_parameter('output_topic', '/cmd_vel_safe')
        self.declare_parameter('mode_topic', '/space/mode')
        self.declare_parameter('max_linear_mps', 0.30)
        self.declare_parameter('max_angular_radps', 0.80)
        self.declare_parameter('command_timeout_sec', 0.50)
        self.declare_parameter('watchdog_period_sec', 0.05)
        self.declare_parameter('stop_publish_period_sec', 0.20)

        input_topic = self.get_parameter('input_topic').value
        output_topic = self.get_parameter('output_topic').value
        mode_topic = self.get_parameter('mode_topic').value
        command_timeout_sec = float(
            self.get_parameter('command_timeout_sec').value
        )
        watchdog_period_sec = float(
            self.get_parameter('watchdog_period_sec').value
        )
        stop_publish_period_sec = float(
            self.get_parameter('stop_publish_period_sec').value
        )

        _positive_seconds('watchdog_period_sec', watchdog_period_sec)
        self._policy = CommandSafetyPolicy(
            max_linear_mps=float(
                self.get_parameter('max_linear_mps').value
            ),
            max_angular_radps=float(
                self.get_parameter('max_angular_radps').value
            ),
            command_timeout_sec=command_timeout_sec,
            stop_publish_period_sec=stop_publish_period_sec,
            start_time_ns=self._now_ns(),
        )

        self._command_publisher = self.create_publisher(
            Twist, output_topic, 10
        )
        self.create_subscription(
            Twist, input_topic, self._on_command, 10
        )
        self.create_subscription(UInt8, mode_topic, self._on_mode, 10)
        self.create_timer(watchdog_period_sec, self._on_watchdog)

        self.get_logger().info(
            f'Command safety ready: {input_topic} -> {output_topic}; '
            f'mode topic={mode_topic}, timeout={command_timeout_sec:.3f}s'
        )

    def _now_ns(self) -> int:
        return self.get_clock().now().nanoseconds

    def _publish_stop(self):
        self._command_publisher.publish(Twist())

    def _on_command(self, message: Twist):
        decision = self._policy.accept_command(
            message.linear.x,
            message.angular.z,
            self._now_ns(),
        )
        if not decision.publish:
            return

        if decision.recovered:
            self.get_logger().info('Fresh command received; watchdog recovered')

        limited = Twist()
        limited.linear.x = decision.linear_x
        limited.angular.z = decision.angular_z
        self._command_publisher.publish(limited)

    def _on_mode(self, message: UInt8):
        decision = self._policy.change_mode(message.data, self._now_ns())
        if not decision.accepted:
            return
        if not decision.changed:
            return

        self.get_logger().info(
            f'Mode changed: {decision.previous.name} -> '
            f'{decision.current.name}'
        )
        if decision.publish_stop:
            self._publish_stop()

    def _on_watchdog(self):
        decision = self._policy.evaluate_watchdog(self._now_ns())
        if decision.timed_out:
            self.get_logger().warn('Command timeout; entering STALE state')
        if decision.publish_stop:
            self._publish_stop()


def main(args=None):
    """Run the command-safety node."""
    rclpy.init(args=args)
    node = CommandSafetyNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            node.destroy_node()
            rclpy.try_shutdown()
        except KeyboardInterrupt:
            # A second signal during launch shutdown should not print a
            # traceback from this node.
            pass


if __name__ == '__main__':
    main()
