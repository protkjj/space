"""
Launch tests for the ArduPilot adapter node.

These tests deliberately do not require a running ArduPilot or SITL. They
launch the adapter, drive its input, and assert on what it publishes, so the
command contract is checked in CI on a machine with no autopilot attached.
Behaviour that genuinely needs an autopilot is recorded in
``firmware/ardupilot/README.md`` instead of being faked here.
"""

import time
import unittest

from geometry_msgs.msg import Twist, TwistStamped
import launch
import launch_ros.actions
import launch_testing
import launch_testing.actions
import pytest
import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy


COMMAND_TIMEOUT_SEC = 0.5
PUBLISH_RATE_HZ = 20.0
OUTPUT_TOPIC = '/ap/cmd_vel'
INPUT_TOPIC = '/cmd_vel_safe'
FRAME_ID = 'base_link'


@pytest.mark.launch_test
def generate_test_description():
    """Launch the adapter with short, deterministic test timings."""
    adapter = launch_ros.actions.Node(
        package='space_ardupilot_interface',
        executable='ardupilot_adapter',
        name='space_ardupilot_adapter',
        output='screen',
        parameters=[{
            'input_topic': INPUT_TOPIC,
            'output_topic': OUTPUT_TOPIC,
            'frame_id': FRAME_ID,
            'command_timeout_sec': COMMAND_TIMEOUT_SEC,
            'link_timeout_sec': 3600.0,
            'publish_rate_hz': PUBLISH_RATE_HZ,
            'manage_vehicle': False,
        }],
    )
    return (
        launch.LaunchDescription([
            adapter,
            launch_testing.actions.ReadyToTest(),
        ]),
        {'adapter': adapter},
    )


def autopilot_qos():
    """Return the QoS measured on the AP_DDS /ap/cmd_vel subscription."""
    return QoSProfile(
        reliability=ReliabilityPolicy.BEST_EFFORT,
        durability=DurabilityPolicy.VOLATILE,
        depth=10,
    )


class Harness(Node):
    """Publish upstream commands and collect adapter output."""

    def __init__(self):
        super().__init__('adapter_test_harness')
        self.received = []
        self.publisher = self.create_publisher(Twist, INPUT_TOPIC, 10)
        self.create_subscription(
            TwistStamped, OUTPUT_TOPIC, self._on_output, autopilot_qos()
        )

    def _on_output(self, message):
        self.received.append((time.time(), message))

    def spin_for(self, seconds, command=None, rate_hz=10.0):
        """Spin for a duration, optionally publishing a command."""
        end = time.time() + seconds
        period = 1.0 / rate_hz
        next_publish = 0.0
        while time.time() < end:
            rclpy.spin_once(self, timeout_sec=0.01)
            if command is not None and time.time() >= next_publish:
                self.publisher.publish(command)
                next_publish = time.time() + period

    def wait_for_publisher(self, timeout_sec=10.0):
        """Block until the adapter's output publisher is discovered."""
        end = time.time() + timeout_sec
        while time.time() < end:
            rclpy.spin_once(self, timeout_sec=0.1)
            if self.count_publishers(OUTPUT_TOPIC) > 0:
                return True
        return False


class TestAdapterInterface(unittest.TestCase):
    """Interface behaviour that must hold with no autopilot present."""

    @classmethod
    def setUpClass(cls):
        rclpy.init()

    @classmethod
    def tearDownClass(cls):
        rclpy.shutdown()

    def setUp(self):
        self.harness = Harness()

    def tearDown(self):
        self.harness.destroy_node()

    def test_adapter_advertises_the_command_topic(self):
        self.assertTrue(
            self.harness.wait_for_publisher(),
            f'adapter did not advertise {OUTPUT_TOPIC}',
        )

    # "publishes nothing before the first command" is a property of a freshly
    # started node. Every test here shares one launched process, so by the time
    # any given method runs the node may already have been commanded. That
    # property is asserted in test_ardupilot_adapter.py against the policy
    # directly, where the initial state is real rather than simulated.

    def test_command_is_stamped_and_framed(self):
        self.assertTrue(self.harness.wait_for_publisher())
        command = Twist()
        command.linear.x = 0.25
        command.angular.z = -0.4

        self.harness.received.clear()
        self.harness.spin_for(1.5, command=command)
        self.assertGreater(len(self.harness.received), 0)

        _, message = self.harness.received[-1]
        self.assertEqual(message.header.frame_id, FRAME_ID)
        self.assertAlmostEqual(message.twist.linear.x, 0.25, places=6)
        self.assertAlmostEqual(message.twist.angular.z, -0.4, places=6)

        stamp = message.header.stamp
        self.assertTrue(
            stamp.sec > 0 or stamp.nanosec > 0,
            'adapter published an unset timestamp',
        )

    def test_stale_command_produces_zero(self):
        self.assertTrue(self.harness.wait_for_publisher())
        command = Twist()
        command.linear.x = 0.3

        self.harness.spin_for(1.0, command=command)
        self.harness.received.clear()

        # Stop commanding and let the stale timeout elapse.
        self.harness.spin_for(COMMAND_TIMEOUT_SEC + 1.0)
        self.assertGreater(
            len(self.harness.received), 0,
            'adapter stopped publishing entirely instead of publishing zero',
        )

        _, message = self.harness.received[-1]
        self.assertAlmostEqual(message.twist.linear.x, 0.0, places=9)
        self.assertAlmostEqual(message.twist.angular.z, 0.0, places=9)

    def test_zero_arrives_within_the_configured_timeout(self):
        self.assertTrue(self.harness.wait_for_publisher())
        command = Twist()
        command.linear.x = 0.3

        self.harness.spin_for(1.0, command=command)
        self.harness.received.clear()
        stopped_at = time.time()
        self.harness.spin_for(COMMAND_TIMEOUT_SEC + 1.0)

        zeros = [
            (t, m) for t, m in self.harness.received
            if abs(m.twist.linear.x) < 1e-9
        ]
        self.assertGreater(len(zeros), 0, 'adapter never published zero')

        delay = zeros[0][0] - stopped_at
        # Allow one publish period plus transport latency beyond the timeout.
        limit = COMMAND_TIMEOUT_SEC + (1.0 / PUBLISH_RATE_HZ) + 0.5
        self.assertLess(
            delay, limit,
            f'zero command took {delay:.3f}s, expected under {limit:.3f}s',
        )

    def test_recovers_after_a_fresh_command(self):
        self.assertTrue(self.harness.wait_for_publisher())
        command = Twist()
        command.linear.x = 0.3

        self.harness.spin_for(1.0, command=command)
        self.harness.spin_for(COMMAND_TIMEOUT_SEC + 0.5)

        self.harness.received.clear()
        self.harness.spin_for(1.0, command=command)
        self.assertGreater(len(self.harness.received), 0)

        _, message = self.harness.received[-1]
        self.assertAlmostEqual(message.twist.linear.x, 0.3, places=6)


@launch_testing.post_shutdown_test()
class TestAdapterShutdown(unittest.TestCase):
    """The node must exit cleanly when the launch is torn down."""

    def test_exits_without_error(self, proc_info, adapter):
        launch_testing.asserts.assertExitCodes(
            proc_info,
            allowable_exit_codes=[0, -2, -15],
            process=adapter,
        )
