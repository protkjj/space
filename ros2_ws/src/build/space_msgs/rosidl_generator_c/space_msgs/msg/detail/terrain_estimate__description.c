// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from space_msgs:msg/TerrainEstimate.idl
// generated code does not contain a copyright notice

#include "space_msgs/msg/detail/terrain_estimate__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_space_msgs
const rosidl_type_hash_t *
space_msgs__msg__TerrainEstimate__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0xe9, 0xfe, 0x9f, 0x5e, 0xfd, 0xc4, 0xa1, 0x16,
      0xfd, 0xd5, 0x1d, 0xff, 0x3b, 0x54, 0xf3, 0x2d,
      0xe0, 0x53, 0x92, 0x27, 0xe1, 0xb2, 0x52, 0x85,
      0x3c, 0xa6, 0xf4, 0x0c, 0x13, 0x5d, 0x7c, 0xf2,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types
#include "std_msgs/msg/detail/multi_array_layout__functions.h"
#include "std_msgs/msg/detail/float32_multi_array__functions.h"
#include "geometry_msgs/msg/detail/point__functions.h"
#include "geometry_msgs/msg/detail/pose__functions.h"
#include "grid_map_msgs/msg/detail/grid_map__functions.h"
#include "std_msgs/msg/detail/multi_array_dimension__functions.h"
#include "std_msgs/msg/detail/header__functions.h"
#include "grid_map_msgs/msg/detail/grid_map_info__functions.h"
#include "geometry_msgs/msg/detail/quaternion__functions.h"
#include "builtin_interfaces/msg/detail/time__functions.h"

// Hashes for external referenced types
#ifndef NDEBUG
static const rosidl_type_hash_t builtin_interfaces__msg__Time__EXPECTED_HASH = {1, {
    0xb1, 0x06, 0x23, 0x5e, 0x25, 0xa4, 0xc5, 0xed,
    0x35, 0x09, 0x8a, 0xa0, 0xa6, 0x1a, 0x3e, 0xe9,
    0xc9, 0xb1, 0x8d, 0x19, 0x7f, 0x39, 0x8b, 0x0e,
    0x42, 0x06, 0xce, 0xa9, 0xac, 0xf9, 0xc1, 0x97,
  }};
static const rosidl_type_hash_t geometry_msgs__msg__Point__EXPECTED_HASH = {1, {
    0x69, 0x63, 0x08, 0x48, 0x42, 0xa9, 0xb0, 0x44,
    0x94, 0xd6, 0xb2, 0x94, 0x1d, 0x11, 0x44, 0x47,
    0x08, 0xd8, 0x92, 0xda, 0x2f, 0x4b, 0x09, 0x84,
    0x3b, 0x9c, 0x43, 0xf4, 0x2a, 0x7f, 0x68, 0x81,
  }};
static const rosidl_type_hash_t geometry_msgs__msg__Pose__EXPECTED_HASH = {1, {
    0xd5, 0x01, 0x95, 0x4e, 0x94, 0x76, 0xce, 0xa2,
    0x99, 0x69, 0x84, 0xe8, 0x12, 0x05, 0x4b, 0x68,
    0x02, 0x6a, 0xe0, 0xbf, 0xae, 0x78, 0x9d, 0x9a,
    0x10, 0xb2, 0x3d, 0xaf, 0x35, 0xcc, 0x90, 0xfa,
  }};
static const rosidl_type_hash_t geometry_msgs__msg__Quaternion__EXPECTED_HASH = {1, {
    0x8a, 0x76, 0x5f, 0x66, 0x77, 0x8c, 0x8f, 0xf7,
    0xc8, 0xab, 0x94, 0xaf, 0xcc, 0x59, 0x0a, 0x2e,
    0xd5, 0x32, 0x5a, 0x1d, 0x9a, 0x07, 0x6f, 0xff,
    0xf3, 0x8f, 0xbc, 0xe3, 0x6f, 0x45, 0x86, 0x84,
  }};
static const rosidl_type_hash_t grid_map_msgs__msg__GridMap__EXPECTED_HASH = {1, {
    0x34, 0x3b, 0x0e, 0x72, 0x88, 0x75, 0x41, 0xbe,
    0xda, 0x6b, 0x03, 0x5c, 0xc0, 0x53, 0xf2, 0xd6,
    0xff, 0xfa, 0xad, 0x9d, 0x6d, 0xcb, 0x27, 0x73,
    0xc1, 0x5a, 0x80, 0x8d, 0xfc, 0xa3, 0x1f, 0xde,
  }};
static const rosidl_type_hash_t grid_map_msgs__msg__GridMapInfo__EXPECTED_HASH = {1, {
    0x0a, 0x36, 0xd6, 0xb5, 0xbc, 0x9a, 0xf8, 0x46,
    0x3d, 0x1d, 0x5a, 0x50, 0x08, 0xef, 0x9f, 0xca,
    0xc0, 0xc1, 0x37, 0x3b, 0xa0, 0x90, 0xf8, 0x0c,
    0x35, 0x94, 0xe4, 0x7c, 0xc5, 0x65, 0xb7, 0x45,
  }};
static const rosidl_type_hash_t std_msgs__msg__Float32MultiArray__EXPECTED_HASH = {1, {
    0x05, 0x99, 0xf6, 0xf8, 0x5b, 0x4b, 0xfc, 0xa3,
    0x79, 0x87, 0x3a, 0x0b, 0x43, 0x75, 0xa0, 0xac,
    0xa0, 0x22, 0x15, 0x6b, 0xd2, 0xd7, 0x02, 0x12,
    0x75, 0xd1, 0x16, 0xed, 0x1f, 0xa8, 0xbf, 0xe0,
  }};
static const rosidl_type_hash_t std_msgs__msg__Header__EXPECTED_HASH = {1, {
    0xf4, 0x9f, 0xb3, 0xae, 0x2c, 0xf0, 0x70, 0xf7,
    0x93, 0x64, 0x5f, 0xf7, 0x49, 0x68, 0x3a, 0xc6,
    0xb0, 0x62, 0x03, 0xe4, 0x1c, 0x89, 0x1e, 0x17,
    0x70, 0x1b, 0x1c, 0xb5, 0x97, 0xce, 0x6a, 0x01,
  }};
static const rosidl_type_hash_t std_msgs__msg__MultiArrayDimension__EXPECTED_HASH = {1, {
    0x5e, 0x77, 0x3a, 0x60, 0xa4, 0xc7, 0xfc, 0x8a,
    0x54, 0x98, 0x5f, 0x30, 0x7c, 0x78, 0x37, 0xaa,
    0x29, 0x94, 0x25, 0x2a, 0x12, 0x6c, 0x30, 0x19,
    0x57, 0xa2, 0x4e, 0x31, 0x28, 0x2c, 0x9c, 0xbe,
  }};
static const rosidl_type_hash_t std_msgs__msg__MultiArrayLayout__EXPECTED_HASH = {1, {
    0x4c, 0x66, 0xe6, 0xf7, 0x8e, 0x74, 0x0a, 0xc1,
    0x03, 0xa9, 0x4c, 0xf6, 0x32, 0x59, 0xf9, 0x68,
    0xe4, 0x8c, 0x61, 0x7e, 0x76, 0x99, 0xe8, 0x29,
    0xb6, 0x3c, 0x21, 0xa5, 0xcb, 0x50, 0xda, 0xc6,
  }};
#endif

static char space_msgs__msg__TerrainEstimate__TYPE_NAME[] = "space_msgs/msg/TerrainEstimate";
static char builtin_interfaces__msg__Time__TYPE_NAME[] = "builtin_interfaces/msg/Time";
static char geometry_msgs__msg__Point__TYPE_NAME[] = "geometry_msgs/msg/Point";
static char geometry_msgs__msg__Pose__TYPE_NAME[] = "geometry_msgs/msg/Pose";
static char geometry_msgs__msg__Quaternion__TYPE_NAME[] = "geometry_msgs/msg/Quaternion";
static char grid_map_msgs__msg__GridMap__TYPE_NAME[] = "grid_map_msgs/msg/GridMap";
static char grid_map_msgs__msg__GridMapInfo__TYPE_NAME[] = "grid_map_msgs/msg/GridMapInfo";
static char std_msgs__msg__Float32MultiArray__TYPE_NAME[] = "std_msgs/msg/Float32MultiArray";
static char std_msgs__msg__Header__TYPE_NAME[] = "std_msgs/msg/Header";
static char std_msgs__msg__MultiArrayDimension__TYPE_NAME[] = "std_msgs/msg/MultiArrayDimension";
static char std_msgs__msg__MultiArrayLayout__TYPE_NAME[] = "std_msgs/msg/MultiArrayLayout";

// Define type names, field names, and default values
static char space_msgs__msg__TerrainEstimate__FIELD_NAME__header[] = "header";
static char space_msgs__msg__TerrainEstimate__FIELD_NAME__grid[] = "grid";
static char space_msgs__msg__TerrainEstimate__FIELD_NAME__soil_model_id[] = "soil_model_id";
static char space_msgs__msg__TerrainEstimate__FIELD_NAME__soil_model_version[] = "soil_model_version";

static rosidl_runtime_c__type_description__Field space_msgs__msg__TerrainEstimate__FIELDS[] = {
  {
    {space_msgs__msg__TerrainEstimate__FIELD_NAME__header, 6, 6},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {std_msgs__msg__Header__TYPE_NAME, 19, 19},
    },
    {NULL, 0, 0},
  },
  {
    {space_msgs__msg__TerrainEstimate__FIELD_NAME__grid, 4, 4},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {grid_map_msgs__msg__GridMap__TYPE_NAME, 25, 25},
    },
    {NULL, 0, 0},
  },
  {
    {space_msgs__msg__TerrainEstimate__FIELD_NAME__soil_model_id, 13, 13},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {space_msgs__msg__TerrainEstimate__FIELD_NAME__soil_model_version, 18, 18},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_STRING,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

static rosidl_runtime_c__type_description__IndividualTypeDescription space_msgs__msg__TerrainEstimate__REFERENCED_TYPE_DESCRIPTIONS[] = {
  {
    {builtin_interfaces__msg__Time__TYPE_NAME, 27, 27},
    {NULL, 0, 0},
  },
  {
    {geometry_msgs__msg__Point__TYPE_NAME, 23, 23},
    {NULL, 0, 0},
  },
  {
    {geometry_msgs__msg__Pose__TYPE_NAME, 22, 22},
    {NULL, 0, 0},
  },
  {
    {geometry_msgs__msg__Quaternion__TYPE_NAME, 28, 28},
    {NULL, 0, 0},
  },
  {
    {grid_map_msgs__msg__GridMap__TYPE_NAME, 25, 25},
    {NULL, 0, 0},
  },
  {
    {grid_map_msgs__msg__GridMapInfo__TYPE_NAME, 29, 29},
    {NULL, 0, 0},
  },
  {
    {std_msgs__msg__Float32MultiArray__TYPE_NAME, 30, 30},
    {NULL, 0, 0},
  },
  {
    {std_msgs__msg__Header__TYPE_NAME, 19, 19},
    {NULL, 0, 0},
  },
  {
    {std_msgs__msg__MultiArrayDimension__TYPE_NAME, 32, 32},
    {NULL, 0, 0},
  },
  {
    {std_msgs__msg__MultiArrayLayout__TYPE_NAME, 29, 29},
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
space_msgs__msg__TerrainEstimate__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {space_msgs__msg__TerrainEstimate__TYPE_NAME, 30, 30},
      {space_msgs__msg__TerrainEstimate__FIELDS, 4, 4},
    },
    {space_msgs__msg__TerrainEstimate__REFERENCED_TYPE_DESCRIPTIONS, 10, 10},
  };
  if (!constructed) {
    assert(0 == memcmp(&builtin_interfaces__msg__Time__EXPECTED_HASH, builtin_interfaces__msg__Time__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[0].fields = builtin_interfaces__msg__Time__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&geometry_msgs__msg__Point__EXPECTED_HASH, geometry_msgs__msg__Point__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[1].fields = geometry_msgs__msg__Point__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&geometry_msgs__msg__Pose__EXPECTED_HASH, geometry_msgs__msg__Pose__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[2].fields = geometry_msgs__msg__Pose__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&geometry_msgs__msg__Quaternion__EXPECTED_HASH, geometry_msgs__msg__Quaternion__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[3].fields = geometry_msgs__msg__Quaternion__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&grid_map_msgs__msg__GridMap__EXPECTED_HASH, grid_map_msgs__msg__GridMap__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[4].fields = grid_map_msgs__msg__GridMap__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&grid_map_msgs__msg__GridMapInfo__EXPECTED_HASH, grid_map_msgs__msg__GridMapInfo__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[5].fields = grid_map_msgs__msg__GridMapInfo__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&std_msgs__msg__Float32MultiArray__EXPECTED_HASH, std_msgs__msg__Float32MultiArray__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[6].fields = std_msgs__msg__Float32MultiArray__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&std_msgs__msg__Header__EXPECTED_HASH, std_msgs__msg__Header__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[7].fields = std_msgs__msg__Header__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&std_msgs__msg__MultiArrayDimension__EXPECTED_HASH, std_msgs__msg__MultiArrayDimension__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[8].fields = std_msgs__msg__MultiArrayDimension__get_type_description(NULL)->type_description.fields;
    assert(0 == memcmp(&std_msgs__msg__MultiArrayLayout__EXPECTED_HASH, std_msgs__msg__MultiArrayLayout__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[9].fields = std_msgs__msg__MultiArrayLayout__get_type_description(NULL)->type_description.fields;
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "# The CANONICAL terrain record: observation layer + estimation layer.\n"
  "#\n"
  "# CLAUDE.md's dual-rover transform layer makes this the thing we store and\n"
  "# transfer. S_small and S_medium are DERIVED from it by substituting a\n"
  "# RoverSpec, so they are never the record of truth. When the real medium-rover\n"
  "# specification arrives, this message is replayed and only the score is\n"
  "# recomputed -- no re-survey.\n"
  "#\n"
  "# Nothing rover-specific may be added here. Slip is the one apparent\n"
  "# exception: lambda is a terrain x rover interaction, not a terrain constant,\n"
  "# so it is named LAYER_SLIP_SMALL to keep that explicit. It is an OBSERVATION\n"
  "# made by our small rover, never a property the medium rover would reproduce.\n"
  "\n"
  "std_msgs/Header header\n"
  "\n"
  "# Multi-layer grid. Layer names are contractual -- look layers up by the\n"
  "# constants below, never by index, because layer order is not guaranteed.\n"
  "grid_map_msgs/GridMap grid\n"
  "\n"
  "# --- Observation layer: terrain-intrinsic geometry -------------------------\n"
  "string LAYER_SLOPE=slope_rad\n"
  "string LAYER_ROUGHNESS=roughness_m\n"
  "string LAYER_STEP=step_height_m\n"
  "\n"
  "# --- Observation layer: what our small rover actually felt ----------------\n"
  "string LAYER_SLIP_SMALL=slip_small\n"
  "string LAYER_SLIP_QUALITY=slip_quality\n"
  "\n"
  "# Number of independent lambda measurements accumulated in each cell. A cell\n"
  "# crossed once and a cell crossed three times must be distinguishable, so that\n"
  "# confidence rises as field data accumulates instead of being a fixed guess.\n"
  "string LAYER_SLIP_SAMPLES=slip_samples\n"
  "\n"
  "# --- Estimation layer: soil proxy ----------------------------------------\n"
  "# A RANK, not a measurement. See soil_model_id below.\n"
  "string LAYER_SOIL_DIFFICULTY=soil_difficulty\n"
  "string LAYER_SOIL_CONFIDENCE=soil_confidence\n"
  "\n"
  "# Unobserved cells carry NaN in every layer. Consumers must treat NaN as\n"
  "# \"no data\", distinct from a measured zero.\n"
  "\n"
  "# --- Estimation provenance ------------------------------------------------\n"
  "# Which soil proxy produced the estimation layers. The first implementation is\n"
  "# a deliberate placeholder (CLAUDE.md 4: no terramechanics before field data),\n"
  "# so its output is only meaningful for RANKING cells against each other, never\n"
  "# as an absolute soil property. Recording the model identity here is what lets\n"
  "# a later, calibrated model be swapped in and old records re-derived.\n"
  "string soil_model_id\n"
  "string soil_model_version";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
space_msgs__msg__TerrainEstimate__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {space_msgs__msg__TerrainEstimate__TYPE_NAME, 30, 30},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 2353, 2353},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
space_msgs__msg__TerrainEstimate__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[11];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 11, 11};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *space_msgs__msg__TerrainEstimate__get_individual_type_description_source(NULL),
    sources[1] = *builtin_interfaces__msg__Time__get_individual_type_description_source(NULL);
    sources[2] = *geometry_msgs__msg__Point__get_individual_type_description_source(NULL);
    sources[3] = *geometry_msgs__msg__Pose__get_individual_type_description_source(NULL);
    sources[4] = *geometry_msgs__msg__Quaternion__get_individual_type_description_source(NULL);
    sources[5] = *grid_map_msgs__msg__GridMap__get_individual_type_description_source(NULL);
    sources[6] = *grid_map_msgs__msg__GridMapInfo__get_individual_type_description_source(NULL);
    sources[7] = *std_msgs__msg__Float32MultiArray__get_individual_type_description_source(NULL);
    sources[8] = *std_msgs__msg__Header__get_individual_type_description_source(NULL);
    sources[9] = *std_msgs__msg__MultiArrayDimension__get_individual_type_description_source(NULL);
    sources[10] = *std_msgs__msg__MultiArrayLayout__get_individual_type_description_source(NULL);
    constructed = true;
  }
  return &source_sequence;
}
