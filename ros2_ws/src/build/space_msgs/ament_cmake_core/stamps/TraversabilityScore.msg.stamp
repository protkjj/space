# A DERIVED traversability map for one specific rover.
#
# Published on /traversability/small and /traversability/medium. Both come from
# the same evaluate() call with a different RoverSpec -- never from scaling one
# into the other. CLAUDE.md is explicit that lambda is a terrain x rover
# interaction: the same sand that slips our 3 kg rover 15% will slip a medium
# rover differently because contact pressure, wheel diameter, mass, and grouser
# shape all differ. Scaling S_small into S_medium is physically wrong.

std_msgs/Header header

string rover_id

# The exact specification this score was computed under, carried inline rather
# than referenced. If rover_spec.provenance is PROVENANCE_ASSUMED, every cell
# here is provisional and must be recomputed when real numbers land -- and this
# field is how you find out which maps those are.
RoverSpec rover_spec

# Layers keyed by the constants below.
grid_map_msgs/GridMap grid

# Traversability score, higher is better. NaN where the terrain record had no
# data or the observation-quality gate rejected the cell.
string LAYER_SCORE=score

# Which term dominated the score, so a low value is explainable rather than an
# opaque number. Values are LIMIT_* below.
string LAYER_LIMITING_FACTOR=limiting_factor

uint8 LIMIT_NONE=0
uint8 LIMIT_SLOPE=1
uint8 LIMIT_ROUGHNESS=2
uint8 LIMIT_STEP=3
uint8 LIMIT_SOIL=4
uint8 LIMIT_CLEARANCE=5
uint8 LIMIT_WIDTH=6
uint8 LIMIT_NO_DATA=7

# --- Provenance, so a recompute can be targeted instead of global ---------
# Stamp of the TerrainEstimate this was derived from.
builtin_interfaces/Time terrain_stamp

# Copied from the source TerrainEstimate: a score is only as valid as the soil
# model behind it.
string soil_model_id
string soil_model_version

# Version of the evaluation function itself, separate from the soil model,
# because scoring weights and the soil proxy change independently.
string evaluator_version
