"""
Rover physical specification -- the evaluation layer's only rover input.

Pure and ROS-free like :mod:`space_mission.slip_math`, so the derived limits
can be unit-tested without a graph.

Why this module exists
----------------------
Rover limits kept masquerading as tuning constants.
``space_perception.traversability.TraversabilityConfig`` ships
``step_max = 0.056``, and ``docs/traversability.md`` records its origin as
"half the current 0.112 m wheel radius". That is a rover property, not a
threshold. When the CAD import moved the wheel to 0.070 m, nothing recomputed
it, so traversability has been judging steps against a rover 1.6x more capable
than the one we have -- silently, because the arithmetic still succeeds.

The fix is structural, not a corrected number: anything derivable from the
rover is a property here, so it cannot go stale independently of its source.
"""

from dataclasses import dataclass
import math


#: Fraction of wheel radius a wheel can climb over unaided. Retains the
#: ``docs/traversability.md`` rule (half the wheel radius) but anchors it to
#: whatever radius the spec actually carries.
STEP_LIMIT_PER_WHEEL_RADIUS = 0.5

PROVENANCE_UNKNOWN = 'unknown'
PROVENANCE_MEASURED = 'measured'
PROVENANCE_ASSUMED = 'assumed'


@dataclass(frozen=True)
class RoverSpec:
    """
    One rover's physical specification.

    Frozen so an evaluation cannot mutate the spec it was handed; a score is
    only interpretable against an unchanged spec.

    ``provenance`` separates our own rover from the medium rover we do not
    possess. ``PROVENANCE_ASSUMED`` marks every derived score as provisional,
    which is what makes a later recompute targetable rather than global.
    """

    rover_id: str
    mass_kg: float
    wheel_radius_m: float
    wheel_width_m: float
    ground_pressure_kpa: float

    #: MECHANICAL capability only -- the steepest grade the vehicle can climb.
    #: Not the mission's hazard boundary (``verdict.VerdictThresholds``) and not
    #: a scoring saturation point (``ScoringConfig``). One name previously
    #: covered all three, which is how the tree ended up holding 20 deg and
    #: 30 deg for what read as a single parameter. Split, not derived: no
    #: arithmetic relates them, only policy. Once a ramp test gives this
    #: number, "what fraction of it is the hazard boundary" becomes a separate
    #: decision rather than an implicit one.
    max_climb_angle_rad: float

    min_passable_width_m: float
    ground_clearance_m: float
    has_grousers: bool
    provenance: str = PROVENANCE_UNKNOWN
    provenance_note: str = ''

    @property
    def max_step_height_m(self):
        """
        Return the tallest step this rover clears, derived from the wheel.

        Replaces ``TraversabilityConfig.step_max``. Derived rather than
        configured precisely so a wheel change cannot leave it behind.
        """
        return self.wheel_radius_m * STEP_LIMIT_PER_WHEEL_RADIUS

    def validate(self):
        """
        Raise ``ValueError`` if the spec is physically incoherent.

        Catches the failures that would otherwise surface as a plausible but
        wrong map: non-positive mass or wheel radius, a climb angle outside
        (0, pi/2), a passable width narrower than the rover itself, or a
        negative clearance.
        """
        if self.mass_kg <= 0.0:
            raise ValueError(f'{self.rover_id}: mass_kg must be positive')
        if self.wheel_radius_m <= 0.0 or self.wheel_width_m <= 0.0:
            raise ValueError(f'{self.rover_id}: wheel dimensions must be positive')
        if not 0.0 < self.max_climb_angle_rad < math.pi / 2.0:
            raise ValueError(
                f'{self.rover_id}: max_climb_angle_rad must lie in (0, pi/2)'
            )
        if self.min_passable_width_m <= 0.0:
            raise ValueError(
                f'{self.rover_id}: min_passable_width_m must be positive'
            )
        if self.ground_clearance_m < 0.0:
            raise ValueError(
                f'{self.rover_id}: ground_clearance_m cannot be negative'
            )
        if self.ground_pressure_kpa <= 0.0:
            raise ValueError(
                f'{self.rover_id}: ground_pressure_kpa must be positive'
            )
        if self.provenance not in (
            PROVENANCE_UNKNOWN, PROVENANCE_MEASURED, PROVENANCE_ASSUMED
        ):
            raise ValueError(
                f'{self.rover_id}: unknown provenance {self.provenance!r}'
            )
        return self


#: Fields a spec mapping must supply. ``provenance``/``provenance_note`` are
#: optional because they annotate rather than define the rover.
REQUIRED_FIELDS = (
    'rover_id',
    'mass_kg',
    'wheel_radius_m',
    'wheel_width_m',
    'ground_pressure_kpa',
    'max_climb_angle_rad',
    'min_passable_width_m',
    'ground_clearance_m',
    'has_grousers',
)


def load_rover_spec(params):
    """
    Build a :class:`RoverSpec` from a flat parameter mapping.

    ``params`` is the YAML block for one rover (see
    ``config/rover_spec_small.yaml``), already flattened by whatever loaded
    it -- this module stays ROS-free, so a caller passes a plain mapping
    rather than a node.

    Missing keys raise rather than defaulting: a silently defaulted rover
    limit is the exact failure mode this module exists to prevent.
    """
    missing = [name for name in REQUIRED_FIELDS if name not in params]
    if missing:
        raise KeyError(f'rover spec is missing fields: {sorted(missing)}')
    spec = RoverSpec(
        rover_id=str(params['rover_id']),
        mass_kg=float(params['mass_kg']),
        wheel_radius_m=float(params['wheel_radius_m']),
        wheel_width_m=float(params['wheel_width_m']),
        ground_pressure_kpa=float(params['ground_pressure_kpa']),
        max_climb_angle_rad=float(params['max_climb_angle_rad']),
        min_passable_width_m=float(params['min_passable_width_m']),
        ground_clearance_m=float(params['ground_clearance_m']),
        has_grousers=bool(params['has_grousers']),
        provenance=str(params.get('provenance', PROVENANCE_UNKNOWN)),
        provenance_note=str(params.get('provenance_note', '')),
    )
    return spec.validate()


def spec_to_msg(spec):
    """
    Convert a :class:`RoverSpec` into ``space_msgs/RoverSpec``.

    Lives beside the dataclass rather than in the node so the field mapping
    has one home. The caller imports the message type; this module does not,
    keeping it importable without a sourced workspace.
    """
    raise NotImplementedError


def spec_from_msg(msg):
    """Convert a ``space_msgs/RoverSpec`` back into a :class:`RoverSpec`."""
    raise NotImplementedError
