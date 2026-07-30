// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from space_msgs:msg/TerrainEstimate.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "space_msgs/msg/terrain_estimate.h"


#ifndef SPACE_MSGS__MSG__DETAIL__TERRAIN_ESTIMATE__STRUCT_H_
#define SPACE_MSGS__MSG__DETAIL__TERRAIN_ESTIMATE__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Constants defined in the message

/// Constant 'LAYER_SLOPE'.
/**
  * --- Observation layer: terrain-intrinsic geometry -------------------------
 */
static const char * const space_msgs__msg__TerrainEstimate__LAYER_SLOPE = "slope_rad";

/// Constant 'LAYER_ROUGHNESS'.
static const char * const space_msgs__msg__TerrainEstimate__LAYER_ROUGHNESS = "roughness_m";

/// Constant 'LAYER_STEP'.
static const char * const space_msgs__msg__TerrainEstimate__LAYER_STEP = "step_height_m";

/// Constant 'LAYER_SLIP_SMALL'.
/**
  * --- Observation layer: what our small rover actually felt ----------------
 */
static const char * const space_msgs__msg__TerrainEstimate__LAYER_SLIP_SMALL = "slip_small";

/// Constant 'LAYER_SLIP_QUALITY'.
static const char * const space_msgs__msg__TerrainEstimate__LAYER_SLIP_QUALITY = "slip_quality";

/// Constant 'LAYER_SLIP_SAMPLES'.
/**
  * Number of independent lambda measurements accumulated in each cell. A cell
  * crossed once and a cell crossed three times must be distinguishable, so that
  * confidence rises as field data accumulates instead of being a fixed guess.
 */
static const char * const space_msgs__msg__TerrainEstimate__LAYER_SLIP_SAMPLES = "slip_samples";

/// Constant 'LAYER_SOIL_DIFFICULTY'.
/**
  * --- Estimation layer: soil proxy ----------------------------------------
  * A RANK, not a measurement. See soil_model_id below.
 */
static const char * const space_msgs__msg__TerrainEstimate__LAYER_SOIL_DIFFICULTY = "soil_difficulty";

/// Constant 'LAYER_SOIL_CONFIDENCE'.
static const char * const space_msgs__msg__TerrainEstimate__LAYER_SOIL_CONFIDENCE = "soil_confidence";

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.h"
// Member 'grid'
#include "grid_map_msgs/msg/detail/grid_map__struct.h"
// Member 'soil_model_id'
// Member 'soil_model_version'
#include "rosidl_runtime_c/string.h"

/// Struct defined in msg/TerrainEstimate in the package space_msgs.
/**
  * The CANONICAL terrain record: observation layer + estimation layer.
  *
  * CLAUDE.md's dual-rover transform layer makes this the thing we store and
  * transfer. S_small and S_medium are DERIVED from it by substituting a
  * RoverSpec, so they are never the record of truth. When the real medium-rover
  * specification arrives, this message is replayed and only the score is
  * recomputed -- no re-survey.
  *
  * Nothing rover-specific may be added here. Slip is the one apparent
  * exception: lambda is a terrain x rover interaction, not a terrain constant,
  * so it is named LAYER_SLIP_SMALL to keep that explicit. It is an OBSERVATION
  * made by our small rover, never a property the medium rover would reproduce.
 */
typedef struct space_msgs__msg__TerrainEstimate
{
  std_msgs__msg__Header header;
  /// Multi-layer grid. Layer names are contractual -- look layers up by the
  /// constants below, never by index, because layer order is not guaranteed.
  grid_map_msgs__msg__GridMap grid;
  /// Unobserved cells carry NaN in every layer. Consumers must treat NaN as
  /// "no data", distinct from a measured zero.
  /// --- Estimation provenance ------------------------------------------------
  /// Which soil proxy produced the estimation layers. The first implementation is
  /// a deliberate placeholder (CLAUDE.md 4: no terramechanics before field data),
  /// so its output is only meaningful for RANKING cells against each other, never
  /// as an absolute soil property. Recording the model identity here is what lets
  /// a later, calibrated model be swapped in and old records re-derived.
  rosidl_runtime_c__String soil_model_id;
  rosidl_runtime_c__String soil_model_version;
} space_msgs__msg__TerrainEstimate;

// Struct for a sequence of space_msgs__msg__TerrainEstimate.
typedef struct space_msgs__msg__TerrainEstimate__Sequence
{
  space_msgs__msg__TerrainEstimate * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} space_msgs__msg__TerrainEstimate__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SPACE_MSGS__MSG__DETAIL__TERRAIN_ESTIMATE__STRUCT_H_
