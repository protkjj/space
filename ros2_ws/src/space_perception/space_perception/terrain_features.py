"""Pure NumPy terrain-feature extraction from measured elevation cells."""

from dataclasses import dataclass

import numpy as np


FEATURE_COLUMN_COUNT = 11


@dataclass(frozen=True)
class FeatureConfig:
    """Configuration for local elevation-neighbourhood feature extraction."""

    grid_resolution: float = 0.05
    feature_radius: float = 0.15
    minimum_neighbors: int = 5
    minimum_adjacent_neighbors: int = 2
    maximum_neighbors: int = 32
    plane_fit_method: str = 'svd'
    maximum_condition_number: float = 100.0
    maximum_fit_residual: float = 0.05
    roughness_method: str = 'median_absolute_residual'
    step_neighborhood_cells: int = 1
    confidence_min_point_count: int = 2
    confidence_target_point_count: int = 8
    confidence_variance_scale: float = 0.02
    confidence_residual_scale: float = 0.02


@dataclass(frozen=True)
class FeatureStats:
    """Counts and medians produced during one feature computation."""

    input_cells: int
    valid_cells: int
    rejected_nonfinite: int
    rejected_duplicates: int
    rejected_neighbors: int
    rejected_plane_fit: int
    median_neighbor_count: float
    median_coverage: float
    median_plane_residual: float


def _validate_config(config):
    if config.grid_resolution <= 0.0 or config.feature_radius <= 0.0:
        raise ValueError('grid_resolution and feature_radius must be positive')
    if config.minimum_neighbors < 0:
        raise ValueError('minimum_neighbors cannot be negative')
    if config.minimum_adjacent_neighbors < 0:
        raise ValueError('minimum_adjacent_neighbors cannot be negative')
    if config.maximum_neighbors < max(config.minimum_neighbors, 1):
        raise ValueError('maximum_neighbors is too small')
    if config.step_neighborhood_cells < 1:
        raise ValueError('step_neighborhood_cells must be at least one')
    if config.plane_fit_method != 'svd':
        raise ValueError('plane_fit_method must be "svd"')
    if config.roughness_method != 'median_absolute_residual':
        raise ValueError(
            'roughness_method must be "median_absolute_residual"'
        )
    if config.maximum_condition_number <= 0.0:
        raise ValueError('maximum_condition_number must be positive')
    if config.maximum_fit_residual < 0.0:
        raise ValueError('maximum_fit_residual cannot be negative')
    if config.confidence_target_point_count <= (
        config.confidence_min_point_count
    ):
        raise ValueError('confidence target must exceed minimum point count')
    if config.confidence_variance_scale <= 0.0:
        raise ValueError('confidence_variance_scale must be positive')
    if config.confidence_residual_scale <= 0.0:
        raise ValueError('confidence_residual_scale must be positive')


def _grid_index(coordinate, resolution):
    """Recover the index of a cell centre despite float32 representation."""
    return int(np.rint(float(coordinate) / resolution - 0.5))


def _quality_key(row):
    """Prefer greater support, then lower variance for duplicate indices."""
    return (-int(row[4]), float(row[3]), float(row[2]))


def _prepare_cells(rows, resolution):
    rows = np.asarray(rows, dtype=np.float64)
    if rows.size == 0:
        return {}, 0, 0
    if rows.ndim != 2 or rows.shape[1] != 5:
        raise ValueError('elevation rows must have shape (N, 5)')
    cells = {}
    rejected_nonfinite = 0
    duplicates = 0
    for row in rows:
        if not np.all(np.isfinite(row)) or row[4] < 0.0 or row[3] < 0.0:
            rejected_nonfinite += 1
            continue
        index = (
            _grid_index(row[0], resolution),
            _grid_index(row[1], resolution),
        )
        existing = cells.get(index)
        if existing is not None:
            duplicates += 1
            if _quality_key(row) >= _quality_key(existing):
                continue
        cells[index] = row.copy()
    return cells, rejected_nonfinite, duplicates


def _expected_offsets(config):
    radius_cells = int(np.ceil(
        config.feature_radius / config.grid_resolution
    ))
    radius_squared = config.feature_radius ** 2 + 1e-12
    offsets = []
    for dx in range(-radius_cells, radius_cells + 1):
        for dy in range(-radius_cells, radius_cells + 1):
            if dx == 0 and dy == 0:
                continue
            distance_squared = (
                (dx * config.grid_resolution) ** 2
                + (dy * config.grid_resolution) ** 2
            )
            if distance_squared <= radius_squared:
                offsets.append((dx, dy, distance_squared))
    return sorted(offsets, key=lambda item: (item[2], item[0], item[1]))


def _fit_plane(center, neighbors, config):
    samples = np.vstack((center, neighbors))
    dx = samples[:, 0] - center[0]
    dy = samples[:, 1] - center[1]
    design = np.column_stack((dx, dy, np.ones(len(samples))))
    singular_values = np.linalg.svd(design, compute_uv=False)
    if singular_values[-1] <= np.finfo(float).eps:
        return None
    condition = singular_values[0] / singular_values[-1]
    if not np.isfinite(condition) or condition > config.maximum_condition_number:
        return None
    coefficients, _, rank, _ = np.linalg.lstsq(
        design, samples[:, 2], rcond=None
    )
    if rank < 3 or not np.all(np.isfinite(coefficients)):
        return None
    residuals = samples[:, 2] - design @ coefficients
    fit_residual = float(np.sqrt(np.mean(np.square(residuals))))
    if (
        not np.isfinite(fit_residual)
        or fit_residual > config.maximum_fit_residual
    ):
        return None
    roughness = float(np.median(np.abs(residuals)))
    return coefficients, fit_residual, roughness


def _confidence(coverage, center, fit_residual, config):
    point_support = np.clip(
        (center[4] - config.confidence_min_point_count)
        / (
            config.confidence_target_point_count
            - config.confidence_min_point_count
        ),
        0.0,
        1.0,
    )
    variance_quality = np.exp(
        -center[3] / (config.confidence_variance_scale ** 2)
    )
    residual_quality = np.exp(
        -fit_residual / config.confidence_residual_scale
    )
    return float(np.clip(
        coverage * point_support * variance_quality * residual_quality,
        0.0,
        1.0,
    ))


def compute_terrain_features(rows, config=FeatureConfig()):
    """
    Compute valid features and statistics from elevation Nx5 rows.

    Output columns are x, y, z, slope, roughness, step_height,
    elevation_variance, point_count, neighbor_count,
    neighborhood_coverage, and confidence.
    """
    _validate_config(config)
    cells, rejected_nonfinite, duplicates = _prepare_cells(
        rows, config.grid_resolution
    )
    input_count = 0 if np.asarray(rows).size == 0 else len(np.asarray(rows))
    if not cells:
        return np.empty((0, FEATURE_COLUMN_COUNT)), FeatureStats(
            input_count, 0, rejected_nonfinite, duplicates, 0, 0,
            0.0, 0.0, 0.0
        )

    offsets = _expected_offsets(config)
    expected_count = len(offsets)
    features = []
    neighbor_counts = []
    coverages = []
    residual_values = []
    rejected_neighbors = 0
    rejected_fit = 0
    for index in sorted(cells):
        center = cells[index]
        available = [
            (offset, cells[(index[0] + offset[0], index[1] + offset[1])])
            for offset in offsets
            if (index[0] + offset[0], index[1] + offset[1]) in cells
        ]
        neighbor_count = len(available)
        if neighbor_count < config.minimum_neighbors:
            rejected_neighbors += 1
            continue
        selected = available[:config.maximum_neighbors]
        neighbors = np.asarray([item[1] for item in selected])
        fit = _fit_plane(center, neighbors, config)
        if fit is None:
            rejected_fit += 1
            continue
        coefficients, fit_residual, roughness = fit
        adjacent = [
            (offset, row) for offset, row in available
            if max(abs(offset[0]), abs(offset[1]))
            <= config.step_neighborhood_cells
        ]
        if len(adjacent) < config.minimum_adjacent_neighbors:
            rejected_neighbors += 1
            continue
        a, b = coefficients[:2]
        step_residuals = [
            abs(
                (row[2] - center[2])
                - a * (row[0] - center[0])
                - b * (row[1] - center[1])
            )
            for _, row in adjacent
        ]
        step_height = float(max(step_residuals, default=0.0))
        slope = float(np.arctan(np.hypot(a, b)))
        coverage = (
            neighbor_count / expected_count if expected_count else 1.0
        )
        coverage = float(np.clip(coverage, 0.0, 1.0))
        confidence = _confidence(
            coverage, center, fit_residual, config
        )
        features.append([
            center[0], center[1], center[2], slope, roughness, step_height,
            center[3], center[4], neighbor_count, coverage, confidence,
        ])
        neighbor_counts.append(neighbor_count)
        coverages.append(coverage)
        residual_values.append(fit_residual)

    output = np.asarray(features, dtype=np.float64).reshape(
        (-1, FEATURE_COLUMN_COUNT)
    )
    stats = FeatureStats(
        input_cells=input_count,
        valid_cells=len(output),
        rejected_nonfinite=rejected_nonfinite,
        rejected_duplicates=duplicates,
        rejected_neighbors=rejected_neighbors,
        rejected_plane_fit=rejected_fit,
        median_neighbor_count=float(np.median(neighbor_counts))
        if neighbor_counts else 0.0,
        median_coverage=float(np.median(coverages)) if coverages else 0.0,
        median_plane_residual=float(np.median(residual_values))
        if residual_values else 0.0,
    )
    return output, stats
