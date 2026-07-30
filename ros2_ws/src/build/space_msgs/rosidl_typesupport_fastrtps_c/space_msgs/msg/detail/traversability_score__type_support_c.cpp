// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from space_msgs:msg/TraversabilityScore.idl
// generated code does not contain a copyright notice
#include "space_msgs/msg/detail/traversability_score__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <cstddef>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/serialization_helpers.hpp"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "space_msgs/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "space_msgs/msg/detail/traversability_score__struct.h"
#include "space_msgs/msg/detail/traversability_score__functions.h"
#include "fastcdr/Cdr.h"

#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-parameter"
# ifdef __clang__
#  pragma clang diagnostic ignored "-Wdeprecated-register"
#  pragma clang diagnostic ignored "-Wreturn-type-c-linkage"
# endif
#endif
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif

// includes and forward declarations of message dependencies and their conversion functions

#if defined(__cplusplus)
extern "C"
{
#endif

#include "builtin_interfaces/msg/detail/time__functions.h"  // terrain_stamp
#include "grid_map_msgs/msg/detail/grid_map__functions.h"  // grid
#include "rosidl_runtime_c/string.h"  // evaluator_version, rover_id, soil_model_id, soil_model_version
#include "rosidl_runtime_c/string_functions.h"  // evaluator_version, rover_id, soil_model_id, soil_model_version
#include "space_msgs/msg/detail/rover_spec__functions.h"  // rover_spec
#include "std_msgs/msg/detail/header__functions.h"  // header

// forward declare type support functions

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_space_msgs
bool cdr_serialize_builtin_interfaces__msg__Time(
  const builtin_interfaces__msg__Time * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_space_msgs
bool cdr_deserialize_builtin_interfaces__msg__Time(
  eprosima::fastcdr::Cdr & cdr,
  builtin_interfaces__msg__Time * ros_message);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_space_msgs
size_t get_serialized_size_builtin_interfaces__msg__Time(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_space_msgs
size_t max_serialized_size_builtin_interfaces__msg__Time(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_space_msgs
bool cdr_serialize_key_builtin_interfaces__msg__Time(
  const builtin_interfaces__msg__Time * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_space_msgs
size_t get_serialized_size_key_builtin_interfaces__msg__Time(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_space_msgs
size_t max_serialized_size_key_builtin_interfaces__msg__Time(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_space_msgs
const rosidl_message_type_support_t *
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, builtin_interfaces, msg, Time)();

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_space_msgs
bool cdr_serialize_grid_map_msgs__msg__GridMap(
  const grid_map_msgs__msg__GridMap * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_space_msgs
bool cdr_deserialize_grid_map_msgs__msg__GridMap(
  eprosima::fastcdr::Cdr & cdr,
  grid_map_msgs__msg__GridMap * ros_message);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_space_msgs
size_t get_serialized_size_grid_map_msgs__msg__GridMap(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_space_msgs
size_t max_serialized_size_grid_map_msgs__msg__GridMap(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_space_msgs
bool cdr_serialize_key_grid_map_msgs__msg__GridMap(
  const grid_map_msgs__msg__GridMap * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_space_msgs
size_t get_serialized_size_key_grid_map_msgs__msg__GridMap(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_space_msgs
size_t max_serialized_size_key_grid_map_msgs__msg__GridMap(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_space_msgs
const rosidl_message_type_support_t *
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, grid_map_msgs, msg, GridMap)();

bool cdr_serialize_space_msgs__msg__RoverSpec(
  const space_msgs__msg__RoverSpec * ros_message,
  eprosima::fastcdr::Cdr & cdr);

bool cdr_deserialize_space_msgs__msg__RoverSpec(
  eprosima::fastcdr::Cdr & cdr,
  space_msgs__msg__RoverSpec * ros_message);

size_t get_serialized_size_space_msgs__msg__RoverSpec(
  const void * untyped_ros_message,
  size_t current_alignment);

size_t max_serialized_size_space_msgs__msg__RoverSpec(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

bool cdr_serialize_key_space_msgs__msg__RoverSpec(
  const space_msgs__msg__RoverSpec * ros_message,
  eprosima::fastcdr::Cdr & cdr);

size_t get_serialized_size_key_space_msgs__msg__RoverSpec(
  const void * untyped_ros_message,
  size_t current_alignment);

size_t max_serialized_size_key_space_msgs__msg__RoverSpec(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

const rosidl_message_type_support_t *
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, space_msgs, msg, RoverSpec)();

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_space_msgs
bool cdr_serialize_std_msgs__msg__Header(
  const std_msgs__msg__Header * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_space_msgs
bool cdr_deserialize_std_msgs__msg__Header(
  eprosima::fastcdr::Cdr & cdr,
  std_msgs__msg__Header * ros_message);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_space_msgs
size_t get_serialized_size_std_msgs__msg__Header(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_space_msgs
size_t max_serialized_size_std_msgs__msg__Header(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_space_msgs
bool cdr_serialize_key_std_msgs__msg__Header(
  const std_msgs__msg__Header * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_space_msgs
size_t get_serialized_size_key_std_msgs__msg__Header(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_space_msgs
size_t max_serialized_size_key_std_msgs__msg__Header(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_space_msgs
const rosidl_message_type_support_t *
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, std_msgs, msg, Header)();


using _TraversabilityScore__ros_msg_type = space_msgs__msg__TraversabilityScore;


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_space_msgs
bool cdr_serialize_space_msgs__msg__TraversabilityScore(
  const space_msgs__msg__TraversabilityScore * ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Field name: header
  {
    cdr_serialize_std_msgs__msg__Header(
      &ros_message->header, cdr);
  }

  // Field name: rover_id
  {
    const rosidl_runtime_c__String * str = &ros_message->rover_id;
    if (str->capacity == 0 || str->capacity <= str->size) {
      fprintf(stderr, "string capacity not greater than size\n");
      return false;
    }
    if (str->data[str->size] != '\0') {
      fprintf(stderr, "string not null-terminated\n");
      return false;
    }
    cdr << str->data;
  }

  // Field name: rover_spec
  {
    cdr_serialize_space_msgs__msg__RoverSpec(
      &ros_message->rover_spec, cdr);
  }

  // Field name: grid
  {
    cdr_serialize_grid_map_msgs__msg__GridMap(
      &ros_message->grid, cdr);
  }

  // Field name: terrain_stamp
  {
    cdr_serialize_builtin_interfaces__msg__Time(
      &ros_message->terrain_stamp, cdr);
  }

  // Field name: soil_model_id
  {
    const rosidl_runtime_c__String * str = &ros_message->soil_model_id;
    if (str->capacity == 0 || str->capacity <= str->size) {
      fprintf(stderr, "string capacity not greater than size\n");
      return false;
    }
    if (str->data[str->size] != '\0') {
      fprintf(stderr, "string not null-terminated\n");
      return false;
    }
    cdr << str->data;
  }

  // Field name: soil_model_version
  {
    const rosidl_runtime_c__String * str = &ros_message->soil_model_version;
    if (str->capacity == 0 || str->capacity <= str->size) {
      fprintf(stderr, "string capacity not greater than size\n");
      return false;
    }
    if (str->data[str->size] != '\0') {
      fprintf(stderr, "string not null-terminated\n");
      return false;
    }
    cdr << str->data;
  }

  // Field name: evaluator_version
  {
    const rosidl_runtime_c__String * str = &ros_message->evaluator_version;
    if (str->capacity == 0 || str->capacity <= str->size) {
      fprintf(stderr, "string capacity not greater than size\n");
      return false;
    }
    if (str->data[str->size] != '\0') {
      fprintf(stderr, "string not null-terminated\n");
      return false;
    }
    cdr << str->data;
  }

  return true;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_space_msgs
bool cdr_deserialize_space_msgs__msg__TraversabilityScore(
  eprosima::fastcdr::Cdr & cdr,
  space_msgs__msg__TraversabilityScore * ros_message)
{
  // Field name: header
  {
    cdr_deserialize_std_msgs__msg__Header(cdr, &ros_message->header);
  }

  // Field name: rover_id
  {
    std::string tmp;
    cdr >> tmp;
    if (!ros_message->rover_id.data) {
      rosidl_runtime_c__String__init(&ros_message->rover_id);
    }
    bool succeeded = rosidl_runtime_c__String__assign(
      &ros_message->rover_id,
      tmp.c_str());
    if (!succeeded) {
      fprintf(stderr, "failed to assign string into field 'rover_id'\n");
      return false;
    }
  }

  // Field name: rover_spec
  {
    cdr_deserialize_space_msgs__msg__RoverSpec(cdr, &ros_message->rover_spec);
  }

  // Field name: grid
  {
    cdr_deserialize_grid_map_msgs__msg__GridMap(cdr, &ros_message->grid);
  }

  // Field name: terrain_stamp
  {
    cdr_deserialize_builtin_interfaces__msg__Time(cdr, &ros_message->terrain_stamp);
  }

  // Field name: soil_model_id
  {
    std::string tmp;
    cdr >> tmp;
    if (!ros_message->soil_model_id.data) {
      rosidl_runtime_c__String__init(&ros_message->soil_model_id);
    }
    bool succeeded = rosidl_runtime_c__String__assign(
      &ros_message->soil_model_id,
      tmp.c_str());
    if (!succeeded) {
      fprintf(stderr, "failed to assign string into field 'soil_model_id'\n");
      return false;
    }
  }

  // Field name: soil_model_version
  {
    std::string tmp;
    cdr >> tmp;
    if (!ros_message->soil_model_version.data) {
      rosidl_runtime_c__String__init(&ros_message->soil_model_version);
    }
    bool succeeded = rosidl_runtime_c__String__assign(
      &ros_message->soil_model_version,
      tmp.c_str());
    if (!succeeded) {
      fprintf(stderr, "failed to assign string into field 'soil_model_version'\n");
      return false;
    }
  }

  // Field name: evaluator_version
  {
    std::string tmp;
    cdr >> tmp;
    if (!ros_message->evaluator_version.data) {
      rosidl_runtime_c__String__init(&ros_message->evaluator_version);
    }
    bool succeeded = rosidl_runtime_c__String__assign(
      &ros_message->evaluator_version,
      tmp.c_str());
    if (!succeeded) {
      fprintf(stderr, "failed to assign string into field 'evaluator_version'\n");
      return false;
    }
  }

  return true;
}  // NOLINT(readability/fn_size)


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_space_msgs
size_t get_serialized_size_space_msgs__msg__TraversabilityScore(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _TraversabilityScore__ros_msg_type * ros_message = static_cast<const _TraversabilityScore__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Field name: header
  current_alignment += get_serialized_size_std_msgs__msg__Header(
    &(ros_message->header), current_alignment);

  // Field name: rover_id
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->rover_id.size + 1);

  // Field name: rover_spec
  current_alignment += get_serialized_size_space_msgs__msg__RoverSpec(
    &(ros_message->rover_spec), current_alignment);

  // Field name: grid
  current_alignment += get_serialized_size_grid_map_msgs__msg__GridMap(
    &(ros_message->grid), current_alignment);

  // Field name: terrain_stamp
  current_alignment += get_serialized_size_builtin_interfaces__msg__Time(
    &(ros_message->terrain_stamp), current_alignment);

  // Field name: soil_model_id
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->soil_model_id.size + 1);

  // Field name: soil_model_version
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->soil_model_version.size + 1);

  // Field name: evaluator_version
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->evaluator_version.size + 1);

  return current_alignment - initial_alignment;
}


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_space_msgs
size_t max_serialized_size_space_msgs__msg__TraversabilityScore(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  size_t last_member_size = 0;
  (void)last_member_size;
  (void)padding;
  (void)wchar_size;

  full_bounded = true;
  is_plain = true;

  // Field name: header
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_std_msgs__msg__Header(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: rover_id
  {
    size_t array_size = 1;
    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }

  // Field name: rover_spec
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_space_msgs__msg__RoverSpec(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: grid
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_grid_map_msgs__msg__GridMap(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: terrain_stamp
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_builtin_interfaces__msg__Time(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: soil_model_id
  {
    size_t array_size = 1;
    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }

  // Field name: soil_model_version
  {
    size_t array_size = 1;
    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }

  // Field name: evaluator_version
  {
    size_t array_size = 1;
    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }


  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = space_msgs__msg__TraversabilityScore;
    is_plain =
      (
      offsetof(DataType, evaluator_version) +
      last_member_size
      ) == ret_val;
  }
  return ret_val;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_space_msgs
bool cdr_serialize_key_space_msgs__msg__TraversabilityScore(
  const space_msgs__msg__TraversabilityScore * ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Field name: header
  {
    cdr_serialize_key_std_msgs__msg__Header(
      &ros_message->header, cdr);
  }

  // Field name: rover_id
  {
    const rosidl_runtime_c__String * str = &ros_message->rover_id;
    if (str->capacity == 0 || str->capacity <= str->size) {
      fprintf(stderr, "string capacity not greater than size\n");
      return false;
    }
    if (str->data[str->size] != '\0') {
      fprintf(stderr, "string not null-terminated\n");
      return false;
    }
    cdr << str->data;
  }

  // Field name: rover_spec
  {
    cdr_serialize_key_space_msgs__msg__RoverSpec(
      &ros_message->rover_spec, cdr);
  }

  // Field name: grid
  {
    cdr_serialize_key_grid_map_msgs__msg__GridMap(
      &ros_message->grid, cdr);
  }

  // Field name: terrain_stamp
  {
    cdr_serialize_key_builtin_interfaces__msg__Time(
      &ros_message->terrain_stamp, cdr);
  }

  // Field name: soil_model_id
  {
    const rosidl_runtime_c__String * str = &ros_message->soil_model_id;
    if (str->capacity == 0 || str->capacity <= str->size) {
      fprintf(stderr, "string capacity not greater than size\n");
      return false;
    }
    if (str->data[str->size] != '\0') {
      fprintf(stderr, "string not null-terminated\n");
      return false;
    }
    cdr << str->data;
  }

  // Field name: soil_model_version
  {
    const rosidl_runtime_c__String * str = &ros_message->soil_model_version;
    if (str->capacity == 0 || str->capacity <= str->size) {
      fprintf(stderr, "string capacity not greater than size\n");
      return false;
    }
    if (str->data[str->size] != '\0') {
      fprintf(stderr, "string not null-terminated\n");
      return false;
    }
    cdr << str->data;
  }

  // Field name: evaluator_version
  {
    const rosidl_runtime_c__String * str = &ros_message->evaluator_version;
    if (str->capacity == 0 || str->capacity <= str->size) {
      fprintf(stderr, "string capacity not greater than size\n");
      return false;
    }
    if (str->data[str->size] != '\0') {
      fprintf(stderr, "string not null-terminated\n");
      return false;
    }
    cdr << str->data;
  }

  return true;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_space_msgs
size_t get_serialized_size_key_space_msgs__msg__TraversabilityScore(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _TraversabilityScore__ros_msg_type * ros_message = static_cast<const _TraversabilityScore__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;

  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Field name: header
  current_alignment += get_serialized_size_key_std_msgs__msg__Header(
    &(ros_message->header), current_alignment);

  // Field name: rover_id
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->rover_id.size + 1);

  // Field name: rover_spec
  current_alignment += get_serialized_size_key_space_msgs__msg__RoverSpec(
    &(ros_message->rover_spec), current_alignment);

  // Field name: grid
  current_alignment += get_serialized_size_key_grid_map_msgs__msg__GridMap(
    &(ros_message->grid), current_alignment);

  // Field name: terrain_stamp
  current_alignment += get_serialized_size_key_builtin_interfaces__msg__Time(
    &(ros_message->terrain_stamp), current_alignment);

  // Field name: soil_model_id
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->soil_model_id.size + 1);

  // Field name: soil_model_version
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->soil_model_version.size + 1);

  // Field name: evaluator_version
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->evaluator_version.size + 1);

  return current_alignment - initial_alignment;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_space_msgs
size_t max_serialized_size_key_space_msgs__msg__TraversabilityScore(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  size_t last_member_size = 0;
  (void)last_member_size;
  (void)padding;
  (void)wchar_size;

  full_bounded = true;
  is_plain = true;
  // Field name: header
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_key_std_msgs__msg__Header(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: rover_id
  {
    size_t array_size = 1;
    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }

  // Field name: rover_spec
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_key_space_msgs__msg__RoverSpec(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: grid
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_key_grid_map_msgs__msg__GridMap(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: terrain_stamp
  {
    size_t array_size = 1;
    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_key_builtin_interfaces__msg__Time(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  // Field name: soil_model_id
  {
    size_t array_size = 1;
    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }

  // Field name: soil_model_version
  {
    size_t array_size = 1;
    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }

  // Field name: evaluator_version
  {
    size_t array_size = 1;
    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }

  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = space_msgs__msg__TraversabilityScore;
    is_plain =
      (
      offsetof(DataType, evaluator_version) +
      last_member_size
      ) == ret_val;
  }
  return ret_val;
}


static bool _TraversabilityScore__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const space_msgs__msg__TraversabilityScore * ros_message = static_cast<const space_msgs__msg__TraversabilityScore *>(untyped_ros_message);
  (void)ros_message;
  return cdr_serialize_space_msgs__msg__TraversabilityScore(ros_message, cdr);
}

static bool _TraversabilityScore__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  space_msgs__msg__TraversabilityScore * ros_message = static_cast<space_msgs__msg__TraversabilityScore *>(untyped_ros_message);
  (void)ros_message;
  return cdr_deserialize_space_msgs__msg__TraversabilityScore(cdr, ros_message);
}

static uint32_t _TraversabilityScore__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_space_msgs__msg__TraversabilityScore(
      untyped_ros_message, 0));
}

static size_t _TraversabilityScore__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_space_msgs__msg__TraversabilityScore(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_TraversabilityScore = {
  "space_msgs::msg",
  "TraversabilityScore",
  _TraversabilityScore__cdr_serialize,
  _TraversabilityScore__cdr_deserialize,
  _TraversabilityScore__get_serialized_size,
  _TraversabilityScore__max_serialized_size,
  nullptr
};

static rosidl_message_type_support_t _TraversabilityScore__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_TraversabilityScore,
  get_message_typesupport_handle_function,
  &space_msgs__msg__TraversabilityScore__get_type_hash,
  &space_msgs__msg__TraversabilityScore__get_type_description,
  &space_msgs__msg__TraversabilityScore__get_type_description_sources,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, space_msgs, msg, TraversabilityScore)() {
  return &_TraversabilityScore__type_support;
}

#if defined(__cplusplus)
}
#endif
