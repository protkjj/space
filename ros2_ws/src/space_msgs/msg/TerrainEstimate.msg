# The CANONICAL terrain record: observation layer + estimation layer.
#
# CLAUDE.md's dual-rover transform layer makes this the thing we store and
# transfer. S_small and S_medium are DERIVED from it by substituting a
# RoverSpec, so they are never the record of truth. When the real medium-rover
# specification arrives, this message is replayed and only the score is
# recomputed -- no re-survey.
#
# Nothing rover-specific may be added here. Slip is the one apparent
# exception: lambda is a terrain x rover interaction, not a terrain constant,
# so it is named LAYER_SLIP_SMALL to keep that explicit. It is an OBSERVATION
# made by our small rover, never a property the medium rover would reproduce.

std_msgs/Header header

# Multi-layer grid. Layer names are contractual -- look layers up by the
# constants below, never by index, because layer order is not guaranteed.
grid_map_msgs/GridMap grid

# --- Observation layer: terrain-intrinsic geometry -------------------------
string LAYER_SLOPE=slope_rad
string LAYER_ROUGHNESS=roughness_m
string LAYER_STEP=step_height_m

# --- Observation layer: what our small rover actually felt ----------------
string LAYER_SLIP_SMALL=slip_small
string LAYER_SLIP_QUALITY=slip_quality

# Number of independent lambda measurements accumulated in each cell. A cell
# crossed once and a cell crossed three times must be distinguishable, so that
# confidence rises as field data accumulates instead of being a fixed guess.
string LAYER_SLIP_SAMPLES=slip_samples

# --- Estimation layer: soil proxy ----------------------------------------
# A RANK, not a measurement. See soil_model_id below.
string LAYER_SOIL_DIFFICULTY=soil_difficulty
string LAYER_SOIL_CONFIDENCE=soil_confidence

# Unobserved cells carry NaN in every layer. Consumers must treat NaN as
# "no data", distinct from a measured zero.

# --- Estimation provenance ------------------------------------------------
# Which soil proxy produced the estimation layers. The first implementation is
# a deliberate placeholder (CLAUDE.md 4: no terramechanics before field data),
# so its output is only meaningful for RANKING cells against each other, never
# as an absolute soil property. Recording the model identity here is what lets
# a later, calibrated model be swapped in and old records re-derived.
string soil_model_id
string soil_model_version
