"""
Tests for the dual-rover evaluation layer.

The property that matters is not the exact score. It is that ONE terrain record
scored against TWO rover specs produces two genuinely different maps, and that
the difference comes from the specs rather than from any scaling of one result
into the other. CLAUDE.md is explicit that lambda is a terrain x rover
interaction, so a scaled map would be physically wrong, not merely imprecise.
"""

import math

import numpy as np
import pytest
from space_mission import soil_model
from space_mission.rover_spec import (
    PROVENANCE_ASSUMED,
    PROVENANCE_MEASURED,
    RoverSpec,
)
from space_mission.traversability_transform import (
    evaluate,
    evaluate_both,
    LIMIT_NO_DATA,
    LIMIT_SLOPE,
    LIMIT_STEP,
    ObservationGate,
    ScoringConfig,
    smooth_penalty,
    TerrainGrid,
)


SMALL = RoverSpec(
    rover_id='small', mass_kg=2.725, wheel_radius_m=0.070,
    wheel_width_m=0.040, ground_pressure_kpa=3.157,
    max_climb_angle_rad=0.349, min_passable_width_m=0.300,
    ground_clearance_m=0.030, has_grousers=False,
    provenance=PROVENANCE_MEASURED,
)

MEDIUM = RoverSpec(
    rover_id='medium', mass_kg=50.0, wheel_radius_m=0.200,
    wheel_width_m=0.100, ground_pressure_kpa=8.0,
    max_climb_angle_rad=0.436, min_passable_width_m=0.800,
    ground_clearance_m=0.250, has_grousers=True,
    provenance=PROVENANCE_ASSUMED,
)


def _grid(slope, roughness, step, soil, confidence=0.9, samples=3.0):
    n = len(slope)
    return TerrainGrid(
        resolution_m=0.05,
        slope_rad=np.asarray(slope, dtype=float),
        roughness_m=np.asarray(roughness, dtype=float),
        step_height_m=np.asarray(step, dtype=float),
        slip_small=np.zeros(n),
        slip_quality=np.full(n, confidence),
        slip_samples=np.full(n, samples),
        soil_difficulty=np.asarray(soil, dtype=float),
        soil_confidence=np.full(n, confidence),
    )


def test_flat_clean_terrain_scores_one():
    """With every penalty at zero the score must be exactly 1, not merely high."""
    grid = _grid([0.0], [0.0], [0.0], [0.0])
    assert evaluate(grid, SMALL).score[0] == pytest.approx(1.0)


def test_step_past_the_small_wheel_is_impassable_but_medium_passes():
    """
    The central claim of the dual-map design, as a test.

    A 36 mm step exceeds the small rover's 35 mm limit (half its 70 mm wheel) so
    it must be vetoed outright, while the medium rover's 100 mm limit leaves it
    traversable. No scaling of one score could produce this: it is a sign change
    in passability, not a magnitude difference.
    """
    grid = _grid([0.05], [0.004], [0.036], [0.05])
    small, medium = evaluate_both(grid, SMALL, MEDIUM)

    assert small.score[0] == 0.0
    assert small.limiting_factor[0] == LIMIT_STEP
    assert medium.score[0] > 0.5


def test_slope_past_the_small_limit_is_impassable_but_medium_passes():
    """Same asymmetry on the slope axis, from the specs' climb angles."""
    grid = _grid([0.40], [0.003], [0.004], [0.15])
    small, medium = evaluate_both(grid, SMALL, MEDIUM)

    assert 0.349 < 0.40 < 0.436, 'fixture must straddle the two climb limits'
    assert small.score[0] == 0.0
    assert small.limiting_factor[0] == LIMIT_SLOPE
    assert medium.score[0] > 0.0


def test_medium_is_not_a_scaled_small():
    """
    The two maps must not be related by any single factor.

    If they were, one could be derived from the other and the whole transform
    layer would be unnecessary -- and wrong, because lambda does not transfer
    between rovers.
    """
    grid = _grid(
        [0.00, 0.15, 0.30, 0.05],
        [0.001, 0.010, 0.005, 0.020],
        [0.000, 0.010, 0.004, 0.030],
        [0.00, 0.20, 0.40, 0.10],
    )
    small, medium = evaluate_both(grid, SMALL, MEDIUM)

    usable = ~np.isnan(small.score) & (small.score > 0.0)
    ratios = medium.score[usable] / small.score[usable]
    assert ratios.max() - ratios.min() > 0.05, (
        'scores differ by a constant factor, which would mean the specs are not '
        'actually changing the evaluation'
    )


def test_nan_input_yields_nan_and_no_data_not_zero():
    """
    Unknown must never read as traversable-but-bad.

    A planner treats 0.0 as "passable, costly" and NaN as "unknown". Collapsing
    the two would send the rover into unsurveyed ground at a low cost.
    """
    grid = _grid([math.nan], [0.004], [0.004], [0.05])
    result = evaluate(grid, SMALL)

    assert math.isnan(result.score[0])
    assert result.limiting_factor[0] == LIMIT_NO_DATA


def test_low_soil_confidence_is_gated_out_when_a_floor_is_set():
    """
    The confidence gate must reject, not down-weight.

    A low-confidence soil estimate is not a slightly-worse cell; it is a cell we
    have not really measured.
    """
    grid = _grid([0.05], [0.004], [0.004], [0.05], confidence=0.05)
    gate = ObservationGate(min_soil_confidence=0.5)

    assert math.isnan(evaluate(grid, SMALL, gate=gate).score[0])
    # With no floor configured the same cell is scored normally.
    assert not math.isnan(evaluate(grid, SMALL).score[0])


def test_scores_stay_within_zero_and_one():
    """Extreme inputs must not produce out-of-range scores."""
    grid = _grid(
        [0.0, 1.5, 0.2], [0.0, 0.5, 0.01], [0.0, 0.3, 0.002], [0.0, 1.0, 0.5]
    )
    score = evaluate(grid, SMALL).score
    finite = score[~np.isnan(score)]

    assert finite.min() >= 0.0
    assert finite.max() <= 1.0


def test_weights_are_normalised_so_adding_a_term_cannot_rescale_maps():
    """
    Doubling every weight must leave the score unchanged.

    Otherwise introducing a fifth penalty later would silently shift every
    previously published map.
    """
    grid = _grid([0.15], [0.010], [0.010], [0.20])
    doubled = ScoringConfig(
        weight_slope=0.60, weight_roughness=0.30,
        weight_step=0.50, weight_soil=0.60,
    )

    assert evaluate(grid, SMALL).score[0] == pytest.approx(
        evaluate(grid, SMALL, config=doubled).score[0]
    )


def test_smooth_penalty_is_zero_at_free_and_one_at_saturation():
    """Endpoint behaviour, since every term depends on this curve."""
    assert smooth_penalty([0.005], 0.005, 0.035)[0] == pytest.approx(0.0)
    assert smooth_penalty([0.035], 0.005, 0.035)[0] == pytest.approx(1.0)
    assert smooth_penalty([0.001], 0.005, 0.035)[0] == pytest.approx(0.0)
    assert smooth_penalty([0.100], 0.005, 0.035)[0] == pytest.approx(1.0)
    assert math.isnan(smooth_penalty([math.nan], 0.005, 0.035)[0])


def test_soil_model_separates_slope_from_soil():
    """
    The estimation layer's whole job, as a test.

    Slipping 30% on flat ground says a great deal about the soil; slipping 30%
    on a slope near the rover's limit says almost nothing, because the slope
    alone explains it.
    """
    on_flat = soil_model.estimate_soil_difficulty(0.30, 0.0, SMALL)
    on_slope = soil_model.estimate_soil_difficulty(0.30, 0.34, SMALL)

    assert on_flat > on_slope
    assert on_slope == pytest.approx(0.0)


def test_soil_confidence_rises_with_sample_count():
    """
    Confidence must accrue as the rover works.

    A cell crossed once and a cell crossed ten times are not equally
    trustworthy; a model that ignored count would report the same confidence on
    the first pass as on the tenth.
    """
    values = [
        soil_model.estimate_soil_confidence(n, 1.0) for n in (1, 2, 3, 10)
    ]

    assert values == sorted(values)
    assert values[0] < values[-1]
    assert all(0.0 <= v < 1.0 for v in values), 'must never claim certainty'


def test_soil_quality_gate_rejects_bad_samples_before_estimation():
    """
    The gate runs upstream of the soil proxy.

    A low-confidence lambda reaching the estimation layer corrupts it, and both
    maps derive from that layer -- so one bad sample would break S_small and
    S_medium together.
    """
    assert soil_model.accepts_sample(0.8, 0.3) is True
    assert soil_model.accepts_sample(0.1, 0.3) is False
    assert soil_model.accepts_sample(math.nan, 0.3) is False
    assert soil_model.accepts_sample(None, 0.3) is False


def test_negative_slip_does_not_read_as_easy_soil():
    """
    Rolling downhill faster than the wheels turn is not evidence of good soil.

    Clamping at zero keeps a downhill artefact from ranking a cell as the best
    terrain on the map.
    """
    assert soil_model.estimate_soil_difficulty(-0.5, 0.0, SMALL) == 0.0


def test_evaluate_rejects_an_incoherent_spec():
    """A spec that cannot describe a real rover must fail before scoring."""
    broken = RoverSpec(
        rover_id='broken', mass_kg=-1.0, wheel_radius_m=0.07,
        wheel_width_m=0.04, ground_pressure_kpa=3.0,
        max_climb_angle_rad=0.3, min_passable_width_m=0.3,
        ground_clearance_m=0.03, has_grousers=False,
    )
    with pytest.raises(ValueError):
        evaluate(_grid([0.0], [0.0], [0.0], [0.0]), broken)
