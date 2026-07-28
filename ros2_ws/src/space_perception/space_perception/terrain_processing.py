"""Pure NumPy terrain filtering and elevation-grid algorithms."""

from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np


@dataclass(frozen=True)
class ElevationCell:
    """One measured elevation cell."""

    x: float
    y: float
    elevation: float
    variance: float
    point_count: int
    stamp_ns: int


def transform_points(points: np.ndarray, transform: np.ndarray) -> np.ndarray:
    """Apply a 4x4 rigid transform to an Nx3 point array."""
    points = np.asarray(points, dtype=np.float64)
    if points.size == 0:
        return np.empty((0, 3), dtype=np.float64)
    return points @ transform[:3, :3].T + transform[:3, 3]


def finite_and_range_mask(
    points: np.ndarray, min_range: float, max_range: float
) -> np.ndarray:
    """Return a mask for finite points within inclusive sensor range."""
    finite = np.isfinite(points).all(axis=1)
    squared_range = np.einsum('ij,ij->i', points, points)
    return (
        finite
        & (squared_range >= min_range * min_range)
        & (squared_range <= max_range * max_range)
    )


def crop_mask(
    points_base: np.ndarray,
    crop_min: np.ndarray,
    crop_max: np.ndarray,
) -> np.ndarray:
    """Return a mask for points inside a base-relative axis-aligned crop."""
    return (
        (points_base >= np.asarray(crop_min))
        & (points_base <= np.asarray(crop_max))
    ).all(axis=1)


def rover_exclusion_mask(
    points_base: np.ndarray,
    exclusion_min: np.ndarray,
    exclusion_max: np.ndarray,
) -> np.ndarray:
    """Return a mask excluding points inside the rover-body box."""
    inside = (
        (points_base >= np.asarray(exclusion_min))
        & (points_base <= np.asarray(exclusion_max))
    ).all(axis=1)
    return ~inside


def voxel_downsample(points: np.ndarray, voxel_size: float) -> np.ndarray:
    """Return deterministic per-voxel centroids ordered by voxel index."""
    points = np.asarray(points, dtype=np.float64)
    if points.size == 0:
        return np.empty((0, 3), dtype=np.float64)
    indices = np.floor(points / voxel_size).astype(np.int64)
    order = np.lexsort((indices[:, 2], indices[:, 1], indices[:, 0]))
    sorted_indices = indices[order]
    sorted_points = points[order]
    starts = np.r_[
        True, np.any(sorted_indices[1:] != sorted_indices[:-1], axis=1)
    ]
    group_starts = np.flatnonzero(starts)
    counts = np.diff(np.r_[group_starts, len(points)])
    sums = np.add.reduceat(sorted_points, group_starts, axis=0)
    return sums / counts[:, None]


def filter_terrain_points(
    points_sensor: np.ndarray,
    target_from_sensor: np.ndarray,
    base_from_target: np.ndarray,
    *,
    min_range: float,
    max_range: float,
    crop_min: np.ndarray,
    crop_max: np.ndarray,
    remove_rover_body: bool,
    exclusion_min: np.ndarray,
    exclusion_max: np.ndarray,
    voxel_size: float,
) -> Tuple[np.ndarray, int]:
    """Filter sensor points and return target-frame points and valid count."""
    points_sensor = np.asarray(points_sensor, dtype=np.float64).reshape((-1, 3))
    valid_mask = finite_and_range_mask(
        points_sensor, min_range=min_range, max_range=max_range
    )
    valid = points_sensor[valid_mask]
    if valid.size == 0:
        return np.empty((0, 3), dtype=np.float64), 0
    target = transform_points(valid, target_from_sensor)
    base = transform_points(target, base_from_target)
    keep = crop_mask(base, crop_min, crop_max)
    if remove_rover_body:
        keep &= rover_exclusion_mask(base, exclusion_min, exclusion_max)
    return voxel_downsample(target[keep], voxel_size), len(valid)


def xy_cell_indices(points: np.ndarray, resolution: float) -> np.ndarray:
    """Return odom-aligned integer XY cell indices."""
    points = np.asarray(points)
    if points.size == 0:
        return np.empty((0, 2), dtype=np.int64)
    return np.floor(points[:, :2] / resolution).astype(np.int64)


def aggregate_elevation_cells(
    points: np.ndarray,
    resolution: float,
    min_points: int,
    statistic: str,
    stamp_ns: int,
) -> Dict[Tuple[int, int], ElevationCell]:
    """Aggregate measured points into deterministic odom-aligned cells."""
    points = np.asarray(points, dtype=np.float64).reshape((-1, 3))
    finite = points[np.isfinite(points).all(axis=1)]
    if finite.size == 0:
        return {}
    indices = xy_cell_indices(finite, resolution)
    order = np.lexsort((indices[:, 1], indices[:, 0]))
    indices = indices[order]
    finite = finite[order]
    starts = np.r_[
        True, np.any(indices[1:] != indices[:-1], axis=1)
    ]
    group_starts = np.flatnonzero(starts)
    counts = np.diff(np.r_[group_starts, len(finite)])
    cells: Dict[Tuple[int, int], ElevationCell] = {}
    for start, count in zip(group_starts, counts):
        if count < min_points:
            continue
        cell_index = tuple(int(value) for value in indices[start])
        heights = finite[start:start + count, 2]
        if statistic == 'median':
            elevation = float(np.median(heights))
        elif statistic == 'mean':
            elevation = float(np.mean(heights))
        else:
            raise ValueError(f'unsupported elevation statistic: {statistic}')
        cells[cell_index] = ElevationCell(
            x=(cell_index[0] + 0.5) * resolution,
            y=(cell_index[1] + 0.5) * resolution,
            elevation=elevation,
            variance=float(np.var(heights)),
            point_count=int(count),
            stamp_ns=stamp_ns,
        )
    return cells


def retain_local_fresh_cells(
    cells: Dict[Tuple[int, int], ElevationCell],
    *,
    center_x: float,
    center_y: float,
    length_x: float,
    length_y: float,
    now_ns: int,
    timeout_ns: int,
) -> Dict[Tuple[int, int], ElevationCell]:
    """Return fresh cells inside the current rover-centred grid extent."""
    half_x = length_x * 0.5
    half_y = length_y * 0.5
    return {
        key: cell
        for key, cell in sorted(cells.items())
        if now_ns - cell.stamp_ns <= timeout_ns
        and abs(cell.x - center_x) <= half_x
        and abs(cell.y - center_y) <= half_y
    }


def cells_to_array(
    cells: Dict[Tuple[int, int], ElevationCell]
) -> np.ndarray:
    """Convert cells to deterministic x,y,z,variance,count rows."""
    if not cells:
        return np.empty((0, 5), dtype=np.float64)
    return np.asarray(
        [
            (
                cell.x,
                cell.y,
                cell.elevation,
                cell.variance,
                cell.point_count,
            )
            for _, cell in sorted(cells.items())
        ],
        dtype=np.float64,
    )
