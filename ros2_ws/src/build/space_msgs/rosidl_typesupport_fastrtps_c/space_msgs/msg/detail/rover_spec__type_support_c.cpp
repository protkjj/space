// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from space_msgs:msg/RoverSpec.idl
// generated code does not contain a copyright notice
#include "space_msgs/msg/detail/rover_spec__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <cstddef>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/serialization_helpers.hpp"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "space_msgs/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "space_msgs/msg/detail/rover_spec__struct.h"
#include "space_msgs/msg/detail/rover_spec__functions.h"
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

#include "rosidl_runtime_c/string.h"  // provenance_note, rover_id
#include "rosidl_runtime_c/string_functions.h"  // provenance_note, rover_id

// forward declare type support functions


using _RoverSpec__ros_msg_type = space_msgs__msg__RoverSpec;


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_space_msgs
bool cdr_serialize_space_msgs__msg__RoverSpec(
  const space_msgs__msg__RoverSpec * ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
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

  // Field name: mass_kg
  {
    cdr << ros_message->mass_kg;
  }

  // Field name: wheel_radius_m
  {
    cdr << ros_message->wheel_radius_m;
  }

  // Field name: wheel_width_m
  {
    cdr << ros_message->wheel_width_m;
  }

  // Field name: ground_pressure_kpa
  {
    cdr << ros_message->ground_pressure_kpa;
  }

  // Field name: max_climb_angle_rad
  {
    cdr << ros_message->max_climb_angle_rad;
  }

  // Field name: min_passable_width_m
  {
    cdr << ros_message->min_passable_width_m;
  }

  // Field name: ground_clearance_m
  {
    cdr << ros_message->ground_clearance_m;
  }

  // Field name: has_grousers
  {
    cdr << (ros_message->has_grousers ? true : false);
  }

  // Field name: provenance
  {
    cdr << ros_message->provenance;
  }

  // Field name: provenance_note
  {
    const rosidl_runtime_c__String * str = &ros_message->provenance_note;
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
bool cdr_deserialize_space_msgs__msg__RoverSpec(
  eprosima::fastcdr::Cdr & cdr,
  space_msgs__msg__RoverSpec * ros_message)
{
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

  // Field name: mass_kg
  {
    cdr >> ros_message->mass_kg;
  }

  // Field name: wheel_radius_m
  {
    cdr >> ros_message->wheel_radius_m;
  }

  // Field name: wheel_width_m
  {
    cdr >> ros_message->wheel_width_m;
  }

  // Field name: ground_pressure_kpa
  {
    cdr >> ros_message->ground_pressure_kpa;
  }

  // Field name: max_climb_angle_rad
  {
    cdr >> ros_message->max_climb_angle_rad;
  }

  // Field name: min_passable_width_m
  {
    cdr >> ros_message->min_passable_width_m;
  }

  // Field name: ground_clearance_m
  {
    cdr >> ros_message->ground_clearance_m;
  }

  // Field name: has_grousers
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message->has_grousers = tmp ? true : false;
  }

  // Field name: provenance
  {
    cdr >> ros_message->provenance;
  }

  // Field name: provenance_note
  {
    std::string tmp;
    cdr >> tmp;
    if (!ros_message->provenance_note.data) {
      rosidl_runtime_c__String__init(&ros_message->provenance_note);
    }
    bool succeeded = rosidl_runtime_c__String__assign(
      &ros_message->provenance_note,
      tmp.c_str());
    if (!succeeded) {
      fprintf(stderr, "failed to assign string into field 'provenance_note'\n");
      return false;
    }
  }

  return true;
}  // NOLINT(readability/fn_size)


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_space_msgs
size_t get_serialized_size_space_msgs__msg__RoverSpec(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _RoverSpec__ros_msg_type * ros_message = static_cast<const _RoverSpec__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Field name: rover_id
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->rover_id.size + 1);

  // Field name: mass_kg
  {
    size_t item_size = sizeof(ros_message->mass_kg);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: wheel_radius_m
  {
    size_t item_size = sizeof(ros_message->wheel_radius_m);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: wheel_width_m
  {
    size_t item_size = sizeof(ros_message->wheel_width_m);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: ground_pressure_kpa
  {
    size_t item_size = sizeof(ros_message->ground_pressure_kpa);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: max_climb_angle_rad
  {
    size_t item_size = sizeof(ros_message->max_climb_angle_rad);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: min_passable_width_m
  {
    size_t item_size = sizeof(ros_message->min_passable_width_m);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: ground_clearance_m
  {
    size_t item_size = sizeof(ros_message->ground_clearance_m);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: has_grousers
  {
    size_t item_size = sizeof(ros_message->has_grousers);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: provenance
  {
    size_t item_size = sizeof(ros_message->provenance);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: provenance_note
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->provenance_note.size + 1);

  return current_alignment - initial_alignment;
}


ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_space_msgs
size_t max_serialized_size_space_msgs__msg__RoverSpec(
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

  // Field name: mass_kg
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: wheel_radius_m
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: wheel_width_m
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: ground_pressure_kpa
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: max_climb_angle_rad
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: min_passable_width_m
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: ground_clearance_m
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: has_grousers
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: provenance
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: provenance_note
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
    using DataType = space_msgs__msg__RoverSpec;
    is_plain =
      (
      offsetof(DataType, provenance_note) +
      last_member_size
      ) == ret_val;
  }
  return ret_val;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_space_msgs
bool cdr_serialize_key_space_msgs__msg__RoverSpec(
  const space_msgs__msg__RoverSpec * ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
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

  // Field name: mass_kg
  {
    cdr << ros_message->mass_kg;
  }

  // Field name: wheel_radius_m
  {
    cdr << ros_message->wheel_radius_m;
  }

  // Field name: wheel_width_m
  {
    cdr << ros_message->wheel_width_m;
  }

  // Field name: ground_pressure_kpa
  {
    cdr << ros_message->ground_pressure_kpa;
  }

  // Field name: max_climb_angle_rad
  {
    cdr << ros_message->max_climb_angle_rad;
  }

  // Field name: min_passable_width_m
  {
    cdr << ros_message->min_passable_width_m;
  }

  // Field name: ground_clearance_m
  {
    cdr << ros_message->ground_clearance_m;
  }

  // Field name: has_grousers
  {
    cdr << (ros_message->has_grousers ? true : false);
  }

  // Field name: provenance
  {
    cdr << ros_message->provenance;
  }

  // Field name: provenance_note
  {
    const rosidl_runtime_c__String * str = &ros_message->provenance_note;
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
size_t get_serialized_size_key_space_msgs__msg__RoverSpec(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _RoverSpec__ros_msg_type * ros_message = static_cast<const _RoverSpec__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;

  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Field name: rover_id
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->rover_id.size + 1);

  // Field name: mass_kg
  {
    size_t item_size = sizeof(ros_message->mass_kg);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: wheel_radius_m
  {
    size_t item_size = sizeof(ros_message->wheel_radius_m);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: wheel_width_m
  {
    size_t item_size = sizeof(ros_message->wheel_width_m);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: ground_pressure_kpa
  {
    size_t item_size = sizeof(ros_message->ground_pressure_kpa);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: max_climb_angle_rad
  {
    size_t item_size = sizeof(ros_message->max_climb_angle_rad);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: min_passable_width_m
  {
    size_t item_size = sizeof(ros_message->min_passable_width_m);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: ground_clearance_m
  {
    size_t item_size = sizeof(ros_message->ground_clearance_m);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: has_grousers
  {
    size_t item_size = sizeof(ros_message->has_grousers);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: provenance
  {
    size_t item_size = sizeof(ros_message->provenance);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Field name: provenance_note
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->provenance_note.size + 1);

  return current_alignment - initial_alignment;
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_space_msgs
size_t max_serialized_size_key_space_msgs__msg__RoverSpec(
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

  // Field name: mass_kg
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: wheel_radius_m
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: wheel_width_m
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: ground_pressure_kpa
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: max_climb_angle_rad
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: min_passable_width_m
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: ground_clearance_m
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Field name: has_grousers
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: provenance
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Field name: provenance_note
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
    using DataType = space_msgs__msg__RoverSpec;
    is_plain =
      (
      offsetof(DataType, provenance_note) +
      last_member_size
      ) == ret_val;
  }
  return ret_val;
}


static bool _RoverSpec__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const space_msgs__msg__RoverSpec * ros_message = static_cast<const space_msgs__msg__RoverSpec *>(untyped_ros_message);
  (void)ros_message;
  return cdr_serialize_space_msgs__msg__RoverSpec(ros_message, cdr);
}

static bool _RoverSpec__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  space_msgs__msg__RoverSpec * ros_message = static_cast<space_msgs__msg__RoverSpec *>(untyped_ros_message);
  (void)ros_message;
  return cdr_deserialize_space_msgs__msg__RoverSpec(cdr, ros_message);
}

static uint32_t _RoverSpec__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_space_msgs__msg__RoverSpec(
      untyped_ros_message, 0));
}

static size_t _RoverSpec__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_space_msgs__msg__RoverSpec(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_RoverSpec = {
  "space_msgs::msg",
  "RoverSpec",
  _RoverSpec__cdr_serialize,
  _RoverSpec__cdr_deserialize,
  _RoverSpec__get_serialized_size,
  _RoverSpec__max_serialized_size,
  nullptr
};

static rosidl_message_type_support_t _RoverSpec__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_RoverSpec,
  get_message_typesupport_handle_function,
  &space_msgs__msg__RoverSpec__get_type_hash,
  &space_msgs__msg__RoverSpec__get_type_description,
  &space_msgs__msg__RoverSpec__get_type_description_sources,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, space_msgs, msg, RoverSpec)() {
  return &_RoverSpec__type_support;
}

#if defined(__cplusplus)
}
#endif
