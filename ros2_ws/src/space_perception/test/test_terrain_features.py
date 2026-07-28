"""Tests for deterministic, sensor-derived terrain features."""

from dataclasses import replace

import numpy as np

from space_perception.pointcloud_utils import (
    create_elevation_cloud,
    create_feature_cloud,
    elevation_cloud_numpy,
    FEATURE_DTYPE,
)
from space_perception.terrain_features import (
    compute_terrain_features,
    FeatureConfig,
)
from std_msgs.msg import Header


CONFIG = FeatureConfig(
    grid_resolution=0.1,
    feature_radius=0.15,
    minimum_neighbors=3,
    minimum_adjacent_neighbors=2,
    maximum_neighbors=8,
    maximum_fit_residual=0.2,
    confidence_min_point_count=1,
    confidence_target_point_count=5,
    confidence_variance_scale=0.1,
    confidence_residual_scale=0.1,
)


def grid_rows(function, missing=()):
    rows = []
    for ix in range(-2, 3):
        for iy in range(-2, 3):
            if (ix, iy) in missing:
                continue
            x, y = (ix + 0.5) * 0.1, (iy + 0.5) * 0.1
            rows.append([x, y, function(ix, iy, x, y), 0.0, 5])
    return np.asarray(rows)


def center_feature(features):
    return features[
        np.argmin(np.square(features[:, 0:2] - [0.05, 0.05]).sum(axis=1))
    ]


def test_flat_horizontal_plane():
    features, _ = compute_terrain_features(
        grid_rows(lambda *_: 0.2), CONFIG
    )
    center = center_feature(features)
    assert center[3] < 1e-10
    assert center[4] < 1e-10
    assert center[5] < 1e-10


def test_known_inclined_plane():
    features, _ = compute_terrain_features(
        grid_rows(lambda _i, _j, x, y: 0.2 * x - 0.1 * y), CONFIG
    )
    center = center_feature(features)
    assert np.isclose(center[3], np.arctan(np.hypot(0.2, 0.1)))
    assert center[4] < 1e-10
    assert center[5] < 1e-10


def test_noisy_plane_has_roughness_but_stable_slope():
    def surface(ix, iy, x, y):
        return 0.2 * x - 0.1 * y + 0.01 * ((ix + 2 * iy) % 3 - 1)

    features, _ = compute_terrain_features(grid_rows(surface), CONFIG)
    center = center_feature(features)
    assert abs(center[3] - np.arctan(np.hypot(0.2, 0.1))) < 0.08
    assert center[4] > 0.0


def test_abrupt_step_exceeds_smooth_ramp_step_feature():
    abrupt, _ = compute_terrain_features(
        grid_rows(lambda ix, _iy, _x, _y: 0.12 if ix >= 0 else 0.0),
        CONFIG,
    )
    ramp, _ = compute_terrain_features(
        grid_rows(lambda _ix, _iy, x, _y: 0.4 * x), CONFIG
    )
    assert np.max(abrupt[:, 5]) > 0.04
    assert np.max(ramp[:, 3]) > 0.1
    assert np.max(ramp[:, 5]) < np.max(abrupt[:, 5])


def test_missing_cells_reduce_coverage_without_fabrication():
    complete, _ = compute_terrain_features(
        grid_rows(lambda *_: 0.0), CONFIG
    )
    missing, _ = compute_terrain_features(
        grid_rows(lambda *_: 0.0, missing={(1, 0), (0, 1)}), CONFIG
    )
    assert center_feature(missing)[9] < center_feature(complete)[9]
    assert center_feature(missing)[8] == center_feature(complete)[8] - 2


def test_insufficient_neighbors_rejects_feature():
    rows = grid_rows(lambda *_: 0.0)[:2]
    features, stats = compute_terrain_features(rows, CONFIG)
    assert len(features) == 0
    assert stats.rejected_neighbors == 2


def test_duplicate_index_prefers_more_supported_measurement():
    rows = grid_rows(lambda *_: 0.0)
    duplicate = rows[12].copy()
    duplicate[2] = 0.3
    duplicate[4] = 1
    features, stats = compute_terrain_features(
        np.vstack((rows, duplicate)), CONFIG
    )
    assert stats.rejected_duplicates == 1
    assert np.isclose(center_feature(features)[2], rows[12, 2])


def test_collinear_neighborhood_is_rejected_as_poor_fit():
    rows = np.asarray([
        [(ix + 0.5) * 0.1, 0.05, 0.0, 0.0, 5]
        for ix in range(-3, 4)
    ])
    features, stats = compute_terrain_features(
        rows, replace(CONFIG, feature_radius=0.31)
    )
    assert len(features) == 0
    assert stats.rejected_plane_fit > 0


def test_nan_and_infinite_rows_are_rejected():
    rows = grid_rows(lambda *_: 0.0)
    rows[0, 2] = np.nan
    rows[1, 3] = np.inf
    _, stats = compute_terrain_features(rows, CONFIG)
    assert stats.rejected_nonfinite == 2


def test_confidence_is_bounded_and_variance_reduces_it():
    low = grid_rows(lambda *_: 0.0)
    high = low.copy()
    high[:, 3] = 0.02
    low_features, _ = compute_terrain_features(low, CONFIG)
    high_features, _ = compute_terrain_features(high, CONFIG)
    assert np.all((low_features[:, 10] >= 0) & (low_features[:, 10] <= 1))
    assert center_feature(high_features)[10] < center_feature(low_features)[10]


def test_higher_coverage_increases_confidence():
    full, _ = compute_terrain_features(
        grid_rows(lambda *_: 0.0), CONFIG
    )
    sparse, _ = compute_terrain_features(
        grid_rows(lambda *_: 0.0, missing={(1, 0), (0, 1)}), CONFIG
    )
    assert center_feature(full)[10] > center_feature(sparse)[10]


def test_output_order_is_deterministic():
    rows = grid_rows(lambda *_: 0.0)
    first, _ = compute_terrain_features(rows, CONFIG)
    second, _ = compute_terrain_features(rows[::-1], CONFIG)
    np.testing.assert_allclose(first, second)


def test_empty_input():
    features, stats = compute_terrain_features(np.empty((0, 5)), CONFIG)
    assert features.shape == (0, 11)
    assert stats.input_cells == 0


def test_pointcloud_mixed_field_packing_and_unpacking():
    elevation_rows = np.asarray([[0.05, -0.05, 0.2, 0.003, 7]])
    cloud = create_elevation_cloud(Header(frame_id='odom'), elevation_rows)
    np.testing.assert_allclose(
        elevation_cloud_numpy(cloud), elevation_rows, rtol=1e-6
    )
    features, _ = compute_terrain_features(
        grid_rows(lambda *_: 0.0), CONFIG
    )
    feature_cloud = create_feature_cloud(Header(frame_id='odom'), features)
    assert feature_cloud.point_step == FEATURE_DTYPE.itemsize == 44
    assert [field.name for field in feature_cloud.fields] == list(
        FEATURE_DTYPE.names
    )
