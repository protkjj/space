"""
Pure slip-estimation helpers (no ROS dependency, unit-testable).

Kept dependency-free like ``space_navigation.navigation_math`` so the slip
arithmetic can be exercised in isolation.
"""

import math


def wheel_linear_speed(left_speeds, right_speeds, wheel_radius):
    """
    Return the forward speed implied by the wheel angular velocities.

    ``left_speeds`` / ``right_speeds`` are wheel joint angular velocities
    (rad/s). Skid-steer forward speed is the mean of the two side surface
    speeds. This is the *encoder* view of motion: it counts wheel rotation
    whether or not the chassis moved, so slip inflates it exactly as it would
    inflate a real RoboClaw encoder reading.
    """
    if not left_speeds or not right_speeds:
        # Returning a one-sided average here would be worse than returning
        # nothing: skid-steer forward speed is the mean of the two sides, so a
        # single side is the speed of a rover that is turning, reported as if it
        # were driving straight. The caller must treat this as "no reading".
        return None
    left = sum(left_speeds) / len(left_speeds)
    right = sum(right_speeds) / len(right_speeds)
    return (left + right) / 2.0 * wheel_radius


def compute_slip(v_wheel, v_actual, min_wheel_speed):
    """
    Return the slip ratio lambda, or ``None`` when speed is too low to judge.

    ``lambda = (V_wheel - V_actual) / V_wheel`` (the Wong/Bekker slip ratio).

    ``v_actual`` MUST come from a wheel-independent source (VIO); feeding a
    wheel-derived estimate here makes the metric circular (mission doc 1.3).
    The result is clamped to ``[-1, 1]`` and is a *relative* indicator, not a
    precise measurement (mission doc 1.3): "this patch slips more than that
    one" survives VIO error, an absolute percentage does not.
    """
    if not (math.isfinite(v_wheel) and math.isfinite(v_actual)):
        return None
    if abs(v_wheel) < min_wheel_speed:
        return None
    lam = (v_wheel - v_actual) / v_wheel
    return max(-1.0, min(1.0, lam))
