"""Small dependency-free helpers used by the navigation nodes."""

import math


def normalize_angle(angle: float) -> float:
    """Normalize an angle to the closed-open interval [-pi, pi)."""
    return (angle + math.pi) % (2.0 * math.pi) - math.pi


def yaw_to_quaternion(yaw: float) -> tuple[float, float]:
    """Return the z and w components of a planar yaw quaternion."""
    half_yaw = normalize_angle(yaw) * 0.5
    return math.sin(half_yaw), math.cos(half_yaw)


def is_finite_pose(x: float, y: float, qz: float, qw: float) -> bool:
    """Return whether a planar pose has finite values and a valid quaternion."""
    values = (x, y, qz, qw)
    if not all(math.isfinite(value) for value in values):
        return False
    return math.hypot(qz, qw) > 1.0e-6
