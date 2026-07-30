"""
CLAUDE.md 1.4 verdict thresholds -- mission POLICY, not rover capability.

Pure and ROS-free like :mod:`space_mission.slip_math`.

Why this is its own module
--------------------------
"Slope limit" meant three unrelated things in this tree, all under names close
enough to be mistaken for each other:

    mechanical capability    RoverSpec.max_climb_angle_rad       (ramp test)
    mission verdict boundary VerdictThresholds.hazard_slope_rad  (here, 20 deg)
    scoring curve shape      ScoringConfig.slope_penalty_saturation_rad (30 deg)

They are connected by policy, never by arithmetic. Deriving one from another --
the reflex that is correct for ``step_max``, which really is half a wheel
radius -- would be wrong here: a mission may cap itself well below what the
vehicle can do, and a penalty curve may saturate above the hazard line so that
scores keep discriminating past it. Once a ramp test yields the mechanical
limit, "what fraction of it should the hazard boundary be" becomes an explicit
decision instead of an accident of naming.

Marker placement does NOT use these thresholds
----------------------------------------------
CLAUDE.md 1.5 flags this as the recurring mistake. A verdict here describes
terrain as OUR rover found it. Marker sites are chosen on ``S_medium``, because
the marker's consumer is the medium rover: a site our 3 kg rover calls SAFE may
sit in a gap the medium rover cannot enter, which makes the marker worthless.
Use this module for our own driving decisions; use the medium map for markers.
"""

from dataclasses import dataclass


VERDICT_UNKNOWN = 'unknown'
VERDICT_SAFE = 'safe'
VERDICT_MARGINAL = 'marginal'
VERDICT_HAZARD = 'hazard'


@dataclass(frozen=True)
class VerdictThresholds:
    """
    The CLAUDE.md 1.4 decision table, transcribed once.

    Two properties of that table are worth stating because they are easy to
    misread from the prose:

    1. ``safe_slope_rad`` and ``hazard_slope_rad`` are the SAME boundary (SAFE
       requires < 20 deg, HAZARD triggers at >= 20 deg). Slope is therefore
       binary: it can never by itself produce a MARGINAL verdict. Both names
       are kept so that a future decision to open a slope band between them is
       a one-line config change rather than a re-reading of the table.
    2. MARGINAL arises only from the slip band (15% to 40%) or from roughness.

    Roughness has no value here on purpose -- see :data:`safe_roughness_m`.
    """

    #: CLAUDE.md 1.4: SAFE requires slope < 20 deg.
    safe_slope_rad: float = 0.349

    #: CLAUDE.md 1.4: HAZARD at slope >= 20 deg. Same boundary as above.
    hazard_slope_rad: float = 0.349

    #: CLAUDE.md 1.4: SAFE requires slip < 15%.
    safe_slip_ratio: float = 0.15

    #: CLAUDE.md 1.4: HAZARD at slip >= 40%. The 15-40% band is MARGINAL.
    hazard_slip_ratio: float = 0.40

    #: CLAUDE.md 1.4 writes this as "roughness < sigma_0" and never defines
    #: sigma_0. There is no defensible default, so this stays None until it is
    #: measured on arena sand; :meth:`validate` refuses to run without it
    #: rather than inventing a number that would silently pass every cell.
    safe_roughness_m: float = None

    def validate(self):
        """
        Raise ``ValueError`` if the table is unusable or self-contradictory.

        Specifically refuses a ``None`` ``safe_roughness_m``: a missing
        threshold that defaulted to infinity would mark every cell SAFE on the
        roughness axis, which is exactly the kind of silent pass that
        ``step_max`` taught us to reject.
        """
        raise NotImplementedError


def classify(slope_rad, slip_ratio, roughness_m, step_height_m, spec, thresholds):
    """
    Return one of the ``VERDICT_*`` values for a single cell.

    ``spec`` supplies the step limit rather than ``thresholds``: CLAUDE.md 1.4
    lists "obstacle / step" among the HAZARD conditions, but how tall a step is
    impassable is a property of the wheel, not a mission choice, so it comes
    from ``RoverSpec.max_step_height_m``. Mixing it into the threshold table is
    how such values went stale in the first place.

    Returns ``VERDICT_UNKNOWN`` when any input is NaN. A missing measurement
    must never read as SAFE.
    """
    raise NotImplementedError
