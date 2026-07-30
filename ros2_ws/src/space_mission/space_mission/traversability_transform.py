"""
Evaluation layer: terrain estimate x rover spec -> per-rover traversability.

Pure and ROS-free like :mod:`space_mission.slip_math`. Deliberately NOT inside
``traversability_fusion_node``: the medium rover's specification is an external
parameter we do not control and expect to change, small and medium must not
share a code path where their parameters can be crossed, and a third rover
should cost one more spec rather than one more branch.

The layering (CLAUDE.md, dual-rover transform layer)
----------------------------------------------------
    observation   terrain geometry + lambda our rover actually felt
                            |
    estimation    soil_model: lambda + our spec -> soil difficulty rank
                            |
              +-------------+-------------+
    evaluation  [small spec]         [medium spec]
                S_small               S_medium

Only observation and estimation are canonical; both scores are derived. The
same :func:`evaluate` runs for both rovers -- a different spec goes in, never
different code, and never a scaling of one score into the other. Scaling would
be physically wrong: lambda is a terrain x rover interaction, so the sand that
slips our 3 kg rover 15% behaves differently under a medium rover's contact
pressure, wheel diameter, mass, and grousers.

What belongs in which config
----------------------------
``TraversabilityConfig`` in ``space_perception`` currently mixes three kinds of
value, which is how ``step_max`` went stale when the wheels changed:

    rover limits      -> RoverSpec (max_climb_angle, max_step_height, ...)
    observation gates -> ObservationGate (coverage, confidence, slip quality)
    scoring weights   -> ScoringConfig (below)

:class:`ScoringConfig` therefore holds weights and composition only. If a field
here can be derived from the rover, it is in the wrong place.
"""

from dataclasses import dataclass

import numpy as np


#: Bumped on any change to score arithmetic; stamped into TraversabilityScore
#: alongside the soil model version, since weights and the soil proxy change
#: independently.
EVALUATOR_VERSION = '0.1.0'


@dataclass(frozen=True)
class ObservationGate:
    """
    Quality floors a cell must clear before it is evaluated at all.

    ``min_slip_quality`` is applied by the estimation layer, upstream of this
    one (see :mod:`space_mission.soil_model`); it is named here only so the
    two stages can be configured from one block. Gating slip at the score
    stage would be too late -- the soil estimate would already be polluted,
    and both maps derive from it.
    """

    min_slip_quality: float = 0.3
    min_soil_confidence: float = 0.0
    coverage_min: float = 0.60
    confidence_min: float = 0.10


@dataclass(frozen=True)
class ScoringConfig:
    """
    Weights and composition for the score. No rover limits, no gates.

    Weights are relative; the evaluator normalises them so that adding a term
    later does not silently rescale every existing map.
    """

    composition_mode: str = 'weighted_sum'
    weight_slope: float = 0.30
    weight_roughness: float = 0.15
    weight_step: float = 0.25
    weight_soil: float = 0.30

    #: Below these, the term contributes nothing. Observation allowances, not
    #: rover limits: sensor noise should not read as terrain.
    slope_free_rad: float = 0.0872665
    roughness_free_m: float = 0.002
    step_free_m: float = 0.005

    #: Roughness at which the penalty saturates. A discrimination range for the
    #: arena, not a rover property -- unlike the step limit, which comes from
    #: the spec.
    roughness_saturation_m: float = 0.025

    #: Slope at which the slope penalty saturates -- a pure curve-shape knob,
    #: NOT a rover limit and NOT a hazard boundary. Inherits the 30 deg that
    #: ``space_perception``'s ``slope_max`` used, which was only ever a
    #: saturation point despite sharing a name with two other concepts. See
    #: ``RoverSpec.max_climb_angle_rad`` for the split.
    slope_penalty_saturation_rad: float = 0.5236


@dataclass(frozen=True)
class TerrainGrid:
    """
    Plain-array view of ``space_msgs/TerrainEstimate``.

    Each field is a 2-D array on a shared grid; NaN means "no data" and is
    distinct from a measured zero. Keeping a ROS-free view lets the whole
    evaluation layer be tested from arrays, exactly as ``slip_math`` is tested
    without a node.
    """

    resolution_m: float
    slope_rad: object
    roughness_m: object
    step_height_m: object
    slip_small: object
    slip_quality: object
    slip_samples: object
    soil_difficulty: object
    soil_confidence: object


@dataclass(frozen=True)
class ScoreGrid:
    """
    Plain-array result of :func:`evaluate`.

    ``limiting_factor`` records which term dominated each cell so a low score
    is explainable instead of opaque; values match the ``LIMIT_*`` constants in
    ``space_msgs/TraversabilityScore``.

    ``soil_measured`` is True only where the rover actually drove and produced a
    slip sample. Elsewhere the score is GEOMETRY-ONLY -- still useful, and still
    the mission's primary product per CLAUDE.md 4, but it carries none of the
    information that only driving on the terrain can provide. A consumer that
    treats the two as equivalent is claiming knowledge the rover does not have.
    """

    score: object
    limiting_factor: object
    soil_measured: object = None


#: Values written into ``ScoreGrid.limiting_factor``. Mirror the ``LIMIT_*``
#: constants in ``space_msgs/TraversabilityScore`` so the node can copy them
#: through without a translation table.
LIMIT_NONE = 0
LIMIT_SLOPE = 1
LIMIT_ROUGHNESS = 2
LIMIT_STEP = 3
LIMIT_SOIL = 4
LIMIT_CLEARANCE = 5
LIMIT_WIDTH = 6
LIMIT_NO_DATA = 7


def smooth_penalty(values, free, saturation):
    """
    Return a smoothstep penalty in ``[0, 1]`` for each value.

    Zero at or below ``free``, one at or above ``saturation``, and
    ``3t^2 - 2t^3`` between. The same curve ``space_perception`` uses, so the
    two layers stay comparable. NaN propagates.
    """
    values = np.asarray(values, dtype=float)
    span = float(saturation) - float(free)
    if span <= 0.0:
        # A degenerate range would divide by zero; treat anything above `free`
        # as saturated rather than silently emitting inf.
        return np.where(np.isnan(values), np.nan,
                        np.where(values > free, 1.0, 0.0))
    t = np.clip((values - float(free)) / span, 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def evaluate(terrain, spec, config=ScoringConfig(), gate=ObservationGate()):
    """
    Score ``terrain`` for the rover described by ``spec``.

    This is the single evaluation entry point for every rover. ``spec`` is the
    only rover-dependent input; passing the medium rover's spec is the entire
    difference between S_medium and S_small.

    Returns a :class:`ScoreGrid`. Cells that fail ``gate``, or whose terrain
    inputs are NaN, come back as NaN with ``LIMIT_NO_DATA`` -- never as zero,
    which a planner would read as "traversable but bad" rather than "unknown".

    Hard limits from ``spec`` (``max_climb_angle_rad``, ``max_step_height_m``)
    veto a cell outright rather than contributing a weighted penalty: a step
    taller than the wheel can climb is not "somewhat worse", it is impassable,
    and no weighting of other terms should be able to outvote that.
    ``ground_clearance_m`` and ``min_passable_width_m`` have no corresponding
    terrain layer yet -- obstacle height and gap width are not measured -- so
    they are accepted in the signature but unused, rather than faked from step
    height.
    """
    spec.validate()

    slope = np.asarray(terrain.slope_rad, dtype=float)
    roughness = np.asarray(terrain.roughness_m, dtype=float)
    step = np.asarray(terrain.step_height_m, dtype=float)
    soil = np.asarray(terrain.soil_difficulty, dtype=float)
    soil_confidence = np.asarray(terrain.soil_confidence, dtype=float)

    penalties = {
        LIMIT_SLOPE: (
            config.weight_slope,
            smooth_penalty(
                np.abs(slope),
                config.slope_free_rad,
                config.slope_penalty_saturation_rad,
            ),
        ),
        LIMIT_ROUGHNESS: (
            config.weight_roughness,
            smooth_penalty(
                roughness, config.roughness_free_m, config.roughness_saturation_m
            ),
        ),
        # Saturates at the ROVER's step limit, not at a configured threshold.
        LIMIT_STEP: (
            config.weight_step,
            smooth_penalty(step, config.step_free_m, spec.max_step_height_m),
        ),
        LIMIT_SOIL: (config.weight_soil, np.clip(soil, 0.0, 1.0)),
    }

    if sum(weight for weight, _ in penalties.values()) <= 0.0:
        raise ValueError('scoring weights must sum to a positive value')

    # Normalise PER CELL over the terms that cell actually has, rather than over
    # all four unconditionally.
    #
    # The soil term only exists where the rover has driven, because lambda is
    # measured by driving. Requiring it everywhere collapsed the map to the
    # driven path: on a survey with 776 cells of geometry, only 8 had slip, so
    # 768 cells with perfectly good slope, roughness and step data were
    # discarded as "no data". That also contradicts CLAUDE.md 4, which puts
    # geometry first and treats slip as what geometry cannot tell you -- an
    # addition, not a precondition.
    #
    # So a cell with geometry but no slip gets a GEOMETRY-ONLY score, and
    # `soil_measured` in the result records which cells those are. Renormalising
    # rather than substituting zero matters: a zero soil penalty would read as
    # "measured, and the soil is perfect".
    available = {
        key: np.isfinite(values) for key, (_, values) in penalties.items()
    }
    weight_sum = sum(
        weight * available[key].astype(float)
        for key, (weight, _) in penalties.items()
    )
    weighted = {
        key: np.where(
            available[key],
            weight * np.nan_to_num(values, nan=0.0)
            / np.maximum(weight_sum, 1e-12),
            0.0,
        )
        for key, (weight, values) in penalties.items()
    }

    score = 1.0 - sum(weighted.values())
    soil_measured = available[LIMIT_SOIL]

    keys = list(weighted)
    stacked = np.stack([weighted[key] for key in keys], axis=0)
    with np.errstate(invalid='ignore'):
        dominant = np.nanargmax(
            np.where(np.isnan(stacked), -np.inf, stacked), axis=0
        )
    limiting = np.asarray(
        np.take(np.asarray(keys), dominant), dtype=np.uint8
    )
    limiting = np.where(
        np.nanmax(np.where(np.isnan(stacked), 0.0, stacked), axis=0) <= 0.0,
        LIMIT_NONE, limiting,
    ).astype(np.uint8)

    # --- Hard vetoes: impassable is not "worse", it is out ------------------
    impassable_slope = np.abs(slope) >= spec.max_climb_angle_rad
    impassable_step = step > spec.max_step_height_m
    score = np.where(impassable_slope | impassable_step, 0.0, score)
    limiting = np.where(impassable_step, LIMIT_STEP, limiting).astype(np.uint8)
    limiting = np.where(
        impassable_slope & ~impassable_step, LIMIT_SLOPE, limiting
    ).astype(np.uint8)

    # --- No data beats every other verdict --------------------------------
    # Geometry is a precondition; soil is not. A cell with no geometry has not
    # been observed at all.
    unknown = np.isnan(slope) | np.isnan(roughness) | np.isnan(step)
    if gate.min_soil_confidence > 0.0:
        unknown = unknown | (
            np.isnan(soil_confidence)
            | (soil_confidence < gate.min_soil_confidence)
        )
    score = np.where(unknown, np.nan, np.clip(score, 0.0, 1.0))
    limiting = np.where(unknown, LIMIT_NO_DATA, limiting).astype(np.uint8)

    return ScoreGrid(
        score=score, limiting_factor=limiting, soil_measured=soil_measured
    )


def evaluate_both(terrain, small_spec, medium_spec, config=ScoringConfig(),
                  gate=ObservationGate()):
    """
    Return ``(S_small, S_medium)`` from one terrain record.

    The point of the whole layer, in one call: the same terrain, the same
    ``evaluate``, two specs. Never a scaling of one result into the other --
    lambda is a terrain x rover interaction, so the sand that slips our 2.7 kg
    rover behaves differently under a medium rover's contact pressure, wheel
    diameter, mass, and grousers.
    """
    return (
        evaluate(terrain, small_spec, config, gate),
        evaluate(terrain, medium_spec, config, gate),
    )


def exploration_objective(score, frontier_proximity, weight_information):
    """
    Combine traversability with information gain for our own rover.

    Published on ``/exploration/objective``, deliberately NOT as a layer of
    ``/traversability/small``.

    CLAUDE.md's objective for the small rover is "easy to reach AND
    informative", but that is a conceptual statement; at implementation level
    the two must not share a topic:

    - **Lifetime.** A terrain measurement is a permanent asset -- the medium
      rover will still be using it later. An exploration objective is volatile,
      changing every time the rover moves. Fusing them drags the canonical
      record's lifetime down to that of the volatile term.
    - **Update rate.** The exploration term must be recomputed as the frontier
      shifts; terrain layers must not be. One topic would force the whole grid
      to republish at the faster rate.
    - **Symmetry.** It would make ``/traversability/small`` and
      ``/traversability/medium`` different kinds of quantity, breaking the
      one-function-two-specs property that keeps the maps comparable.
    - The medium rover never explores on our behalf, so the term is meaningless
      in its map.

    Consequently ``/exploration/objective`` carries a bare
    ``grid_map_msgs/GridMap`` rather than a ``space_msgs`` wrapper: provenance
    metadata exists so a canonical record can be re-derived later, and this
    product is explicitly not canonical. The absence of that metadata is the
    type-level statement that it is disposable.
    """
    raise NotImplementedError
