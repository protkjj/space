#!/usr/bin/env python3
"""
Translate backend-neutral commands into ArduPilot DDS commands.

The adapter consumes ``/cmd_vel_safe`` (``geometry_msgs/msg/Twist``) from
``space_controller`` and republishes it as a stamped, frame-tagged
``geometry_msgs/msg/TwistStamped`` on ``/ap/cmd_vel``, which the ArduPilot
AP_DDS client subscribes to.

Responsibilities assigned to this package by ``docs/architecture.md``:

* command timestamps
* frame selection and validation
* ArduPilot mode and pre-arm/arming management
* vehicle-state monitoring
* communication-loss detection

One-way state barrier
---------------------
Vehicle state is consumed only for safety decisions: liveness, arm state, and
mode. No autopilot *estimate* is retained. This matters because a companion
computer that sends odometry to the autopilot must not feed the autopilot's
own fused estimate back into the estimator producing that odometry. Doing so
counts the same information twice, shrinking the fused covariance while the
true error stays put, so the system grows confident exactly as it drifts. That
failure is silent, so the boundary is kept structural rather than by comment.

On builds that publish ``ardupilot_msgs/msg/Status`` the adapter uses it, which
carries no pose at all. On builds without it, the adapter falls back to a pose
topic and keeps only the arrival time, never the value.
"""

from dataclasses import dataclass
from enum import Enum, IntEnum
import math
from typing import Optional

from geometry_msgs.msg import PoseStamped, Twist, TwistStamped
import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from std_srvs.srv import Trigger

try:
    from ardupilot_msgs.srv import ArmMotors, ModeSwitch
    ARDUPILOT_MSGS_AVAILABLE = True
except ImportError:  # pragma: no cover - depends on external workspace
    ArmMotors = None
    ModeSwitch = None
    ARDUPILOT_MSGS_AVAILABLE = False

try:
    # Added in ArduPilot 4.7; absent on earlier builds.
    from ardupilot_msgs.msg import Status
    STATUS_MSG_AVAILABLE = True
except ImportError:  # pragma: no cover - depends on the pinned firmware
    Status = None
    STATUS_MSG_AVAILABLE = False


NANOSECONDS_PER_SECOND = 1_000_000_000


class RoverMode(IntEnum):
    """
    ArduPilot Rover mode numbers.

    Values are taken from ``Rover/mode.h`` at the pinned firmware revision
    recorded in ``firmware/ardupilot/version.txt``. They are not guessed and
    must be re-checked if that pin changes.
    """

    MANUAL = 0
    HOLD = 4
    GUIDED = 15


class LinkState(Enum):
    """Health of the link to the autopilot, as observed by this node."""

    NEVER_SEEN = 'never_seen'
    ALIVE = 'alive'
    LOST = 'lost'


class PrepStep(Enum):
    """Progress through the pre-arm, mode, and arming sequence."""

    IDLE = 'idle'
    PREARM = 'prearm'
    MODE = 'mode'
    ARM = 'arm'
    READY = 'ready'


class CommandState(Enum):
    """Freshness of the upstream command stream."""

    NEVER_COMMANDED = 'never_commanded'
    FRESH = 'fresh'
    STALE = 'stale'


@dataclass(frozen=True)
class PublishDecision:
    """Result of asking the policy what to send to ArduPilot."""

    publish: bool = False
    linear_x: float = 0.0
    angular_z: float = 0.0
    is_stop: bool = False
    reason: str = ''


def _positive_seconds(name: str, value: float) -> int:
    """Validate a positive duration and convert it to integer nanoseconds."""
    if not math.isfinite(value) or value <= 0.0:
        raise ValueError(f'{name} must be finite and greater than zero')
    nanoseconds = int(value * NANOSECONDS_PER_SECOND)
    if nanoseconds <= 0:
        raise ValueError(f'{name} must be at least one nanosecond')
    return nanoseconds


def _non_empty(name: str, value: str) -> str:
    """Validate that a string parameter is present and not blank."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{name} must be a non-empty string')
    return value


class AdapterPolicy:
    """
    Deterministic timing and state policy, independent of ROS.

    Kept free of ROS types so the stale/communication-loss behaviour required
    by Milestone A can be unit-tested without spinning a node.
    """

    def __init__(
        self,
        *,
        command_timeout_sec: float,
        link_timeout_sec: float,
        start_time_ns: int,
    ):
        self.command_timeout_ns = _positive_seconds(
            'command_timeout_sec', command_timeout_sec
        )
        self.link_timeout_ns = _positive_seconds(
            'link_timeout_sec', link_timeout_sec
        )

        self._start_time_ns = start_time_ns
        self._last_command_ns: Optional[int] = None
        self._last_state_ns: Optional[int] = None
        self._linear_x = 0.0
        self._angular_z = 0.0

        self.command_state = CommandState.NEVER_COMMANDED
        self.link_state = LinkState.NEVER_SEEN

        # Reported vehicle state. None means the build does not publish it,
        # which is not the same as knowing the vehicle is disarmed.
        self.armed: Optional[bool] = None
        self.mode: Optional[int] = None
        self.external_control: Optional[bool] = None

    def accept_command(
        self, linear_x: float, angular_z: float, now_ns: int
    ) -> bool:
        """Store a validated command. Returns False if it was rejected."""
        if not math.isfinite(linear_x) or not math.isfinite(angular_z):
            return False

        self._linear_x = linear_x
        self._angular_z = angular_z
        self._last_command_ns = now_ns
        self.command_state = CommandState.FRESH
        return True

    def note_vehicle_state(
        self,
        now_ns: int,
        *,
        armed: Optional[bool] = None,
        mode: Optional[int] = None,
        external_control: Optional[bool] = None,
    ) -> bool:
        """
        Record that the autopilot was heard from, and what it reported.

        Only safety-relevant state is kept: liveness, arm state, and mode. No
        autopilot estimate is retained; see the one-way state barrier in the
        module docstring. Returns True if this recovered a lost link.
        """
        recovered = self.link_state == LinkState.LOST
        self._last_state_ns = now_ns
        self.link_state = LinkState.ALIVE
        if armed is not None:
            self.armed = armed
        if mode is not None:
            self.mode = mode
        if external_control is not None:
            self.external_control = external_control
        return recovered

    def command_blockers(self, expected_mode: Optional[int] = None) -> list:
        """
        Return reported reasons a command would not move the vehicle.

        Reports only what the autopilot actually said. Unknown state is
        reported as unknown rather than assumed healthy, so a build that
        publishes no status never looks like a vehicle that is ready.
        """
        blockers = []
        if self.link_state == LinkState.NEVER_SEEN:
            blockers.append('no vehicle state received yet')
        elif self.link_state == LinkState.LOST:
            blockers.append('autopilot link lost')
        elif self.armed is None:
            # Heard from the vehicle, but this build reports no arm state.
            # Unknown must not read as ready.
            blockers.append('vehicle state not reported by this build')
        if self.armed is False:
            blockers.append('vehicle disarmed')
        if self.external_control is False:
            blockers.append('external control disabled on the autopilot')
        if (
            expected_mode is not None
            and self.mode is not None
            and self.mode != expected_mode
        ):
            blockers.append(
                f'mode is {self.mode}, expected {expected_mode}'
            )
        return blockers

    def _rewind_if_clock_jumped(self, now_ns: int) -> None:
        """Handle simulated time jumping backwards on a world reset."""
        if self._last_command_ns is not None and now_ns < self._last_command_ns:
            self._last_command_ns = now_ns
        if self._last_state_ns is not None and now_ns < self._last_state_ns:
            self._last_state_ns = now_ns
        if now_ns < self._start_time_ns:
            self._start_time_ns = now_ns

    def evaluate(self, now_ns: int) -> PublishDecision:
        """Decide what should be sent to ArduPilot at this instant."""
        self._rewind_if_clock_jumped(now_ns)

        # Communication loss is measured from startup when nothing was ever
        # received, so a never-connected autopilot is reported rather than
        # silently treated as healthy.
        reference_ns = (
            self._last_state_ns
            if self._last_state_ns is not None
            else self._start_time_ns
        )
        if now_ns - reference_ns > self.link_timeout_ns:
            self.link_state = LinkState.LOST

        if self._last_command_ns is None:
            return PublishDecision(reason='no command received yet')

        if now_ns - self._last_command_ns > self.command_timeout_ns:
            self.command_state = CommandState.STALE

        if self.command_state == CommandState.STALE:
            return PublishDecision(
                publish=True, is_stop=True, reason='command stale'
            )

        if self.link_state == LinkState.LOST:
            return PublishDecision(
                publish=True, is_stop=True, reason='autopilot link lost'
            )

        return PublishDecision(
            publish=True,
            linear_x=self._linear_x,
            angular_z=self._angular_z,
            reason='fresh command',
        )


class ArduPilotAdapter(Node):
    """ROS wrapper publishing stamped commands to the ArduPilot DDS client."""

    def __init__(self):
        super().__init__('space_ardupilot_adapter')

        self.declare_parameter('input_topic', '/cmd_vel_safe')
        self.declare_parameter('output_topic', '/ap/cmd_vel')
        self.declare_parameter('status_topic', '/ap/status')
        self.declare_parameter('vehicle_state_topic', '/ap/pose/filtered')
        self.declare_parameter('arm_service', '/ap/arm_motors')
        self.declare_parameter('mode_service', '/ap/mode_switch')
        self.declare_parameter('prearm_service', '/ap/prearm_check')
        self.declare_parameter('frame_id', 'base_link')
        self.declare_parameter('command_timeout_sec', 0.5)
        self.declare_parameter('link_timeout_sec', 3.0)
        self.declare_parameter('publish_rate_hz', 10.0)
        self.declare_parameter('service_timeout_sec', 5.0)
        self.declare_parameter('manage_vehicle', False)
        self.declare_parameter('target_mode', int(RoverMode.GUIDED))

        self._input_topic = _non_empty(
            'input_topic', self.get_parameter('input_topic').value
        )
        self._output_topic = _non_empty(
            'output_topic', self.get_parameter('output_topic').value
        )
        self._status_topic = _non_empty(
            'status_topic', self.get_parameter('status_topic').value
        )
        self._state_topic = _non_empty(
            'vehicle_state_topic',
            self.get_parameter('vehicle_state_topic').value,
        )
        self._frame_id = _non_empty(
            'frame_id', self.get_parameter('frame_id').value
        )
        self._service_timeout_sec = float(
            self.get_parameter('service_timeout_sec').value
        )
        self._manage_vehicle = bool(
            self.get_parameter('manage_vehicle').value
        )
        self._target_mode = int(self.get_parameter('target_mode').value)

        publish_rate_hz = float(self.get_parameter('publish_rate_hz').value)
        if not math.isfinite(publish_rate_hz) or publish_rate_hz <= 0.0:
            raise ValueError('publish_rate_hz must be finite and positive')

        self._policy = AdapterPolicy(
            command_timeout_sec=float(
                self.get_parameter('command_timeout_sec').value
            ),
            link_timeout_sec=float(
                self.get_parameter('link_timeout_sec').value
            ),
            start_time_ns=self._now_ns(),
        )

        # AP_DDS does not use one QoS for everything. Measured on the pinned
        # revision, on SITL and on a Pixhawk 6X over serial: /ap/cmd_vel,
        # /ap/pose/filtered, /ap/twist/filtered, /ap/tf, /ap/rc and /ap/navsat
        # are BEST_EFFORT, while /ap/status and /ap/clock are RELIABLE.
        # Assuming BEST_EFFORT everywhere is what made `ros2 topic echo
        # --qos-reliability best_effort /ap/status` appear to hang on hardware.
        best_effort_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            depth=1,
        )
        reliable_qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE,
            depth=10,
        )

        self._command_publisher = self.create_publisher(
            TwistStamped, self._output_topic, best_effort_qos
        )
        self.create_subscription(
            Twist, self._input_topic, self._on_command, 10
        )
        # Prefer the status topic, which reports arm state and mode and
        # carries no pose. Builds older than ArduPilot 4.7 do not publish it,
        # so fall back to a pose topic used purely as a liveness heartbeat.
        # Status is subscribed RELIABLE to match its publisher: an arm-state
        # or failsafe transition is exactly the message that must not be
        # dropped, and the topic publishes at only 2 Hz when nothing changes.
        if STATUS_MSG_AVAILABLE:
            self.create_subscription(
                Status, self._status_topic, self._on_status, reliable_qos
            )
            self._state_source = self._status_topic
        else:
            self.create_subscription(
                PoseStamped,
                self._state_topic,
                self._on_vehicle_state,
                best_effort_qos,
            )
            self._state_source = f'{self._state_topic} (liveness only)'

        self._arm_client = None
        self._mode_client = None
        self._prearm_client = None
        self._prep_step = PrepStep.IDLE
        self._pending_future = None
        self._pending_step = None
        self._next_prep_ns = 0
        self._prep_retry_ns = _positive_seconds(
            'service_timeout_sec', self._service_timeout_sec
        )
        if self._manage_vehicle:
            self._create_service_clients()

        self._last_reason = ''
        self._last_blockers = None
        self.create_timer(1.0 / publish_rate_hz, self._on_publish_timer)

        self.get_logger().info(
            f'ArduPilot adapter ready: {self._input_topic} -> '
            f'{self._output_topic} (frame_id={self._frame_id}, '
            f'{publish_rate_hz:.1f} Hz)'
        )
        self.get_logger().info(f'Vehicle state from {self._state_source}')
        if self._manage_vehicle:
            self.get_logger().warn(
                'manage_vehicle is true: this node will run pre-arm checks, '
                f'switch to mode {self._target_mode}, and ARM the vehicle '
                'once a fresh command arrives.'
            )
        else:
            self.get_logger().info(
                'manage_vehicle is false: this node will not arm the vehicle '
                'or change its mode. ArduPilot will ignore velocity commands '
                'unless it is already armed and in the target mode.'
            )

    def _now_ns(self) -> int:
        return self.get_clock().now().nanoseconds

    def _create_service_clients(self) -> None:
        """Create arming/mode clients, degrading clearly if types are absent."""
        if not ARDUPILOT_MSGS_AVAILABLE:
            self.get_logger().error(
                'manage_vehicle is true but ardupilot_msgs is not on the '
                'AMENT_PREFIX_PATH. Arming and mode switching are disabled. '
                'Build ardupilot_msgs and source its workspace.'
            )
            return

        self._arm_client = self.create_client(
            ArmMotors, str(self.get_parameter('arm_service').value)
        )
        self._mode_client = self.create_client(
            ModeSwitch, str(self.get_parameter('mode_service').value)
        )
        self._prearm_client = self.create_client(
            Trigger, str(self.get_parameter('prearm_service').value)
        )

    def _begin(self, step, client, request) -> None:
        """Start one step of the arming sequence, if its service is up."""
        if client is None or not client.service_is_ready():
            return
        self._pending_step = step
        self._pending_future = client.call_async(request)

    def _collect(self) -> None:
        """Apply the result of a completed step, or time it out."""
        future = self._pending_future
        if future is None or not future.done():
            return

        step = self._pending_step
        self._pending_future = None
        self._pending_step = None
        result = future.result()
        now_ns = self._now_ns()

        if result is None:
            self.get_logger().warn(f'{step.value}: no response')
            self._next_prep_ns = now_ns + self._prep_retry_ns
            return

        if step == PrepStep.PREARM:
            if result.success:
                self.get_logger().info(f'Pre-arm passed: {result.message}')
                self._prep_step = PrepStep.MODE
            else:
                # Retry rather than fail: pre-arm commonly clears on its own
                # once the vehicle settles, and the message says why.
                self.get_logger().warn(f'Pre-arm: {result.message}')
                self._next_prep_ns = now_ns + self._prep_retry_ns
        elif step == PrepStep.MODE:
            if result.status:
                self.get_logger().info(f'Mode is now {result.curr_mode}')
                self._prep_step = PrepStep.ARM
            else:
                self.get_logger().warn(
                    f'Mode switch refused; vehicle is in {result.curr_mode}'
                )
                self._next_prep_ns = now_ns + self._prep_retry_ns
        elif step == PrepStep.ARM:
            if result.result:
                self.get_logger().info('Vehicle armed')
                self._prep_step = PrepStep.READY
            else:
                # ArduPilot also returns false when already armed, so trust
                # the reported state rather than this result alone.
                if self._policy.armed:
                    self.get_logger().info('Vehicle reports already armed')
                    self._prep_step = PrepStep.READY
                else:
                    self.get_logger().warn(
                        'Arming refused; see the autopilot pre-arm messages'
                    )
                    self._next_prep_ns = now_ns + self._prep_retry_ns

    def _advance_vehicle_prep(self) -> None:
        """
        Drive the pre-arm, mode, and arming sequence.

        Only runs while there is a fresh upstream command. Arming a vehicle
        that nobody is currently commanding is not something this node should
        do on its own, and it would arm on startup rather than on intent.
        """
        if not self._manage_vehicle or self._arm_client is None:
            return

        self._collect()
        if self._pending_future is not None:
            return

        # If the vehicle disarms or leaves the target mode underneath us, for
        # example because a pilot took over on the RC switch, restart the
        # sequence rather than assuming the earlier success still holds.
        if self._prep_step == PrepStep.READY:
            left_mode = (
                self._policy.mode is not None
                and self._policy.mode != self._target_mode
            )
            if self._policy.armed is False or left_mode:
                self.get_logger().warn(
                    'Vehicle left the armed target state; re-running the '
                    'arming sequence'
                )
                self._prep_step = PrepStep.IDLE
            return

        if self._policy.command_state != CommandState.FRESH:
            return
        now_ns = self._now_ns()
        if now_ns < self._next_prep_ns:
            return

        if self._prep_step == PrepStep.IDLE:
            self._prep_step = PrepStep.PREARM

        if self._prep_step == PrepStep.PREARM:
            self._begin(PrepStep.PREARM, self._prearm_client,
                        Trigger.Request())
        elif self._prep_step == PrepStep.MODE:
            self._begin(PrepStep.MODE, self._mode_client,
                        ModeSwitch.Request(mode=self._target_mode))
        elif self._prep_step == PrepStep.ARM:
            self._begin(PrepStep.ARM, self._arm_client,
                        ArmMotors.Request(arm=True))

    def _on_command(self, message: Twist) -> None:
        """Accept an upstream backend-neutral command."""
        accepted = self._policy.accept_command(
            message.linear.x, message.angular.z, self._now_ns()
        )
        if not accepted:
            self.get_logger().warn(
                'Rejected command with non-finite velocity component'
            )

    def _on_status(self, message) -> None:
        """Record arm state, mode, and external-control state."""
        if self._policy.note_vehicle_state(
            self._now_ns(),
            armed=bool(message.armed),
            mode=int(message.mode),
            external_control=bool(message.external_control),
        ):
            self.get_logger().info('Autopilot link recovered')

    def _on_vehicle_state(self, message: PoseStamped) -> None:
        """
        Note that the autopilot is alive.

        Used only on builds that publish no status topic. The message contents
        are discarded; see the one-way state barrier in the module docstring.
        """
        del message
        if self._policy.note_vehicle_state(self._now_ns()):
            self.get_logger().info('Autopilot link recovered')

    def _report_blockers(self) -> None:
        """Log, on change, why a command would not move the vehicle."""
        blockers = self._policy.command_blockers(self._target_mode)
        if blockers == self._last_blockers:
            return
        self._last_blockers = blockers
        if blockers:
            self.get_logger().warn(
                'Commands will not move the vehicle: ' + '; '.join(blockers)
            )
        else:
            self.get_logger().info('Vehicle reports it can accept commands')

    def _on_publish_timer(self) -> None:
        """Publish the current command, or a stop, at the configured rate."""
        decision = self._policy.evaluate(self._now_ns())

        if decision.reason != self._last_reason:
            self._last_reason = decision.reason
            if decision.is_stop:
                self.get_logger().warn(f'Publishing stop: {decision.reason}')

        self._report_blockers()
        self._advance_vehicle_prep()

        if not decision.publish:
            return

        command = TwistStamped()
        command.header.stamp = self.get_clock().now().to_msg()
        command.header.frame_id = self._frame_id
        command.twist.linear.x = decision.linear_x
        command.twist.angular.z = decision.angular_z
        self._command_publisher.publish(command)


def main(args=None):
    """Run the ArduPilot adapter node."""
    rclpy.init(args=args)
    node = ArduPilotAdapter()
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
