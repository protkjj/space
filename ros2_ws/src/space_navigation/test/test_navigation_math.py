"""Unit tests for navigation geometry helpers."""

import math

from space_navigation.navigation_math import (
    is_finite_pose,
    normalize_angle,
    yaw_to_quaternion,
)


def test_normalize_angle_wraps():
    """Angles are wrapped into the expected interval."""
    assert math.isclose(normalize_angle(3.0 * math.pi), -math.pi)
    assert math.isclose(normalize_angle(-0.5 * math.pi), -0.5 * math.pi)


def test_yaw_to_quaternion():
    """A quarter turn produces a unit planar quaternion."""
    qz, qw = yaw_to_quaternion(math.pi / 2.0)
    assert math.isclose(qz, math.sqrt(0.5))
    assert math.isclose(qw, math.sqrt(0.5))


def test_finite_pose_validation():
    """Invalid numeric values and zero quaternions are rejected."""
    assert is_finite_pose(1.0, 2.0, 0.0, 1.0)
    assert not is_finite_pose(math.nan, 2.0, 0.0, 1.0)
    assert not is_finite_pose(1.0, 2.0, 0.0, 0.0)
