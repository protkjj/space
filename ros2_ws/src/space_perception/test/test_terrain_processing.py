"""Unit tests for deterministic terrain processing."""

import numpy as np

from space_perception.terrain_processing import (
    aggregate_elevation_cells,
    cells_to_array,
    crop_mask,
    ElevationCell,
    filter_terrain_points,
    finite_and_range_mask,
    retain_local_fresh_cells,
    rover_exclusion_mask,
    voxel_downsample,
    xy_cell_indices,
)


IDENTITY = np.eye(4)


def test_nan_and_infinite_removal():
    points = np.array([[1, 0, 0], [np.nan, 0, 0], [1, np.inf, 0]])
    assert finite_and_range_mask(points, 0.1, 2.0).tolist() == [
        True, False, False
    ]


def test_range_filtering_is_inclusive():
    points = np.array([[0.1, 0, 0], [1, 0, 0], [2, 0, 0], [3, 0, 0]])
    assert finite_and_range_mask(points, 1.0, 2.0).tolist() == [
        False, True, True, False
    ]


def test_crop_filtering():
    points = np.array([[0, 0, 0], [2, 0, 0], [0, -2, 0]])
    mask = crop_mask(points, [-1, -1, -1], [1, 1, 1])
    assert mask.tolist() == [True, False, False]


def test_rover_body_exclusion():
    points = np.array([[0, 0, 0], [0.4, 0, 0]])
    mask = rover_exclusion_mask(points, [-0.2] * 3, [0.2] * 3)
    assert mask.tolist() == [False, True]


def test_voxel_downsampling_centroids_and_order():
    points = np.array([[1.2, 0, 0], [0.2, 0, 0], [0.4, 0, 0]])
    result = voxel_downsample(points, 1.0)
    np.testing.assert_allclose(result, [[0.3, 0, 0], [1.2, 0, 0]])


def test_complete_filter_handles_empty_input():
    filtered, valid = filter_terrain_points(
        np.empty((0, 3)),
        IDENTITY,
        IDENTITY,
        min_range=0.1,
        max_range=4.0,
        crop_min=np.array([-1, -1, -1]),
        crop_max=np.array([1, 1, 1]),
        remove_rover_body=False,
        exclusion_min=np.zeros(3),
        exclusion_max=np.zeros(3),
        voxel_size=0.1,
    )
    assert valid == 0
    assert filtered.shape == (0, 3)


def test_xy_cell_indexing():
    points = np.array([[0.01, 0.09, 0], [-0.01, -0.11, 0]])
    assert xy_cell_indices(points, 0.1).tolist() == [[0, 0], [-1, -2]]


def test_median_elevation_variance_and_count():
    points = np.array([
        [0.01, 0.01, 0.0],
        [0.02, 0.02, 0.1],
        [0.03, 0.03, 1.0],
    ])
    cells = aggregate_elevation_cells(points, 0.1, 2, 'median', 10)
    cell = cells[(0, 0)]
    assert cell.elevation == 0.1
    assert np.isclose(cell.variance, np.var([0.0, 0.1, 1.0]))
    assert cell.point_count == 3


def test_minimum_points_rejection():
    points = np.array([[0.01, 0.01, 0.2]])
    assert aggregate_elevation_cells(points, 0.1, 2, 'median', 10) == {}


def test_stale_and_outside_cells_are_removed():
    cells = {
        (0, 0): ElevationCell(0.05, 0.05, 0.1, 0.0, 2, 90),
        (1, 0): ElevationCell(0.15, 0.05, 0.1, 0.0, 2, 0),
        (20, 0): ElevationCell(2.05, 0.05, 0.1, 0.0, 2, 90),
    }
    kept = retain_local_fresh_cells(
        cells,
        center_x=0.0,
        center_y=0.0,
        length_x=2.0,
        length_y=2.0,
        now_ns=100,
        timeout_ns=20,
    )
    assert list(kept) == [(0, 0)]


def test_empty_elevation_input():
    assert aggregate_elevation_cells(
        np.empty((0, 3)), 0.1, 2, 'median', 0
    ) == {}
    assert cells_to_array({}).shape == (0, 5)


def test_elevation_output_order_is_deterministic():
    cells = {
        (1, 0): ElevationCell(1, 0, 0.2, 0.01, 3, 0),
        (-1, 2): ElevationCell(-1, 2, 0.1, 0.02, 4, 0),
    }
    rows = cells_to_array(cells)
    assert rows[:, :3].tolist() == [[-1, 2, 0.1], [1, 0, 0.2]]
