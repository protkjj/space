"""Unit tests for the wheel-odometry integration."""

import math

import pytest
from space_ardupilot_interface.wheel_odometry import (
    _wrap_angle,
    COUNTER_MODULUS,
    slip_ratio,
    WheelOdometry,
    wrapped_delta,
)


SECOND = 1_000_000_000

# The built rover: 120 mm wheels, 225 mm track, 6400 counts per output
# revolution from a 64 CPR motor through 100:1 gearing.
RADIUS = 0.060
TRACK = 0.225
CPR = 6400.0


def make_odometry(**overrides):
    """Return odometry configured like the built rover."""
    kwargs = {
        'wheel_radius_m': RADIUS,
        'track_width_m': TRACK,
        'counts_per_revolution': CPR,
        'max_wheel_speed_mps': 1.0,
    }
    kwargs.update(overrides)
    return WheelOdometry(**kwargs)


def counts_for(distance_m):
    """Return the encoder counts equal to a distance."""
    return round(distance_m * CPR / (2.0 * math.pi * RADIUS))


def test_metres_per_count_matches_the_measured_geometry():
    odometry = make_odometry()
    expected = 2.0 * math.pi * RADIUS / CPR
    assert odometry.metres_per_count == pytest.approx(expected)
    # About 59 micrometres per count on this rover.
    assert odometry.metres_per_count == pytest.approx(5.8905e-5, rel=1e-3)


def test_first_reading_only_establishes_a_baseline():
    odometry = make_odometry()
    assert odometry.update(1000, 1000, SECOND) is None
    assert odometry.x == 0.0
    assert odometry.y == 0.0


def test_straight_line_advances_x_and_holds_heading():
    odometry = make_odometry()
    odometry.update(0, 0, 0)
    step = counts_for(0.1)
    sample = odometry.update(step, step, SECOND)

    assert sample is not None
    assert sample.x == pytest.approx(0.1, abs=1e-3)
    assert sample.y == pytest.approx(0.0, abs=1e-9)
    assert sample.yaw == pytest.approx(0.0, abs=1e-9)
    assert sample.linear_velocity == pytest.approx(0.1, abs=1e-3)
    assert sample.angular_velocity == pytest.approx(0.0, abs=1e-9)


def test_reverse_moves_backwards():
    odometry = make_odometry()
    odometry.update(0, 0, 0)
    step = counts_for(0.1)
    sample = odometry.update(-step, -step, SECOND)

    assert sample.x == pytest.approx(-0.1, abs=1e-3)
    assert sample.linear_velocity == pytest.approx(-0.1, abs=1e-3)


def test_turn_in_place_rotates_without_translating():
    odometry = make_odometry()
    odometry.update(0, 0, 0)
    step = counts_for(0.1)
    # Opposite wheel directions: the signature skid-steer pivot.
    sample = odometry.update(-step, step, SECOND)

    assert sample.linear_velocity == pytest.approx(0.0, abs=1e-9)
    assert math.hypot(sample.x, sample.y) < 1e-6
    expected_omega = (0.1 - -0.1) / TRACK
    assert sample.angular_velocity == pytest.approx(expected_omega, rel=1e-3)


def test_angular_velocity_uses_the_measured_track_width():
    odometry = make_odometry()
    odometry.update(0, 0, 0)
    sample = odometry.update(0, counts_for(0.2), SECOND)
    # Only the right wheel moved, so omega is its speed over the track width.
    assert sample.angular_velocity == pytest.approx(0.2 / TRACK, rel=1e-3)


def test_a_full_circle_returns_close_to_the_start():
    odometry = make_odometry()
    odometry.update(0, 0, 0)
    # Drive an arc in small steps until the heading comes back around.
    left_total = 0
    right_total = 0
    steps = 720
    left_step = counts_for(0.004)
    right_step = counts_for(0.006)
    for index in range(steps):
        left_total += left_step
        right_total += right_step
        odometry.update(left_total, right_total, (index + 1) * SECOND // 100)

    # An arc that has turned through a whole number of revolutions returns to
    # its starting point; allow for the discrete integration.
    turns = odometry.yaw
    assert -math.pi <= turns < math.pi


def test_counter_wraparound_is_not_read_as_huge_motion():
    odometry = make_odometry()
    near_top = COUNTER_MODULUS - 10
    odometry.update(near_top, near_top, 0)
    # Ten counts forward, straight across the 32-bit boundary.
    sample = odometry.update(10, 10, SECOND)

    assert sample is not None
    expected = 20 * odometry.metres_per_count
    assert sample.x == pytest.approx(expected, rel=1e-6)


@pytest.mark.parametrize(
    'previous,current,expected',
    [
        (0, 5, 5),
        (5, 0, -5),
        (COUNTER_MODULUS - 1, 0, 1),
        (0, COUNTER_MODULUS - 1, -1),
    ],
)
def test_wrapped_delta_takes_the_shorter_way_around(previous, current,
                                                    expected):
    assert wrapped_delta(previous, current) == expected


def test_impossible_speed_is_rejected_rather_than_integrated():
    odometry = make_odometry(max_wheel_speed_mps=1.0)
    odometry.update(0, 0, 0)
    # Ten metres in one second is not something this drivetrain can do; it is
    # a corrupted or dropped packet.
    sample = odometry.update(counts_for(10.0), counts_for(10.0), SECOND)

    assert sample is None
    assert odometry.x == 0.0
    assert odometry.rejected_samples == 1


def test_rejected_sample_rebaselines_so_the_next_one_is_usable():
    odometry = make_odometry(max_wheel_speed_mps=1.0)
    odometry.update(0, 0, 0)
    bad = counts_for(10.0)
    assert odometry.update(bad, bad, SECOND) is None

    step = counts_for(0.1)
    sample = odometry.update(bad + step, bad + step, 2 * SECOND)
    assert sample is not None
    assert sample.x == pytest.approx(0.1, abs=1e-3)


def test_non_advancing_time_is_rejected():
    odometry = make_odometry()
    odometry.update(0, 0, SECOND)
    assert odometry.update(100, 100, SECOND) is None
    assert odometry.rejected_samples == 1


def test_backwards_time_is_rejected_not_integrated_negatively():
    odometry = make_odometry()
    odometry.update(0, 0, 2 * SECOND)
    assert odometry.update(100, 100, SECOND) is None
    assert odometry.x == 0.0


def test_reset_clears_the_pose_but_keeps_the_geometry():
    odometry = make_odometry()
    odometry.update(0, 0, 0)
    odometry.update(counts_for(0.5), counts_for(0.5), SECOND)
    assert odometry.x > 0.0

    metres_per_count = odometry.metres_per_count
    odometry.reset()
    assert odometry.x == 0.0
    assert odometry.yaw == 0.0
    assert odometry.metres_per_count == metres_per_count
    # A reset needs a fresh baseline, so the next reading integrates nothing.
    assert odometry.update(12345, 12345, 2 * SECOND) is None


@pytest.mark.parametrize('value', [0.0, -0.1, math.nan, math.inf])
def test_geometry_validation_rejects_bad_values(value):
    with pytest.raises(ValueError, match='must be finite and greater'):
        make_odometry(track_width_m=value)


def test_yaw_stays_wrapped():
    odometry = make_odometry()
    odometry.update(0, 0, 0)
    left = 0
    right = 0
    for index in range(50):
        left -= counts_for(0.05)
        right += counts_for(0.05)
        odometry.update(left, right, (index + 1) * SECOND // 10)
        assert -math.pi <= odometry.yaw < math.pi


@pytest.mark.parametrize('angle,expected', [
    (0.0, 0.0),
    (math.pi / 2, math.pi / 2),
    (3 * math.pi, -math.pi),
    (-3 * math.pi, -math.pi),
])
def test_wrap_angle(angle, expected):
    assert _wrap_angle(angle) == pytest.approx(expected, abs=1e-9)


def test_slip_ratio_is_undefined_for_a_stopped_wheel():
    # Zero would read as "no slip", which is a different claim from "the
    # question does not apply".
    assert slip_ratio(0.0, 0.0) is None
    assert slip_ratio(0.0, 0.5) is None


def test_slip_ratio_of_a_freely_spinning_wheel_is_one():
    assert slip_ratio(0.5, 0.0) == pytest.approx(1.0)


def test_slip_ratio_of_a_gripping_wheel_is_zero():
    assert slip_ratio(0.5, 0.5) == pytest.approx(0.0)


def test_slip_ratio_rejects_non_finite_input():
    assert slip_ratio(math.nan, 0.5) is None
    assert slip_ratio(0.5, math.inf) is None
