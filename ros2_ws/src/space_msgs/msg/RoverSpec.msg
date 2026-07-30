# Physical specification of ONE rover -- the evaluation layer's only
# rover-dependent input (CLAUDE.md: dual-rover transform layer).
#
# This type exists because rover limits kept leaking into "tuning" configs.
# space_perception's TraversabilityConfig carried step_max = 0.056 m, which
# docs/traversability.md records as "half the current 0.112 m wheel radius" --
# a rover property disguised as a threshold. When the CAD import changed the
# wheel to 0.070 m, that value silently became 1.6x too permissive. Rover
# limits belong here and are derived, never hand-copied.
#
# Embedded in TraversabilityScore so a derived map always travels with the
# assumptions it was computed under.

string rover_id                  # 'small' | 'medium' | ...

float32 mass_kg
float32 wheel_radius_m
float32 wheel_width_m
float32 ground_pressure_kpa      # static, mass / total contact patch

# MECHANICAL limit only: the steepest grade this vehicle can physically climb.
# Deliberately NOT the mission's hazard boundary and NOT a scoring saturation
# point. Those are different physical quantities that happened to share this
# name, which is why the codebase held three different numbers (20 deg, 30 deg,
# and an untested one) for what looked like one parameter. They are now split:
#   this field                       -> mechanical capability (ramp test)
#   VerdictThresholds.hazard_slope   -> CLAUDE.md 1.4 verdict boundary
#   ScoringConfig.slope_penalty_saturation_rad -> evaluation tuning
# They are related by policy, not by derivation, so none is computed from
# another.
float32 max_climb_angle_rad

float32 min_passable_width_m     # widest footprint + clearance margin
float32 ground_clearance_m       # lowest chassis point to ground
bool has_grousers

# Where these numbers came from. MEASURED means our own CAD or scale; ASSUMED
# means a rover we do not possess, so every score derived from it is
# provisional. Consumers use this to decide what needs recomputing when the
# real medium-rover numbers arrive -- that is the whole point of keeping the
# observation and estimation layers as the canonical record.
uint8 provenance
uint8 PROVENANCE_UNKNOWN=0
uint8 PROVENANCE_MEASURED=1
uint8 PROVENANCE_ASSUMED=2

# Free text: which drawing, datasheet, or guess each number traces back to.
string provenance_note
