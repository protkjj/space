// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from space_msgs:msg/RoverSpec.idl
// generated code does not contain a copyright notice

#include "space_msgs/msg/detail/rover_spec__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_space_msgs
const rosidl_type_hash_t *
space_msgs__msg__RoverSpec__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x0b, 0x96, 0x15, 0x81, 0xdf, 0xba, 0xe5, 0xca,
      0xc7, 0x18, 0xca, 0x96, 0x9c, 0x4e, 0xb7, 0x9a,
      0x2b, 0x73, 0xaa, 0xc4, 0x65, 0x97, 0xde, 0xd8,
      0xeb, 0xb6, 0x18, 0xeb, 0xa8, 0xc0, 0x20, 0x30,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char space_msgs__msg__RoverSpec__TYPE_NAME[] = "space_msgs/msg/RoverSpec";

// Define type names, field names, and default values
static char space_msgs__msg__RoverSpec__FIELD_NAME__rover_id[] = "rover_id";
static char space_msgs__msg__RoverSpec__FIELD_NAME__mass_kg[] = "mass_kg";
static char space_msgs__msg__RoverSpec__FIELD_NAME__wheel_radius_m[] = "wheel_radius_m";
static char space_msgs__msg__RoverSpec__FIELD_NAME__wheel_width_m[] = "wheel_width_m";
static char space_msgs__msg__RoverSpec__FIELD_NAME__ground_pressure_kpa[] = "ground_pressure_kpa";
static char space_msgs__msg__RoverSpec__FIELD_NAME__max_climb_angle_rad[] = "max_climb_angle_rad";
static char space_msgs__msg__RoverSpec__FIELD_NAME__min_passable_width_m[] = "min_passable_width_m";
static char space_msgs__msg__RoverSpec__FIELD_NAME__ground_clearance_m[] = "ground_clearance_m";
static char space_msgs__msg__RoverSpec__FIELD_NAME__has_grousers[] = "has_grousers";
static char space_msgs__msg__RoverSpec__FIELD_NAME__provenance[] = "provenance";
static char space_msgs__msg__RoverSpec__FIELD_NAME__provenance_note[] = "provenance_note";

static rosidl_runtime_c__type_description__Field space_msgs__msg__RoverSpec__FIELDS[] = {
  {
    {space_msgs__msg__RoverSpec__FIELD_NAME__rover_id, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {space_msgs__msg__RoverSpec__FIELD_NAME__mass_kg, 7, 7},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {space_msgs__msg__RoverSpec__FIELD_NAME__wheel_radius_m, 14, 14},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {space_msgs__msg__RoverSpec__FIELD_NAME__wheel_width_m, 13, 13},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {space_msgs__msg__RoverSpec__FIELD_NAME__ground_pressure_kpa, 19, 19},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {space_msgs__msg__RoverSpec__FIELD_NAME__max_climb_angle_rad, 19, 19},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {space_msgs__msg__RoverSpec__FIELD_NAME__min_passable_width_m, 20, 20},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {space_msgs__msg__RoverSpec__FIELD_NAME__ground_clearance_m, 18, 18},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {space_msgs__msg__RoverSpec__FIELD_NAME__has_grousers, 12, 12},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_BOOLEAN,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {space_msgs__msg__RoverSpec__FIELD_NAME__provenance, 10, 10},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_UINT8,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {space_msgs__msg__RoverSpec__FIELD_NAME__provenance_note, 15, 15},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
space_msgs__msg__RoverSpec__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {space_msgs__msg__RoverSpec__TYPE_NAME, 24, 24},
      {space_msgs__msg__RoverSpec__FIELDS, 11, 11},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "# Physical specification of ONE rover -- the evaluation layer's only\n"
  "# rover-dependent input (CLAUDE.md: dual-rover transform layer).\n"
  "#\n"
  "# This type exists because rover limits kept leaking into \"tuning\" configs.\n"
  "# space_perception's TraversabilityConfig carried step_max = 0.056 m, which\n"
  "# docs/traversability.md records as \"half the current 0.112 m wheel radius\" --\n"
  "# a rover property disguised as a threshold. When the CAD import changed the\n"
  "# wheel to 0.070 m, that value silently became 1.6x too permissive. Rover\n"
  "# limits belong here and are derived, never hand-copied.\n"
  "#\n"
  "# Embedded in TraversabilityScore so a derived map always travels with the\n"
  "# assumptions it was computed under.\n"
  "\n"
  "string rover_id                  # 'small' | 'medium' | ...\n"
  "\n"
  "float32 mass_kg\n"
  "float32 wheel_radius_m\n"
  "float32 wheel_width_m\n"
  "float32 ground_pressure_kpa      # static, mass / total contact patch\n"
  "\n"
  "# MECHANICAL limit only: the steepest grade this vehicle can physically climb.\n"
  "# Deliberately NOT the mission's hazard boundary and NOT a scoring saturation\n"
  "# point. Those are different physical quantities that happened to share this\n"
  "# name, which is why the codebase held three different numbers (20 deg, 30 deg,\n"
  "# and an untested one) for what looked like one parameter. They are now split:\n"
  "#   this field                       -> mechanical capability (ramp test)\n"
  "#   VerdictThresholds.hazard_slope   -> CLAUDE.md 1.4 verdict boundary\n"
  "#   ScoringConfig.slope_penalty_saturation_rad -> evaluation tuning\n"
  "# They are related by policy, not by derivation, so none is computed from\n"
  "# another.\n"
  "float32 max_climb_angle_rad\n"
  "\n"
  "float32 min_passable_width_m     # widest footprint + clearance margin\n"
  "float32 ground_clearance_m       # lowest chassis point to ground\n"
  "bool has_grousers\n"
  "\n"
  "# Where these numbers came from. MEASURED means our own CAD or scale; ASSUMED\n"
  "# means a rover we do not possess, so every score derived from it is\n"
  "# provisional. Consumers use this to decide what needs recomputing when the\n"
  "# real medium-rover numbers arrive -- that is the whole point of keeping the\n"
  "# observation and estimation layers as the canonical record.\n"
  "uint8 provenance\n"
  "uint8 PROVENANCE_UNKNOWN=0\n"
  "uint8 PROVENANCE_MEASURED=1\n"
  "uint8 PROVENANCE_ASSUMED=2\n"
  "\n"
  "# Free text: which drawing, datasheet, or guess each number traces back to.\n"
  "string provenance_note";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
space_msgs__msg__RoverSpec__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {space_msgs__msg__RoverSpec__TYPE_NAME, 24, 24},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 2319, 2319},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
space_msgs__msg__RoverSpec__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *space_msgs__msg__RoverSpec__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
