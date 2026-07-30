"""Unit tests for the dependency-free slip helpers."""

from space_mission.slip_math import compute_slip, wheel_linear_speed


def test_wheel_linear_speed_averages_sides():
    # 10 rad/s on both sides, r=0.1 -> 1.0 m/s forward.
    assert wheel_linear_speed([10.0, 10.0], [10.0, 10.0], 0.1) == 1.0


def test_wheel_linear_speed_requires_both_sides():
    """
    One side alone must yield None, not a plausible speed.

    This test previously asserted the opposite -- that a missing side returns a
    one-sided average -- which froze a defect into the contract. Skid-steer
    forward speed is the mean of the two sides, so a one-sided figure is the
    speed of a rover that is turning, reported as straight-line travel, and it
    would flow into the slip ratio as a valid reading.
    """
    assert wheel_linear_speed([10.0], [], 0.1) is None
    assert wheel_linear_speed([], [10.0], 0.1) is None
    assert wheel_linear_speed([], [], 0.1) is None


def test_no_slip_when_actual_matches_wheel():
    assert compute_slip(1.0, 1.0, 0.03) == 0.0


def test_positive_slip_when_wheel_outruns_body():
    # Wheels spin at 1.0 m/s, body only moves 0.6 -> 40% slip.
    assert abs(compute_slip(1.0, 0.6, 0.03) - 0.4) < 1e-9


def test_none_below_min_wheel_speed():
    assert compute_slip(0.01, 0.0, 0.03) is None


def test_slip_is_clamped():
    # Body moving backwards relative to wheels cannot exceed the clamp.
    assert compute_slip(1.0, -5.0, 0.03) == 1.0
    assert compute_slip(1.0, 5.0, 0.03) == -1.0


def test_none_on_non_finite():
    assert compute_slip(float('nan'), 0.5, 0.03) is None
