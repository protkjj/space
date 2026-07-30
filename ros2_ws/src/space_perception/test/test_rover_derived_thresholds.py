"""
Guard the thresholds this package derives from the rover, not from tuning.

``traversability.py`` is deliberately ROS-free and import-free, so it cannot
read ``space_description/config/rover_geometry.yaml`` itself. That leaves its
dataclass default free to drift from the source, which is exactly what happened:
``step_max`` read 0.056 -- half the old 0.112 m wheel -- and stayed 0.056 for the
whole life of the 0.070 m CAD wheel, scoring steps against a rover 1.6x more
capable than ours. Nothing caught it, because the arithmetic still succeeded and
the scores still looked reasonable.

These tests are the thing that would have caught it.
"""

import pytest
from space_description.rover_geometry import load_geometry, max_step_height
from space_perception.traversability import (
    smooth_penalty,
    TraversabilityConfig,
)


def test_step_max_matches_rover_geometry():
    """
    The dataclass default must equal the value derived from the CAD source.

    If this fails, a rover dimension moved and this copy did not follow. Fix the
    default, do not relax the test -- the whole point is that the copy cannot
    quietly describe a different rover.
    """
    expected = max_step_height(load_geometry())
    assert TraversabilityConfig().step_max == pytest.approx(expected)


def test_step_max_is_absent_from_the_shipped_params_file():
    """
    ``terrain_perception.yaml`` must not set ``step_max``.

    The node derives it; a value in the params file would override that
    derivation and reintroduce the copy that went stale. Absence is the
    guarantee, so it is worth asserting rather than trusting a comment.
    """
    import os

    import yaml
    from ament_index_python.packages import get_package_share_directory

    path = os.path.join(
        get_package_share_directory('space_perception'),
        'config', 'terrain_perception.yaml',
    )
    with open(path, 'r', encoding='utf-8') as handle:
        params = yaml.safe_load(handle)

    node = params['terrain_traversability_node']['ros__parameters']
    assert 'step_free' in node, 'sanity: the step block should still exist'
    assert 'step_max' not in node, (
        'step_max is derived from space_description/config/rover_geometry.yaml; '
        'setting it here overrides the derivation and lets it go stale again'
    )


def test_a_step_at_the_wheel_limit_saturates_the_penalty():
    """
    A step exactly at the wheel's limit must score as fully impassable.

    This is the behaviour the stale value destroyed: under ``step_max`` 0.056 a
    0.035 m step -- the tallest the 0.070 m wheel clears -- scored 0.63 instead
    of 1.0, so the planner treated a wall the rover cannot climb as merely
    rough.
    """
    config = TraversabilityConfig()
    limit = max_step_height(load_geometry())

    at_limit = smooth_penalty(limit, config.step_free, config.step_max)
    assert at_limit == pytest.approx(1.0)

    below = smooth_penalty(limit * 0.5, config.step_free, config.step_max)
    assert 0.0 < below < 1.0, 'penalty must still discriminate below the limit'
