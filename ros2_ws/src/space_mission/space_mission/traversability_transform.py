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
    """

    score: object
    limiting_factor: object


def evaluate(terrain, spec, config=ScoringConfig(), gate=ObservationGate()):
    """
    Score ``terrain`` for the rover described by ``spec``.

    This is the single evaluation entry point for every rover. ``spec`` is the
    only rover-dependent input; passing the medium rover's spec is the entire
    difference between S_medium and S_small.

    Returns a :class:`ScoreGrid`. Cells that fail ``gate``, or whose terrain
    inputs are NaN, come back as NaN with ``LIMIT_NO_DATA`` -- never as zero,
    which a planner would read as "traversable but bad" rather than "unknown".

    Hard limits from ``spec`` (``max_climb_angle_rad``, ``max_step_height_m``,
    ``ground_clearance_m``, ``min_passable_width_m``) veto a cell outright
    rather than contributing a weighted penalty: a step taller than the wheel
    can climb is not "somewhat worse", it is impassable, and no weighting of
    other terms should be able to outvote that.
    """
    raise NotImplementedError


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
