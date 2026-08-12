"""Unit tests for the deterministic ArduPilot adapter policy."""

import math

import pytest
from space_ardupilot_interface.ardupilot_adapter import (
    _non_empty,
    _positive_seconds,
    AdapterPolicy,
    CommandState,
    LinkState,
    RoverMode,
)


SECOND = 1_000_000_000


def make_policy(start_time_ns=0, command_timeout_sec=0.5,
                link_timeout_sec=3.0):
    """Return a policy with short, deterministic test periods."""
    return AdapterPolicy(
        command_timeout_sec=command_timeout_sec,
        link_timeout_sec=link_timeout_sec,
        start_time_ns=start_time_ns,
    )


def test_no_command_publishes_nothing():
    policy = make_policy()
    decision = policy.evaluate(SECOND)
    assert not decision.publish
    assert policy.command_state == CommandState.NEVER_COMMANDED


def test_fresh_command_is_forwarded_unchanged():
    policy = make_policy()
    policy.note_vehicle_state(0)
    assert policy.accept_command(0.25, -0.4, SECOND)

    decision = policy.evaluate(SECOND)
    assert decision.publish
    assert not decision.is_stop
    assert decision.linear_x == pytest.approx(0.25)
    assert decision.angular_z == pytest.approx(-0.4)


@pytest.mark.parametrize(
    'linear_x,angular_z',
    [
        (math.nan, 0.0),
        (0.0, math.nan),
        (math.inf, 0.0),
        (0.0, -math.inf),
    ],
)
def test_non_finite_commands_are_rejected(linear_x, angular_z):
    policy = make_policy()
    assert not policy.accept_command(linear_x, angular_z, SECOND)
    assert policy.command_state == CommandState.NEVER_COMMANDED


def test_stale_command_produces_stop():
    policy = make_policy(command_timeout_sec=0.5)
    policy.note_vehicle_state(0)
    policy.accept_command(0.3, 0.0, SECOND)

    fresh = policy.evaluate(SECOND)
    assert fresh.publish and not fresh.is_stop

    stale = policy.evaluate(SECOND + SECOND)
    assert stale.publish
    assert stale.is_stop
    assert stale.linear_x == 0.0
    assert stale.angular_z == 0.0
    assert policy.command_state == CommandState.STALE


def test_stale_command_stays_stopped_until_refreshed():
    policy = make_policy(command_timeout_sec=0.5)
    policy.note_vehicle_state(0)
    policy.accept_command(0.3, 0.0, 0)
    assert policy.evaluate(SECOND).is_stop

    policy.note_vehicle_state(SECOND)
    policy.accept_command(0.3, 0.0, SECOND)
    resumed = policy.evaluate(SECOND)
    assert resumed.publish
    assert not resumed.is_stop
    assert resumed.linear_x == pytest.approx(0.3)


def test_link_loss_produces_stop_even_with_fresh_commands():
    policy = make_policy(command_timeout_sec=10.0, link_timeout_sec=3.0)
    policy.note_vehicle_state(0)
    policy.accept_command(0.3, 0.0, 4 * SECOND)

    decision = policy.evaluate(4 * SECOND)
    assert decision.publish
    assert decision.is_stop
    assert policy.link_state == LinkState.LOST
    assert 'link' in decision.reason


def test_link_loss_is_measured_from_startup_when_never_seen():
    policy = make_policy(link_timeout_sec=3.0)
    policy.accept_command(0.3, 0.0, 4 * SECOND)

    decision = policy.evaluate(4 * SECOND)
    assert decision.is_stop
    assert policy.link_state == LinkState.LOST


def test_link_recovery_is_reported_once():
    policy = make_policy(link_timeout_sec=1.0)
    policy.accept_command(0.3, 0.0, 0)
    policy.evaluate(5 * SECOND)
    assert policy.link_state == LinkState.LOST

    assert policy.note_vehicle_state(5 * SECOND)
    assert policy.link_state == LinkState.ALIVE
    assert not policy.note_vehicle_state(5 * SECOND)


def test_backwards_clock_does_not_latch_stale():
    policy = make_policy(command_timeout_sec=0.5)
    policy.note_vehicle_state(10 * SECOND)
    policy.accept_command(0.3, 0.0, 10 * SECOND)

    # A world reset moves simulated time backwards.
    decision = policy.evaluate(SECOND)
    assert decision.publish
    assert not decision.is_stop


def test_vehicle_state_contents_are_not_retained():
    policy = make_policy()
    policy.note_vehicle_state(SECOND)
    # The policy exposes no pose attribute at all, which is what keeps the
    # autopilot estimate out of any Jetson-side estimator.
    assert not any(
        'pose' in name.lower() for name in vars(policy)
    )


@pytest.mark.parametrize('value', [0.0, -0.01, math.nan, math.inf])
def test_timeout_validation_rejects_bad_values(value):
    with pytest.raises(ValueError, match='must be finite and greater'):
        _positive_seconds('command_timeout_sec', value)


@pytest.mark.parametrize('value', ['', '   ', None, 5])
def test_non_empty_validation(value):
    with pytest.raises(ValueError, match='must be a non-empty string'):
        _non_empty('frame_id', value)


def test_rover_mode_numbers_match_pinned_firmware():
    # Values read from Rover/mode.h at the pinned revision recorded in
    # firmware/ardupilot/version.txt.
    assert int(RoverMode.MANUAL) == 0
    assert int(RoverMode.HOLD) == 4
    assert int(RoverMode.GUIDED) == 15
