"""Pure NumPy terrain traversability scoring from measured features."""

from dataclasses import dataclass

import numpy as np


LIMIT_NONE = 0
LIMIT_SLOPE = 1
LIMIT_ROUGHNESS = 2
LIMIT_STEP_HEIGHT = 3
LIMIT_UNCERTAINTY = 4
LIMIT_LOW_CONFIDENCE = 5
LIMIT_INVALID = 255
TRAVERSABILITY_COLUMN_COUNT = 11


@dataclass(frozen=True)
class TraversabilityConfig:
    """Configuration for continuous prototype terrain scoring."""

    composition_mode: str = 'weighted_sum'
    slope_free: float = np.deg2rad(5.0)
    slope_max: float = np.deg2rad(30.0)
    roughness_free: float = 0.002
    roughness_max: float = 0.025
    step_free: float = 0.005
    step_max: float = 0.056
    variance_free: float = 0.000025
    variance_max: float = 0.0004
    coverage_min: float = 0.60
    confidence_min: float = 0.10
    minimum_neighbors: int = 8
    weight_slope: float = 0.35
    weight_roughness: float = 0.20
    weight_step: float = 0.30
    weight_uncertainty: float = 0.15


@dataclass(frozen=True)
class TraversabilityStats:
    """Summary values from one deterministic scoring operation."""

    input_cells: int
    valid_cells: int
    invalid_cells: int
    median_traversability: float
    minimum_traversability: float
    maximum_traversability: float
    median_slope_penalty: float
    median_roughness_penalty: float
    median_step_penalty: float
    median_uncertainty_penalty: float
    limiting_factor_counts: tuple


def smooth_penalty(values, free_reference, maximum_reference):
    """Map values continuously to [0, 1] using cubic smoothstep."""
    if (
        not np.isfinite(free_reference)
        or not np.isfinite(maximum_reference)
        or maximum_reference <= free_reference
    ):
        raise ValueError('maximum reference must exceed free reference')
    values = np.asarray(values, dtype=np.float64)
    normalized = np.clip(
        (values - free_reference) / (maximum_reference - free_reference),
        0.0,
        1.0,
    )
    return normalized * normalized * (3.0 - 2.0 * normalized)


def normalized_weights(config):
    """Validate and normalize weighted-sum coefficients."""
    weights = np.asarray([
        config.weight_slope,
        config.weight_roughness,
        config.weight_step,
        config.weight_uncertainty,
    ], dtype=np.float64)
    if not np.all(np.isfinite(weights)) or np.any(weights < 0.0):
        raise ValueError('traversability weights must be finite and nonnegative')
    total = float(np.sum(weights))
    if total <= 0.0:
        raise ValueError('at least one traversability weight must be positive')
    return weights / total


def _validate_config(config):
    if config.composition_mode not in ('weighted_sum', 'conservative_max'):
        raise ValueError('unsupported traversability composition mode')
    for lower_name, upper_name in (
        ('slope_free', 'slope_max'),
        ('roughness_free', 'roughness_max'),
        ('step_free', 'step_max'),
        ('variance_free', 'variance_max'),
    ):
        lower = getattr(config, lower_name)
        upper = getattr(config, upper_name)
        if lower < 0.0 or upper <= lower or not np.isfinite(upper):
            raise ValueError(f'invalid references: {lower_name}, {upper_name}')
    if not 0.0 <= config.coverage_min < 1.0:
        raise ValueError('coverage_min must be in [0, 1)')
    if not 0.0 <= config.confidence_min < 1.0:
        raise ValueError('confidence_min must be in [0, 1)')
    if config.minimum_neighbors < 0:
        raise ValueError('minimum_neighbors cannot be negative')
    normalized_weights(config)


def uncertainty_penalties(variance, coverage, confidence, config):
    """Return aggregate and component measurement-quality penalties."""
    variance_penalty = smooth_penalty(
        variance, config.variance_free, config.variance_max
    )
    coverage_penalty = smooth_penalty(
        1.0 - np.asarray(coverage), 0.0, 1.0 - config.coverage_min
    )
    confidence_penalty = smooth_penalty(
        1.0 - np.asarray(confidence), 0.0, 1.0 - config.confidence_min
    )
    uncertainty = np.maximum.reduce([
        variance_penalty, coverage_penalty, confidence_penalty
    ])
    return (
        np.clip(uncertainty, 0.0, 1.0),
        np.clip(variance_penalty, 0.0, 1.0),
        np.clip(coverage_penalty, 0.0, 1.0),
        np.clip(confidence_penalty, 0.0, 1.0),
    )


def compose_traversability(penalties, config):
    """Compose four penalty columns into bounded traversability scores."""
    penalties = np.clip(np.asarray(penalties, dtype=np.float64), 0.0, 1.0)
    if penalties.ndim != 2 or penalties.shape[1] != 4:
        raise ValueError('penalties must have shape (N, 4)')
    if config.composition_mode == 'weighted_sum':
        combined = penalties @ normalized_weights(config)
    elif config.composition_mode == 'conservative_max':
        combined = np.max(penalties, axis=1)
    else:
        raise ValueError('unsupported traversability composition mode')
    return np.clip(1.0 - combined, 0.0, 1.0)


def compose_geometry_penalty(penalties, config):
    """Compose slope, roughness, and step separately from data quality."""
    penalties = np.clip(np.asarray(penalties, dtype=np.float64), 0.0, 1.0)
    if penalties.ndim != 2 or penalties.shape[1] != 3:
        raise ValueError('geometry penalties must have shape (N, 3)')
    if config.composition_mode == 'conservative_max':
        return np.max(penalties, axis=1)
    weights = normalized_weights(config)[:3]
    weights /= np.sum(weights)
    return np.clip(penalties @ weights, 0.0, 1.0)


def select_limiting_factors(
    slope, roughness, step, variance, coverage, confidence, config
):
    """Select deterministic dominant contributions to the active score."""
    components = np.column_stack((
        slope,
        roughness,
        step,
        np.maximum(variance, coverage),
        confidence,
    ))
    if config.composition_mode == 'weighted_sum':
        weights = normalized_weights(config)
        components *= np.asarray([
            weights[0], weights[1], weights[2], weights[3], weights[3]
        ])
    codes = np.asarray([
        LIMIT_SLOPE,
        LIMIT_ROUGHNESS,
        LIMIT_STEP_HEIGHT,
        LIMIT_UNCERTAINTY,
        LIMIT_LOW_CONFIDENCE,
    ], dtype=np.uint8)
    factors = codes[np.argmax(components, axis=1)]
    factors[np.max(components, axis=1) <= np.finfo(float).eps] = LIMIT_NONE
    return factors


def _empty_stats(input_count=0):
    return TraversabilityStats(
        input_count, 0, input_count, np.nan, np.nan, np.nan,
        np.nan, np.nan, np.nan, np.nan, tuple([0] * 7)
    )


def compute_traversability(rows, config=TraversabilityConfig()):
    """
    Score terrain-feature rows without classifying terrain as safe or unsafe.

    Input columns follow /terrain/features. Output columns are x, y, z,
    traversability, slope_penalty, roughness_penalty, step_penalty,
    uncertainty_penalty, confidence, valid, and limiting_factor.
    Invalid input cells remain present with a NaN traversability value.
    """
    _validate_config(config)
    rows = np.asarray(rows, dtype=np.float64)
    if rows.size == 0:
        return np.empty((0, TRAVERSABILITY_COLUMN_COUNT)), _empty_stats()
    if rows.ndim != 2 or rows.shape[1] != 11:
        raise ValueError('feature rows must have shape (N, 11)')
    order = np.lexsort((rows[:, 1], rows[:, 0]))
    rows = rows[order]
    finite = np.all(np.isfinite(rows), axis=1)
    valid = (
        finite
        & (rows[:, 8] >= config.minimum_neighbors)
        & (rows[:, 9] >= config.coverage_min)
        & (rows[:, 10] >= config.confidence_min)
    )
    safe_rows = np.nan_to_num(
        rows, nan=np.inf, posinf=np.inf, neginf=np.inf
    )
    slope_penalty = smooth_penalty(
        safe_rows[:, 3], config.slope_free, config.slope_max
    )
    roughness_penalty = smooth_penalty(
        safe_rows[:, 4], config.roughness_free, config.roughness_max
    )
    step_penalty = smooth_penalty(
        safe_rows[:, 5], config.step_free, config.step_max
    )
    uncertainty, variance_penalty, coverage_penalty, confidence_penalty = (
        uncertainty_penalties(
            safe_rows[:, 6],
            safe_rows[:, 9],
            safe_rows[:, 10],
            config,
        )
    )
    penalty_columns = np.column_stack((
        slope_penalty, roughness_penalty, step_penalty, uncertainty
    ))
    traversability = compose_traversability(penalty_columns, config)
    traversability[~valid] = np.nan
    factors = select_limiting_factors(
        slope_penalty,
        roughness_penalty,
        step_penalty,
        variance_penalty,
        coverage_penalty,
        confidence_penalty,
        config,
    )
    factors[~valid] = LIMIT_INVALID
    output = np.column_stack((
        rows[:, :3],
        traversability,
        penalty_columns,
        rows[:, 10],
        valid.astype(np.uint8),
        factors,
    ))
    valid_output = output[valid]
    if not len(valid_output):
        return output, _empty_stats(len(rows))
    counts = tuple(
        int(np.count_nonzero(factors == code))
        for code in (
            LIMIT_NONE,
            LIMIT_SLOPE,
            LIMIT_ROUGHNESS,
            LIMIT_STEP_HEIGHT,
            LIMIT_UNCERTAINTY,
            LIMIT_LOW_CONFIDENCE,
            LIMIT_INVALID,
        )
    )
    stats = TraversabilityStats(
        input_cells=len(rows),
        valid_cells=int(np.count_nonzero(valid)),
        invalid_cells=int(np.count_nonzero(~valid)),
        median_traversability=float(np.median(valid_output[:, 3])),
        minimum_traversability=float(np.min(valid_output[:, 3])),
        maximum_traversability=float(np.max(valid_output[:, 3])),
        median_slope_penalty=float(np.median(valid_output[:, 4])),
        median_roughness_penalty=float(np.median(valid_output[:, 5])),
        median_step_penalty=float(np.median(valid_output[:, 6])),
        median_uncertainty_penalty=float(np.median(valid_output[:, 7])),
        limiting_factor_counts=counts,
    )
    return output, stats
