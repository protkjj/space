// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from space_msgs:msg/SlipEstimate.idl
// generated code does not contain a copyright notice

#include "space_msgs/msg/detail/slip_estimate__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_space_msgs
const rosidl_type_hash_t *
space_msgs__msg__SlipEstimate__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x9b, 0xa3, 0x30, 0xc7, 0xe1, 0x33, 0xc9, 0x49,
      0x26, 0xfc, 0xa8, 0x72, 0x10, 0x89, 0x2b, 0x11,
      0xd5, 0x46, 0x02, 0x28, 0xd4, 0xcf, 0x2b, 0xd3,
      0x15, 0x5a, 0x01, 0xba, 0x13, 0xd5, 0x72, 0x6b,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types
#include "builtin_interfaces/msg/detail/time__functions.h"
#include "std_msgs/msg/detail/header__functions.h"

// Hashes for external referenced types
#ifndef NDEBUG
static const rosidl_type_hash_t builtin_interfaces__msg__Time__EXPECTED_HASH = {1, {
    0xb1, 0x06, 0x23, 0x5e, 0x25, 0xa4, 0xc5, 0xed,
    0x35, 0x09, 0x8a, 0xa0, 0xa6, 0x1a, 0x3e, 0xe9,
    0xc9, 0xb1, 0x8d, 0x19, 0x7f, 0x39, 0x8b, 0x0e,
    0x42, 0x06, 0xce, 0xa9, 0xac, 0xf9, 0xc1, 0x97,
  }};
static const rosidl_type_hash_t std_msgs__msg__Header__EXPECTED_HASH = {1, {
    0xf4, 0x9f, 0xb3, 0xae, 0x2c, 0xf0, 0x70, 0xf7,
    0x93, 0x64, 0x5f, 0xf7, 0x49, 0x68, 0x3a, 0xc6,
    0xb0, 0x62, 0x03, 0xe4, 0x1c, 0x89, 0x1e, 0x17,
    0x70, 0x1b, 0x1c, 0xb5, 0x97, 0xce, 0x6a, 0x01,
  }};
#endif

static char space_msgs__msg__SlipEstimate__TYPE_NAME[] = "space_msgs/msg/SlipEstimate";
static char builtin_interfaces__msg__Time__TYPE_NAME[] = "builtin_interfaces/msg/Time";
static char std_msgs__msg__Header__TYPE_NAME[] = "std_msgs/msg/Header";

// Define type names, field names, and default values
static char space_msgs__msg__SlipEstimate__FIELD_NAME__header[] = "header";
static char space_msgs__msg__SlipEstimate__FIELD_NAME__slip_ratio[] = "slip_ratio";
static char space_msgs__msg__SlipEstimate__FIELD_NAME__v_wheel[] = "v_wheel";
static char space_msgs__msg__SlipEstimate__FIELD_NAME__v_actual[] = "v_actual";
static char space_msgs__msg__SlipEstimate__FIELD_NAME__valid[] = "valid";
static char space_msgs__msg__SlipEstimate__FIELD_NAME__quality[] = "quality";
static char space_msgs__msg__SlipEstimate__FIELD_NAME__source[] = "source";

static rosidl_runtime_c__type_description__Field space_msgs__msg__SlipEstimate__FIELDS[] = {
  {
    {space_msgs__msg__SlipEstimate__FIELD_NAME__header, 6, 6},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {std_msgs__msg__Header__TYPE_NAME, 19, 19},
    },
    {NULL, 0, 0},
  },
  {
    {space_msgs__msg__SlipEstimate__FIELD_NAME__slip_ratio, 10, 10},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {space_msgs__msg__SlipEstimate__FIELD_NAME__v_wheel, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {space_msgs__msg__SlipEstimate__FIELD_NAME__v_actual, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {space_msgs__msg__SlipEstimate__FIELD_NAME__valid, 5, 5},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_BOOLEAN,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {space_msgs__msg__SlipEstimate__FIELD_NAME__quality, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {space_msgs__msg__SlipEstimate__FIELD_NAME__source, 6, 6},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

static rosidl_runtime_c__type_description__IndividualTypeDescription space_msgs__msg__SlipEstimate__REFERENCED_TYPE_DESCRIPTIONS[] = {
  {
    {builtin_interfaces__msg__Time__TYPE_NAME, 27, 27},
    {NULL, 0, 0},
  },
  {
    {std_msgs__msg__Header__TYPE_NAME, 19, 19},
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
space_msgs__msg__SlipEstimate__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {space_msgs__msg__SlipEstimate__TYPE_NAME, 27, 27},
      {space_msgs__msg__SlipEstimate__FIELDS, 7, 7},
    },
    {space_msgs__msg__SlipEstimate__REFERENCED_TYPE_DESCRIPTIONS, 2, 2},
  };
  if (!constructed) {
    assert(0 == memcmp(&builtin_interfaces__msg__Time__EXPECTED_HASH, builtin_interfaces__msg__Time__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[0].fields = builtin_interfaces__msg__Time__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&std_msgs__msg__Header__EXPECTED_HASH, std_msgs__msg__Header__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[1].fields = std_msgs__msg__Header__get_type_description(NULL)->type_description.fields;
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "# Wheel slip -- the rover's signature measurement (mission doc section 1.2).\n"
  "#\n"
  "#   lambda = (v_wheel - v_actual) / v_wheel\n"
  "#\n"
  "# Depth gives geometry only; it cannot tell a safe 15 deg slope from a sinking\n"
  "# one. Only the slip a rover actually experiences can. Treat this as a RELATIVE\n"
  "# indicator (\"this patch slips more than that one\"), never as a calibrated\n"
  "# absolute -- section 1.3 holds even with VIO error, but only relatively.\n"
  "\n"
  "std_msgs/Header header\n"
  "\n"
  "# lambda, dimensionless. Meaningless unless `valid` is true; publishers set it\n"
  "# to NaN in that case so a consumer that ignores `valid` fails loudly.\n"
  "float32 slip_ratio\n"
  "\n"
  "# Encoder-implied forward speed, m/s. Contaminated by slip on purpose: a\n"
  "# spinning wheel still reports motion. This is the numerator's inflated term.\n"
  "float32 v_wheel\n"
  "\n"
  "# Wheel-INDEPENDENT forward speed, m/s. Must not fuse wheel encoders, or the\n"
  "# ratio becomes circular (section 1.3). See `source`.\n"
  "float32 v_actual\n"
  "\n"
  "# False -> discard slip_ratio entirely. Set when wheel speed is below the\n"
  "# estimator's floor (a stationary rover has no defined slip) or when an input\n"
  "# is stale. Independent of `quality`: this is \"was lambda computable at all\".\n"
  "bool valid\n"
  "\n"
  "# Confidence in v_actual, 0.0 (useless) .. 1.0 (fully trusted). Derived from\n"
  "# the actual-velocity source's covariance, overridden by a VIO status topic\n"
  "# when one is available. Independent of `valid`: a low-quality reading is\n"
  "# still usable for the relative comparison of section 1.3, so the CONSUMER\n"
  "# picks the threshold rather than the estimator silently dropping data.\n"
  "float32 quality\n"
  "\n"
  "# Which producer supplied v_actual. Published so a consumer can enforce\n"
  "# section 1.3 itself: SOURCE_EKF fuses wheel encoders, which makes the slip\n"
  "# ratio circular. That failure is invisible at runtime -- the arithmetic still\n"
  "# succeeds and the value still looks plausible -- so it has to be typed.\n"
  "uint8 source\n"
  "\n"
  "uint8 SOURCE_UNKNOWN=0\n"
  "uint8 SOURCE_SIM_GROUND_TRUTH=1\n"
  "uint8 SOURCE_VIO=2\n"
  "uint8 SOURCE_EKF=3";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
space_msgs__msg__SlipEstimate__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {space_msgs__msg__SlipEstimate__TYPE_NAME, 27, 27},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 1985, 1985},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
space_msgs__msg__SlipEstimate__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[3];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 3, 3};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *space_msgs__msg__SlipEstimate__get_individual_type_description_source(NULL),
    sources[1] = *builtin_interfaces__msg__Time__get_individual_type_description_source(NULL);
    sources[2] = *std_msgs__msg__Header__get_individual_type_description_source(NULL);
    constructed = true;
  }
  return &source_sequence;
}
