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


def test_nothing_received_yet_is_not_reported_as_ready():
    policy = make_policy()
    # Before any vehicle state arrives, readiness is unknown, not true.
    blockers = policy.command_blockers()
    assert blockers, 'silence must not read as a ready vehicle'
    assert any('received yet' in reason for reason in blockers)


def test_build_without_arm_state_is_not_reported_as_ready():
    policy = make_policy()
    policy.note_vehicle_state(SECOND)
    # Heard from, but this build reports no arm state. Unknown is not ready.
    assert policy.armed is None
    assert policy.external_control is None
    blockers = policy.command_blockers()
    assert any('not reported' in reason for reason in blockers)


def test_disarmed_vehicle_is_reported_as_a_blocker():
    policy = make_policy()
    policy.note_vehicle_state(SECOND, armed=False, external_control=True)
    assert 'vehicle disarmed' in policy.command_blockers()


def test_external_control_disabled_is_reported():
    policy = make_policy()
    policy.note_vehicle_state(SECOND, armed=True, external_control=False)
    blockers = policy.command_blockers()
    assert any('external control' in reason for reason in blockers)


def test_wrong_mode_is_reported_against_the_expected_mode():
    policy = make_policy()
    policy.note_vehicle_state(
        SECOND, armed=True, mode=int(RoverMode.MANUAL), external_control=True
    )
    blockers = policy.command_blockers(int(RoverMode.GUIDED))
    assert any('expected 15' in reason for reason in blockers)

    policy.note_vehicle_state(SECOND, mode=int(RoverMode.GUIDED))
    assert policy.command_blockers(int(RoverMode.GUIDED)) == []


def test_ready_vehicle_reports_no_blockers():
    policy = make_policy()
    policy.note_vehicle_state(
        SECOND, armed=True, mode=int(RoverMode.GUIDED), external_control=True
    )
    assert policy.command_blockers(int(RoverMode.GUIDED)) == []


def test_lost_link_is_reported_as_a_blocker():
    policy = make_policy(link_timeout_sec=1.0)
    policy.note_vehicle_state(0, armed=True, external_control=True)
    policy.accept_command(0.3, 0.0, 5 * SECOND)
    policy.evaluate(5 * SECOND)
    assert 'autopilot link lost' in policy.command_blockers()


def test_zero_command_is_not_an_intent_to_move():
    policy = make_policy()
    # space_controller publishes zero commands continuously while the rover
    # is held, stopped, or in EMERGENCY. Those are fresh, but they are stops.
    assert policy.accept_command(0.0, 0.0, SECOND)
    assert policy.command_state == CommandState.FRESH
    assert not policy.command_is_motion


@pytest.mark.parametrize(
    'linear_x,angular_z',
    [(0.3, 0.0), (0.0, 0.4), (-0.2, 0.0), (0.0, -0.5)],
)
def test_non_zero_command_is_an_intent_to_move(linear_x, angular_z):
    policy = make_policy()
    assert policy.accept_command(linear_x, angular_z, SECOND)
    assert policy.command_is_motion


def test_motion_intent_clears_when_a_stop_follows():
    policy = make_policy()
    policy.accept_command(0.3, 0.0, SECOND)
    assert policy.command_is_motion
    policy.accept_command(0.0, 0.0, 2 * SECOND)
    assert not policy.command_is_motion


def test_status_fields_persist_across_partial_updates():
    policy = make_policy()
    policy.note_vehicle_state(
        SECOND, armed=True, mode=int(RoverMode.GUIDED), external_control=True
    )
    # A later heartbeat carrying no fields must not erase what was reported.
    policy.note_vehicle_state(2 * SECOND)
    assert policy.armed is True
    assert policy.mode == int(RoverMode.GUIDED)
    assert policy.external_control is True
