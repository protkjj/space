"""Unit tests for the deterministic command-safety policy."""

import math

import pytest

from space_controller.command_safety import (
    _positive_limit,
    _positive_seconds,
    CommandSafetyPolicy,
    SafetyState,
)
from space_controller.modes import DriveMode


SECOND = 1_000_000_000


def make_policy(start_time_ns=0):
    """Return a policy with short, deterministic test periods."""
    return CommandSafetyPolicy(
        max_linear_mps=0.3,
        max_angular_radps=0.8,
        command_timeout_sec=0.5,
        stop_publish_period_sec=0.2,
        start_time_ns=start_time_ns,
    )


def test_linear_velocity_clipping():
    policy = make_policy()
    decision = policy.accept_command(0.9, 0.0, 1)
    assert decision.publish
    assert decision.linear_x == pytest.approx(0.3)


def test_angular_velocity_clipping():
    policy = make_policy()
    decision = policy.accept_command(0.0, -1.4, 1)
    assert decision.publish
    assert decision.angular_z == pytest.approx(-0.8)


def test_forwarding_in_driving_mode():
    policy = make_policy()
    decision = policy.accept_command(0.12, -0.25, 100)
    assert decision.publish
    assert decision.linear_x == pytest.approx(0.12)
    assert decision.angular_z == pytest.approx(-0.25)
    assert policy.state == SafetyState.NORMAL


@pytest.mark.parametrize(
    ('linear_x', 'angular_z'),
    [
        (math.nan, 0.0),
        (math.inf, 0.0),
        (-math.inf, 0.0),
        (0.0, math.nan),
        (0.0, math.inf),
        (0.0, -math.inf),
    ],
)
def test_non_finite_command_is_rejected(linear_x, angular_z):
    policy = make_policy()
    last_command_ns = policy.last_command_ns

    decision = policy.accept_command(linear_x, angular_z, 100)

    assert not decision.publish
    assert policy.last_command_ns == last_command_ns


@pytest.mark.parametrize(
    ('mode', 'expected_state'),
    [
        (DriveMode.HOLD, SafetyState.HOLD),
        (DriveMode.EMERGENCY, SafetyState.EMERGENCY),
    ],
)
def test_non_driving_mode_publishes_immediate_stop(mode, expected_state):
    policy = make_policy()
    decision = policy.change_mode(mode, 100)
    assert decision.accepted
    assert decision.changed
    assert decision.publish_stop
    assert policy.state == expected_state


def test_periodic_zero_while_stale():
    policy = make_policy()

    first = policy.evaluate_watchdog(int(0.5 * SECOND) + 1)
    assert first.timed_out
    assert first.publish_stop
    assert policy.state == SafetyState.STALE

    too_soon = policy.evaluate_watchdog(int(0.6 * SECOND))
    assert not too_soon.publish_stop

    next_period = policy.evaluate_watchdog(int(0.7 * SECOND) + 1)
    assert next_period.publish_stop


@pytest.mark.parametrize('mode', [DriveMode.HOLD, DriveMode.EMERGENCY])
def test_periodic_zero_while_non_driving_mode_remains_active(mode):
    policy = make_policy()
    transition = policy.change_mode(mode, 10)
    assert transition.publish_stop

    assert not policy.evaluate_watchdog(int(0.1 * SECOND)).publish_stop
    assert policy.evaluate_watchdog(int(0.2 * SECOND) + 10).publish_stop
    assert policy.state != SafetyState.NORMAL


def test_stop_publication_is_not_faster_than_configured():
    policy = make_policy()
    policy.change_mode(DriveMode.HOLD, 0)

    publication_times = [
        now
        for now in range(0, SECOND + 1, int(0.05 * SECOND))
        if policy.evaluate_watchdog(now).publish_stop
    ]
    assert publication_times == [
        int(0.2 * SECOND),
        int(0.4 * SECOND),
        int(0.6 * SECOND),
        int(0.8 * SECOND),
        SECOND,
    ]


def test_fresh_command_recovers_from_stale_state():
    policy = make_policy()
    policy.evaluate_watchdog(int(0.6 * SECOND))
    assert policy.state == SafetyState.STALE

    decision = policy.accept_command(0.1, 0.2, int(0.61 * SECOND))
    assert decision.publish
    assert decision.recovered
    assert policy.state == SafetyState.NORMAL


def test_new_stale_interval_stops_immediately_after_recovery():
    policy = make_policy()
    policy.evaluate_watchdog(int(0.6 * SECOND))
    policy.accept_command(0.1, 0.0, int(0.61 * SECOND))

    stale = policy.evaluate_watchdog(int(1.11 * SECOND) + 1)
    assert stale.timed_out
    assert stale.publish_stop


def test_return_to_rover_requires_fresh_command_for_recovery():
    policy = make_policy()
    policy.change_mode(DriveMode.HOLD, 10)
    policy.change_mode(DriveMode.ROVER, 20)
    assert policy.state == SafetyState.STALE
    assert policy.evaluate_watchdog(30).publish_stop is False

    decision = policy.accept_command(0.1, 0.0, 31)
    assert decision.recovered
    assert policy.state == SafetyState.NORMAL


def test_unknown_mode_is_rejected_without_state_change():
    policy = make_policy()
    decision = policy.change_mode(255, 100)
    assert not decision.accepted
    assert policy.mode == DriveMode.ROVER
    assert policy.state == SafetyState.NORMAL


@pytest.mark.parametrize('value', [0.0, -0.01, math.nan, math.inf])
@pytest.mark.parametrize(
    'name',
    [
        'command_timeout_sec',
        'watchdog_period_sec',
        'stop_publish_period_sec',
    ],
)
def test_timing_parameter_validation(name, value):
    with pytest.raises(ValueError, match='must be greater than zero'):
        _positive_seconds(name, value)


def test_sub_nanosecond_timing_parameter_is_rejected():
    with pytest.raises(ValueError, match='at least one nanosecond'):
        _positive_seconds('watchdog_period_sec', 1.0e-12)


@pytest.mark.parametrize('value', [0.0, -0.01, math.nan, math.inf])
@pytest.mark.parametrize('name', ['max_linear_mps', 'max_angular_radps'])
def test_command_limit_parameter_validation(name, value):
    with pytest.raises(ValueError, match='finite and greater than zero'):
        _positive_limit(name, value)


def test_simulated_time_reset_keeps_watchdog_operational():
    policy = make_policy(start_time_ns=10 * SECOND)
    policy.evaluate_watchdog(2 * SECOND)
    assert policy.last_command_ns == 2 * SECOND

    stale = policy.evaluate_watchdog(2 * SECOND + SECOND)
    assert stale.timed_out
    assert stale.publish_stop

    reset = policy.evaluate_watchdog(SECOND)
    assert reset.publish_stop
