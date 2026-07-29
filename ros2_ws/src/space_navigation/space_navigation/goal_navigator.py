#!/usr/bin/env python3
"""Forward RViz goal poses to Nav2's NavigateToPose action server."""

from functools import partial
import math

from action_msgs.msg import GoalStatus
from geometry_msgs.msg import PointStamped, PoseStamped
from nav2_msgs.action import NavigateToPose
import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from space_navigation.navigation_math import is_finite_pose
from std_msgs.msg import String


STATUS_NAMES = {
    GoalStatus.STATUS_UNKNOWN: 'unknown',
    GoalStatus.STATUS_ACCEPTED: 'accepted',
    GoalStatus.STATUS_EXECUTING: 'executing',
    GoalStatus.STATUS_CANCELING: 'canceling',
    GoalStatus.STATUS_SUCCEEDED: 'succeeded',
    GoalStatus.STATUS_CANCELED: 'canceled',
    GoalStatus.STATUS_ABORTED: 'aborted',
}


class GoalNavigator(Node):
    """Accept point-and-click targets and manage Nav2 navigation goals."""

    def __init__(self):
        super().__init__('space_goal_navigator')
        self.declare_parameter('goal_topic', '/goal_pose')
        self.declare_parameter('clicked_point_topic', '/clicked_point')
        self.declare_parameter('action_name', 'navigate_to_pose')
        self.declare_parameter('default_goal_frame', 'odom')
        self.declare_parameter('accept_clicked_point', True)
        self.declare_parameter('server_retry_period', 0.5)

        goal_topic = self.get_parameter('goal_topic').value
        clicked_topic = self.get_parameter('clicked_point_topic').value
        action_name = self.get_parameter('action_name').value
        retry_period = float(
            self.get_parameter('server_retry_period').value
        )
        if retry_period <= 0.0 or not math.isfinite(retry_period):
            raise ValueError('server_retry_period must be finite and positive')

        self._client = ActionClient(self, NavigateToPose, action_name)
        self._status_pub = self.create_publisher(
            String, '~/navigation_status', 10
        )
        self._goal_sub = self.create_subscription(
            PoseStamped, goal_topic, self._on_goal_pose, 10
        )
        self._point_sub = None
        if self.get_parameter('accept_clicked_point').value:
            self._point_sub = self.create_subscription(
                PointStamped, clicked_topic, self._on_clicked_point, 10
            )

        self._pending_goal = None
        self._latest_sequence = 0
        self._active_handle = None
        self._server_timer = self.create_timer(
            retry_period, self._try_send_pending
        )
        self._publish_status('waiting_for_goal')
        self.get_logger().info(
            f'Waiting for goals on {goal_topic}; Nav2 action is {action_name}'
        )

    def _publish_status(self, status: str) -> None:
        message = String()
        message.data = status
        self._status_pub.publish(message)

    def _on_clicked_point(self, point: PointStamped) -> None:
        goal = PoseStamped()
        goal.header = point.header
        goal.pose.position = point.point
        goal.pose.orientation.w = 1.0
        self._on_goal_pose(goal)

    def _on_goal_pose(self, goal: PoseStamped) -> None:
        if not goal.header.frame_id:
            goal.header.frame_id = self.get_parameter(
                'default_goal_frame'
            ).value

        position = goal.pose.position
        orientation = goal.pose.orientation
        if not is_finite_pose(
            position.x, position.y, orientation.z, orientation.w
        ):
            self.get_logger().error('Rejected a non-finite or invalid goal')
            self._publish_status('goal_rejected_invalid_pose')
            return

        self._latest_sequence += 1
        self._pending_goal = (self._latest_sequence, goal)
        self._publish_status('goal_queued')
        self.get_logger().info(
            f'Goal #{self._latest_sequence}: '
            f'({position.x:.2f}, {position.y:.2f}) '
            f'in {goal.header.frame_id}'
        )
        self._try_send_pending()

    def _try_send_pending(self) -> None:
        if self._pending_goal is None:
            return
        if not self._client.server_is_ready():
            self._publish_status('waiting_for_nav2')
            return

        sequence, pose = self._pending_goal
        self._pending_goal = None
        goal = NavigateToPose.Goal()
        goal.pose = pose
        future = self._client.send_goal_async(
            goal,
            feedback_callback=partial(self._on_feedback, sequence),
        )
        future.add_done_callback(
            partial(self._on_goal_response, sequence)
        )
        self._publish_status('goal_sending')

    def _on_goal_response(self, sequence: int, future) -> None:
        try:
            handle = future.result()
        except Exception as error:  # ROS futures surface middleware failures.
            self.get_logger().error(f'Failed to send goal: {error}')
            self._publish_status('goal_send_failed')
            return

        if not handle.accepted:
            self.get_logger().error(f'Nav2 rejected goal #{sequence}')
            self._publish_status('goal_rejected_by_nav2')
            return

        if sequence != self._latest_sequence:
            handle.cancel_goal_async()
            return

        self._active_handle = handle
        self._publish_status('navigating')
        self.get_logger().info(f'Nav2 accepted goal #{sequence}')
        result_future = handle.get_result_async()
        result_future.add_done_callback(
            partial(self._on_result, sequence, handle)
        )

    def _on_feedback(self, sequence: int, feedback_message) -> None:
        if sequence != self._latest_sequence:
            return
        feedback = feedback_message.feedback
        distance = feedback.distance_remaining
        self._publish_status(f'navigating:{distance:.2f}m_remaining')

    def _on_result(self, sequence: int, handle, future) -> None:
        try:
            wrapped_result = future.result()
            status = STATUS_NAMES.get(
                wrapped_result.status, f'code_{wrapped_result.status}'
            )
        except Exception as error:  # ROS futures surface middleware failures.
            self.get_logger().error(f'Navigation result failed: {error}')
            status = 'result_failed'

        if self._active_handle is handle:
            self._active_handle = None
        if sequence != self._latest_sequence:
            return

        self._publish_status(status)
        if status == 'succeeded':
            self.get_logger().info(f'Goal #{sequence} reached')
        else:
            self.get_logger().warning(
                f'Goal #{sequence} finished with status: {status}'
            )


def main(args=None):
    """Run the goal-to-action bridge."""
    rclpy.init(args=args)
    node = GoalNavigator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
