// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from space_msgs:msg/TraversabilityScore.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "space_msgs/msg/traversability_score.h"


#ifndef SPACE_MSGS__MSG__DETAIL__TRAVERSABILITY_SCORE__STRUCT_H_
#define SPACE_MSGS__MSG__DETAIL__TRAVERSABILITY_SCORE__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Constants defined in the message

/// Constant 'LAYER_SCORE'.
/**
  * Traversability score, higher is better. NaN where the terrain record had no
  * data or the observation-quality gate rejected the cell.
 */
static const char * const space_msgs__msg__TraversabilityScore__LAYER_SCORE = "score";

/// Constant 'LAYER_LIMITING_FACTOR'.
/**
  * Which term dominated the score, so a low value is explainable rather than an
  * opaque number. Values are LIMIT_* below.
 */
static const char * const space_msgs__msg__TraversabilityScore__LAYER_LIMITING_FACTOR = "limiting_factor";

/// Constant 'LIMIT_NONE'.
enum
{
  space_msgs__msg__TraversabilityScore__LIMIT_NONE = 0
};

/// Constant 'LIMIT_SLOPE'.
enum
{
  space_msgs__msg__TraversabilityScore__LIMIT_SLOPE = 1
};

/// Constant 'LIMIT_ROUGHNESS'.
enum
{
  space_msgs__msg__TraversabilityScore__LIMIT_ROUGHNESS = 2
};

/// Constant 'LIMIT_STEP'.
enum
{
  space_msgs__msg__TraversabilityScore__LIMIT_STEP = 3
};

/// Constant 'LIMIT_SOIL'.
enum
{
  space_msgs__msg__TraversabilityScore__LIMIT_SOIL = 4
};

/// Constant 'LIMIT_CLEARANCE'.
enum
{
  space_msgs__msg__TraversabilityScore__LIMIT_CLEARANCE = 5
};

/// Constant 'LIMIT_WIDTH'.
enum
{
  space_msgs__msg__TraversabilityScore__LIMIT_WIDTH = 6
};

/// Constant 'LIMIT_NO_DATA'.
enum
{
  space_msgs__msg__TraversabilityScore__LIMIT_NO_DATA = 7
};

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.h"
// Member 'rover_id'
// Member 'soil_model_id'
// Member 'soil_model_version'
// Member 'evaluator_version'
#include "rosidl_runtime_c/string.h"
// Member 'rover_spec'
#include "space_msgs/msg/detail/rover_spec__struct.h"
// Member 'grid'
#include "grid_map_msgs/msg/detail/grid_map__struct.h"
// Member 'terrain_stamp'
#include "builtin_interfaces/msg/detail/time__struct.h"

/// Struct defined in msg/TraversabilityScore in the package space_msgs.
/**
  * A DERIVED traversability map for one specific rover.
  *
  * Published on /traversability/small and /traversability/medium. Both come from
  * the same evaluate() call with a different RoverSpec -- never from scaling one
  * into the other. CLAUDE.md is explicit that lambda is a terrain x rover
  * interaction: the same sand that slips our 3 kg rover 15% will slip a medium
  * rover differently because contact pressure, wheel diameter, mass, and grouser
  * shape all differ. Scaling S_small into S_medium is physically wrong.
 */
typedef struct space_msgs__msg__TraversabilityScore
{
  std_msgs__msg__Header header;
  rosidl_runtime_c__String rover_id;
  /// The exact specification this score was computed under, carried inline rather
  /// than referenced. If rover_spec.provenance is PROVENANCE_ASSUMED, every cell
  /// here is provisional and must be recomputed when real numbers land -- and this
  /// field is how you find out which maps those are.
  space_msgs__msg__RoverSpec rover_spec;
  /// Layers keyed by the constants below.
  grid_map_msgs__msg__GridMap grid;
  /// --- Provenance, so a recompute can be targeted instead of global ---------
  /// Stamp of the TerrainEstimate this was derived from.
  builtin_interfaces__msg__Time terrain_stamp;
  /// Copied from the source TerrainEstimate: a score is only as valid as the soil
  /// model behind it.
  rosidl_runtime_c__String soil_model_id;
  rosidl_runtime_c__String soil_model_version;
  /// Version of the evaluation function itself, separate from the soil model,
  /// because scoring weights and the soil proxy change independently.
  rosidl_runtime_c__String evaluator_version;
} space_msgs__msg__TraversabilityScore;

// Struct for a sequence of space_msgs__msg__TraversabilityScore.
typedef struct space_msgs__msg__TraversabilityScore__Sequence
{
  space_msgs__msg__TraversabilityScore * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} space_msgs__msg__TraversabilityScore__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SPACE_MSGS__MSG__DETAIL__TRAVERSABILITY_SCORE__STRUCT_H_
