// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from space_msgs:msg/SlipEstimate.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "space_msgs/msg/slip_estimate.h"


#ifndef SPACE_MSGS__MSG__DETAIL__SLIP_ESTIMATE__STRUCT_H_
#define SPACE_MSGS__MSG__DETAIL__SLIP_ESTIMATE__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Constants defined in the message

/// Constant 'SOURCE_UNKNOWN'.
enum
{
  space_msgs__msg__SlipEstimate__SOURCE_UNKNOWN = 0
};

/// Constant 'SOURCE_SIM_GROUND_TRUTH'.
enum
{
  space_msgs__msg__SlipEstimate__SOURCE_SIM_GROUND_TRUTH = 1
};

/// Constant 'SOURCE_VIO'.
enum
{
  space_msgs__msg__SlipEstimate__SOURCE_VIO = 2
};

/// Constant 'SOURCE_EKF'.
enum
{
  space_msgs__msg__SlipEstimate__SOURCE_EKF = 3
};

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.h"

/// Struct defined in msg/SlipEstimate in the package space_msgs.
/**
  * Wheel slip -- the rover's signature measurement (mission doc section 1.2).
  *
  *   lambda = (v_wheel - v_actual) / v_wheel
  *
  * Depth gives geometry only; it cannot tell a safe 15 deg slope from a sinking
  * one. Only the slip a rover actually experiences can. Treat this as a RELATIVE
  * indicator ("this patch slips more than that one"), never as a calibrated
  * absolute -- section 1.3 holds even with VIO error, but only relatively.
 */
typedef struct space_msgs__msg__SlipEstimate
{
  std_msgs__msg__Header header;
  /// lambda, dimensionless. Meaningless unless `valid` is true; publishers set it
  /// to NaN in that case so a consumer that ignores `valid` fails loudly.
  float slip_ratio;
  /// Encoder-implied forward speed, m/s. Contaminated by slip on purpose: a
  /// spinning wheel still reports motion. This is the numerator's inflated term.
  float v_wheel;
  /// Wheel-INDEPENDENT forward speed, m/s. Must not fuse wheel encoders, or the
  /// ratio becomes circular (section 1.3). See `source`.
  float v_actual;
  /// False -> discard slip_ratio entirely. Set when wheel speed is below the
  /// estimator's floor (a stationary rover has no defined slip) or when an input
  /// is stale. Independent of `quality`: this is "was lambda computable at all".
  bool valid;
  /// Confidence in v_actual, 0.0 (useless) .. 1.0 (fully trusted). Derived from
  /// the actual-velocity source's covariance, overridden by a VIO status topic
  /// when one is available. Independent of `valid`: a low-quality reading is
  /// still usable for the relative comparison of section 1.3, so the CONSUMER
  /// picks the threshold rather than the estimator silently dropping data.
  float quality;
  /// Which producer supplied v_actual. Published so a consumer can enforce
  /// section 1.3 itself: SOURCE_EKF fuses wheel encoders, which makes the slip
  /// ratio circular. That failure is invisible at runtime -- the arithmetic still
  /// succeeds and the value still looks plausible -- so it has to be typed.
  uint8_t source;
} space_msgs__msg__SlipEstimate;

// Struct for a sequence of space_msgs__msg__SlipEstimate.
typedef struct space_msgs__msg__SlipEstimate__Sequence
{
  space_msgs__msg__SlipEstimate * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} space_msgs__msg__SlipEstimate__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SPACE_MSGS__MSG__DETAIL__SLIP_ESTIMATE__STRUCT_H_
