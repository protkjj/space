"""Tests for continuous, deterministic prototype traversability scoring."""

from dataclasses import replace

import numpy as np
import pytest

from space_perception.latest_data import sample_disposition
from space_perception.pointcloud_utils import (
    create_feature_cloud,
    create_traversability_cloud,
    feature_cloud_numpy,
    TRAVERSABILITY_DTYPE,
)
from space_perception.traversability import (
    compose_geometry_penalty,
    compose_traversability,
    compute_traversability,
    LIMIT_INVALID,
    LIMIT_SLOPE,
    normalized_weights,
    smooth_penalty,
    TraversabilityConfig,
)
from space_perception.traversability_calibration import calibration_rows
from std_msgs.msg import Header


CONFIG = TraversabilityConfig(
    slope_free=0.1,
    slope_max=0.5,
    roughness_free=0.002,
    roughness_max=0.02,
    step_free=0.005,
    step_max=0.05,
    variance_free=0.00001,
    variance_max=0.001,
    coverage_min=0.5,
    confidence_min=0.1,
    minimum_neighbors=4,
)


def feature_row(
    x=0.05,
    y=0.05,
    slope=0.0,
    roughness=0.0,
    step=0.0,
    variance=0.0,
    neighbors=8,
    coverage=1.0,
    confidence=1.0,
):
    return [
        x, y, 0.1, slope, roughness, step, variance, 5,
        neighbors, coverage, confidence,
    ]


def score(row, config=CONFIG):
    return compute_traversability(np.asarray([row]), config)[0][0]


def test_normalization_below_lower_reference():
    assert smooth_penalty([-1.0, 0.1], 0.1, 0.5).tolist() == [0.0, 0.0]


def test_normalization_between_references_is_smooth_and_bounded():
    value = smooth_penalty([0.3], 0.1, 0.5)[0]
    assert np.isclose(value, 0.5)


def test_normalization_above_upper_reference():
    assert smooth_penalty([0.5, 1.0], 0.1, 0.5).tolist() == [1.0, 1.0]


def test_invalid_parameter_ordering():
    with pytest.raises(ValueError):
        smooth_penalty([0.2], 0.5, 0.1)
    with pytest.raises(ValueError):
        compute_traversability(
            np.asarray([feature_row()]),
            replace(CONFIG, step_max=CONFIG.step_free),
        )


def test_flat_smooth_terrain_has_high_traversability():
    assert score(feature_row())[3] > 0.99


@pytest.mark.parametrize(
    ('field', 'low', 'high'),
    [('slope', 0.0, 0.4), ('roughness', 0.0, 0.015), ('step', 0.0, 0.04)],
)
def test_increased_geometry_reduces_score(field, low, high):
    arguments = {field: low}
    low_score = score(feature_row(**arguments))[3]
    arguments[field] = high
    high_score = score(feature_row(**arguments))[3]
    assert high_score < low_score


@pytest.mark.parametrize(
    ('field', 'good', 'poor'),
    [
        ('coverage', 1.0, 0.55),
        ('confidence', 1.0, 0.11),
        ('variance', 0.0, 0.0008),
    ],
)
def test_measurement_quality_increases_uncertainty(field, good, poor):
    arguments = {field: good}
    good_penalty = score(feature_row(**arguments))[7]
    arguments[field] = poor
    poor_penalty = score(feature_row(**arguments))[7]
    assert poor_penalty > good_penalty


def test_weighted_sum_composition_and_weight_normalization():
    config = replace(
        CONFIG,
        composition_mode='weighted_sum',
        weight_slope=1,
        weight_roughness=1,
        weight_step=1,
        weight_uncertainty=1,
    )
    penalties = np.asarray([[0.2, 0.4, 0.6, 0.8]])
    assert np.isclose(compose_traversability(penalties, config)[0], 0.5)
    np.testing.assert_allclose(normalized_weights(config), [0.25] * 4)


def test_conservative_max_composition():
    penalties = np.asarray([[0.2, 0.4, 0.6, 0.8]])
    config = replace(CONFIG, composition_mode='conservative_max')
    assert np.isclose(compose_traversability(penalties, config)[0], 0.2)


def test_output_is_bounded():
    rows = np.asarray([
        feature_row(slope=value, roughness=value, step=value)
        for value in np.linspace(0.0, 1.0, 20)
    ])
    output, _ = compute_traversability(rows, CONFIG)
    assert np.all((output[:, 3:8] >= 0.0) & (output[:, 3:8] <= 1.0))


def test_dominant_limiting_factor():
    output = score(feature_row(slope=0.4))
    assert output[10] == LIMIT_SLOPE


def test_deterministic_tie_uses_lower_code():
    config = replace(CONFIG, composition_mode='conservative_max')
    output = score(feature_row(slope=0.3, roughness=0.011), config)
    assert np.isclose(output[4], output[5])
    assert output[10] == LIMIT_SLOPE


def test_low_support_cell_is_invalid_and_never_favourable():
    output = score(feature_row(neighbors=1))
    assert output[9] == 0
    assert output[10] == LIMIT_INVALID
    assert np.isnan(output[3])


def test_nan_and_infinite_input_are_invalid():
    rows = np.asarray([
        feature_row(slope=np.nan),
        feature_row(x=0.15, roughness=np.inf),
    ])
    output, stats = compute_traversability(rows, CONFIG)
    assert np.all(output[:, 9] == 0)
    assert np.all(output[:, 10] == LIMIT_INVALID)
    assert stats.invalid_cells == 2


def test_empty_input():
    output, stats = compute_traversability(np.empty((0, 11)), CONFIG)
    assert output.shape == (0, 11)
    assert stats.input_cells == 0


def test_output_order_is_deterministic():
    rows = np.asarray([
        feature_row(x=0.15, y=0.05),
        feature_row(x=-0.05, y=0.15),
        feature_row(x=-0.05, y=0.05),
    ])
    first, _ = compute_traversability(rows, CONFIG)
    second, _ = compute_traversability(rows[::-1], CONFIG)
    np.testing.assert_allclose(first, second)


def test_invalid_weights():
    with pytest.raises(ValueError):
        normalized_weights(replace(CONFIG, weight_slope=-1.0))
    with pytest.raises(ValueError):
        normalized_weights(replace(
            CONFIG,
            weight_slope=0.0,
            weight_roughness=0.0,
            weight_step=0.0,
            weight_uncertainty=0.0,
        ))


def test_pointcloud_packing_and_feature_validation():
    rows = np.asarray([feature_row()])
    feature_cloud = create_feature_cloud(Header(frame_id='odom'), rows)
    np.testing.assert_allclose(feature_cloud_numpy(feature_cloud), rows)
    output, _ = compute_traversability(rows, CONFIG)
    cloud = create_traversability_cloud(Header(frame_id='odom'), output)
    assert cloud.point_step == TRAVERSABILITY_DTYPE.itemsize == 38
    assert [field.name for field in cloud.fields] == list(
        TRAVERSABILITY_DTYPE.names
    )


@pytest.mark.parametrize(
    ('column', 'values'),
    [
        (3, np.linspace(0.0, 0.7, 50)),
        (4, np.linspace(0.0, 0.04, 50)),
        (5, np.linspace(0.0, 0.1, 50)),
        (6, np.linspace(0.0, 0.001, 50)),
    ],
)
def test_increasing_input_never_increases_score(column, values):
    rows = np.tile(feature_row(), (len(values), 1))
    rows[:, column] = values
    output, _ = compute_traversability(rows, CONFIG)
    assert np.all(np.diff(output[:, 3]) <= 1e-12)


@pytest.mark.parametrize('column', [9, 10])
def test_decreasing_quality_never_increases_score(column):
    rows = np.tile(feature_row(), (50, 1))
    rows[:, column] = np.linspace(1.0, 0.51 if column == 9 else 0.11, 50)
    output, _ = compute_traversability(rows, CONFIG)
    assert np.all(np.diff(output[:, 3]) <= 1e-12)


def test_smoothstep_reference_values_and_continuity():
    epsilon = 1e-8
    assert smooth_penalty([0.1, 0.5], 0.1, 0.5).tolist() == [0.0, 1.0]
    near = smooth_penalty(
        [0.1 - epsilon, 0.1 + epsilon, 0.5 - epsilon, 0.5 + epsilon],
        0.1,
        0.5,
    )
    assert abs(near[1] - near[0]) < 1e-10
    assert abs(near[3] - near[2]) < 1e-10


def test_geometry_composition_excludes_quality():
    penalties = np.asarray([[0.2, 0.4, 0.6]])
    geometry = compose_geometry_penalty(penalties, CONFIG)
    changed_quality = replace(CONFIG, weight_uncertainty=100.0)
    np.testing.assert_allclose(
        geometry, compose_geometry_penalty(penalties, changed_quality)
    )


def test_low_confidence_semantics():
    valid = score(feature_row(confidence=0.11))
    invalid = score(feature_row(confidence=0.09))
    assert valid[9] == 1
    assert valid[10] != LIMIT_INVALID
    assert invalid[9] == 0
    assert invalid[10] == LIMIT_INVALID


def test_latest_sample_disposition():
    assert sample_disposition(10, 10, 20, 1.0, True) == 'duplicate'
    assert sample_disposition(0, None, 2_000_000_000, 1.0, True) == 'stale'
    assert sample_disposition(0, None, 2_000_000_000, 1.0, False) == 'process'
    assert sample_disposition(2_000_000_000, None, 2_100_000_000, 1.0, True) == (
        'process'
    )


def test_calibration_output_is_deterministic_and_complete():
    first = calibration_rows(CONFIG)
    second = calibration_rows(CONFIG)
    for first_row, second_row in zip(first, second):
        for key in first_row:
            if isinstance(first_row[key], float) and np.isnan(first_row[key]):
                assert np.isnan(second_row[key])
            else:
                assert first_row[key] == second_row[key]
    assert len(first) == 44
    assert {row['sweep'] for row in first} == {
        'slope_rad', 'roughness_m', 'step_height_m',
        'coverage', 'confidence', 'variance_m2',
    }
