// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from space_msgs:msg/RoverSpec.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "space_msgs/msg/rover_spec.h"


#ifndef SPACE_MSGS__MSG__DETAIL__ROVER_SPEC__STRUCT_H_
#define SPACE_MSGS__MSG__DETAIL__ROVER_SPEC__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Constants defined in the message

/// Constant 'PROVENANCE_UNKNOWN'.
enum
{
  space_msgs__msg__RoverSpec__PROVENANCE_UNKNOWN = 0
};

/// Constant 'PROVENANCE_MEASURED'.
enum
{
  space_msgs__msg__RoverSpec__PROVENANCE_MEASURED = 1
};

/// Constant 'PROVENANCE_ASSUMED'.
enum
{
  space_msgs__msg__RoverSpec__PROVENANCE_ASSUMED = 2
};

// Include directives for member types
// Member 'rover_id'
// Member 'provenance_note'
#include "rosidl_runtime_c/string.h"

/// Struct defined in msg/RoverSpec in the package space_msgs.
/**
  * Physical specification of ONE rover -- the evaluation layer's only
  * rover-dependent input (CLAUDE.md: dual-rover transform layer).
  *
  * This type exists because rover limits kept leaking into "tuning" configs.
  * space_perception's TraversabilityConfig carried step_max = 0.056 m, which
  * docs/traversability.md records as "half the current 0.112 m wheel radius" --
  * a rover property disguised as a threshold. When the CAD import changed the
  * wheel to 0.070 m, that value silently became 1.6x too permissive. Rover
  * limits belong here and are derived, never hand-copied.
  *
  * Embedded in TraversabilityScore so a derived map always travels with the
  * assumptions it was computed under.
 */
typedef struct space_msgs__msg__RoverSpec
{
  /// 'small' | 'medium' | ...
  rosidl_runtime_c__String rover_id;
  float mass_kg;
  float wheel_radius_m;
  float wheel_width_m;
  /// static, mass / total contact patch
  float ground_pressure_kpa;
  /// MECHANICAL limit only: the steepest grade this vehicle can physically climb.
  /// Deliberately NOT the mission's hazard boundary and NOT a scoring saturation
  /// point. Those are different physical quantities that happened to share this
  /// name, which is why the codebase held three different numbers (20 deg, 30 deg,
  /// and an untested one) for what looked like one parameter. They are now split:
  ///   this field                       -> mechanical capability (ramp test)
  ///   VerdictThresholds.hazard_slope   -> CLAUDE.md 1.4 verdict boundary
  ///   ScoringConfig.slope_penalty_saturation_rad -> evaluation tuning
  /// They are related by policy, not by derivation, so none is computed from
  /// another.
  float max_climb_angle_rad;
  /// widest footprint + clearance margin
  float min_passable_width_m;
  /// lowest chassis point to ground
  float ground_clearance_m;
  bool has_grousers;
  /// Where these numbers came from. MEASURED means our own CAD or scale; ASSUMED
  /// means a rover we do not possess, so every score derived from it is
  /// provisional. Consumers use this to decide what needs recomputing when the
  /// real medium-rover numbers arrive -- that is the whole point of keeping the
  /// observation and estimation layers as the canonical record.
  uint8_t provenance;
  /// Free text: which drawing, datasheet, or guess each number traces back to.
  rosidl_runtime_c__String provenance_note;
} space_msgs__msg__RoverSpec;

// Struct for a sequence of space_msgs__msg__RoverSpec.
typedef struct space_msgs__msg__RoverSpec__Sequence
{
  space_msgs__msg__RoverSpec * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} space_msgs__msg__RoverSpec__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SPACE_MSGS__MSG__DETAIL__ROVER_SPEC__STRUCT_H_
