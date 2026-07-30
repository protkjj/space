// generated from rosidl_typesupport_fastrtps_cpp/resource/idl__type_support.cpp.em
// with input from space_msgs:msg/RoverSpec.idl
// generated code does not contain a copyright notice
#include "space_msgs/msg/detail/rover_spec__rosidl_typesupport_fastrtps_cpp.hpp"
#include "space_msgs/msg/detail/rover_spec__functions.h"
#include "space_msgs/msg/detail/rover_spec__struct.hpp"

#include <cstddef>
#include <limits>
#include <stdexcept>
#include <string>
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_fastrtps_cpp/identifier.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_fastrtps_cpp/serialization_helpers.hpp"
#include "rosidl_typesupport_fastrtps_cpp/wstring_conversion.hpp"
#include "fastcdr/Cdr.h"


// forward declaration of message dependencies and their conversion functions

namespace space_msgs
{

namespace msg
{

namespace typesupport_fastrtps_cpp
{


bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_space_msgs
cdr_serialize(
  const space_msgs::msg::RoverSpec & ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Member: rover_id
  cdr << ros_message.rover_id;

  // Member: mass_kg
  cdr << ros_message.mass_kg;

  // Member: wheel_radius_m
  cdr << ros_message.wheel_radius_m;

  // Member: wheel_width_m
  cdr << ros_message.wheel_width_m;

  // Member: ground_pressure_kpa
  cdr << ros_message.ground_pressure_kpa;

  // Member: max_climb_angle_rad
  cdr << ros_message.max_climb_angle_rad;

  // Member: min_passable_width_m
  cdr << ros_message.min_passable_width_m;

  // Member: ground_clearance_m
  cdr << ros_message.ground_clearance_m;

  // Member: has_grousers
  cdr << (ros_message.has_grousers ? true : false);

  // Member: provenance
  cdr << ros_message.provenance;

  // Member: provenance_note
  cdr << ros_message.provenance_note;

  return true;
}

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_space_msgs
cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  space_msgs::msg::RoverSpec & ros_message)
{
  // Member: rover_id
  cdr >> ros_message.rover_id;

  // Member: mass_kg
  cdr >> ros_message.mass_kg;

  // Member: wheel_radius_m
  cdr >> ros_message.wheel_radius_m;

  // Member: wheel_width_m
  cdr >> ros_message.wheel_width_m;

  // Member: ground_pressure_kpa
  cdr >> ros_message.ground_pressure_kpa;

  // Member: max_climb_angle_rad
  cdr >> ros_message.max_climb_angle_rad;

  // Member: min_passable_width_m
  cdr >> ros_message.min_passable_width_m;

  // Member: ground_clearance_m
  cdr >> ros_message.ground_clearance_m;

  // Member: has_grousers
  {
    uint8_t tmp;
    cdr >> tmp;
    ros_message.has_grousers = tmp ? true : false;
  }

  // Member: provenance
  cdr >> ros_message.provenance;

  // Member: provenance_note
  cdr >> ros_message.provenance_note;

  return true;
}  // NOLINT(readability/fn_size)


size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_space_msgs
get_serialized_size(
  const space_msgs::msg::RoverSpec & ros_message,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Member: rover_id
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message.rover_id.size() + 1);

  // Member: mass_kg
  {
    size_t item_size = sizeof(ros_message.mass_kg);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: wheel_radius_m
  {
    size_t item_size = sizeof(ros_message.wheel_radius_m);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: wheel_width_m
  {
    size_t item_size = sizeof(ros_message.wheel_width_m);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: ground_pressure_kpa
  {
    size_t item_size = sizeof(ros_message.ground_pressure_kpa);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: max_climb_angle_rad
  {
    size_t item_size = sizeof(ros_message.max_climb_angle_rad);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: min_passable_width_m
  {
    size_t item_size = sizeof(ros_message.min_passable_width_m);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: ground_clearance_m
  {
    size_t item_size = sizeof(ros_message.ground_clearance_m);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: has_grousers
  {
    size_t item_size = sizeof(ros_message.has_grousers);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: provenance
  {
    size_t item_size = sizeof(ros_message.provenance);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: provenance_note
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message.provenance_note.size() + 1);

  return current_alignment - initial_alignment;
}


size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_space_msgs
max_serialized_size_RoverSpec(
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

  // Member: rover_id
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
  // Member: mass_kg
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: wheel_radius_m
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: wheel_width_m
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: ground_pressure_kpa
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: max_climb_angle_rad
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: min_passable_width_m
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: ground_clearance_m
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // Member: has_grousers
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // Member: provenance
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // Member: provenance_note
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
    using DataType = space_msgs::msg::RoverSpec;
    is_plain =
      (
      offsetof(DataType, provenance_note) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_space_msgs
cdr_serialize_key(
  const space_msgs::msg::RoverSpec & ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Member: rover_id
  cdr << ros_message.rover_id;

  // Member: mass_kg
  cdr << ros_message.mass_kg;

  // Member: wheel_radius_m
  cdr << ros_message.wheel_radius_m;

  // Member: wheel_width_m
  cdr << ros_message.wheel_width_m;

  // Member: ground_pressure_kpa
  cdr << ros_message.ground_pressure_kpa;

  // Member: max_climb_angle_rad
  cdr << ros_message.max_climb_angle_rad;

  // Member: min_passable_width_m
  cdr << ros_message.min_passable_width_m;

  // Member: ground_clearance_m
  cdr << ros_message.ground_clearance_m;

  // Member: has_grousers
  cdr << (ros_message.has_grousers ? true : false);

  // Member: provenance
  cdr << ros_message.provenance;

  // Member: provenance_note
  cdr << ros_message.provenance_note;

  return true;
}

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_space_msgs
get_serialized_size_key(
  const space_msgs::msg::RoverSpec & ros_message,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Member: rover_id
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message.rover_id.size() + 1);

  // Member: mass_kg
  {
    size_t item_size = sizeof(ros_message.mass_kg);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: wheel_radius_m
  {
    size_t item_size = sizeof(ros_message.wheel_radius_m);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: wheel_width_m
  {
    size_t item_size = sizeof(ros_message.wheel_width_m);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: ground_pressure_kpa
  {
    size_t item_size = sizeof(ros_message.ground_pressure_kpa);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: max_climb_angle_rad
  {
    size_t item_size = sizeof(ros_message.max_climb_angle_rad);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: min_passable_width_m
  {
    size_t item_size = sizeof(ros_message.min_passable_width_m);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: ground_clearance_m
  {
    size_t item_size = sizeof(ros_message.ground_clearance_m);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: has_grousers
  {
    size_t item_size = sizeof(ros_message.has_grousers);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: provenance
  {
    size_t item_size = sizeof(ros_message.provenance);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  // Member: provenance_note
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message.provenance_note.size() + 1);

  return current_alignment - initial_alignment;
}

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_space_msgs
max_serialized_size_key_RoverSpec(
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

  // Member: rover_id
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

  // Member: mass_kg
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: wheel_radius_m
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: wheel_width_m
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: ground_pressure_kpa
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: max_climb_angle_rad
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: min_passable_width_m
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: ground_clearance_m
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }

  // Member: has_grousers
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: provenance
  {
    size_t array_size = 1;
    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }

  // Member: provenance_note
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
    using DataType = space_msgs::msg::RoverSpec;
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
  auto typed_message =
    static_cast<const space_msgs::msg::RoverSpec *>(
    untyped_ros_message);
  return cdr_serialize(*typed_message, cdr);
}

static bool _RoverSpec__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  auto typed_message =
    static_cast<space_msgs::msg::RoverSpec *>(
    untyped_ros_message);
  return cdr_deserialize(cdr, *typed_message);
}

static uint32_t _RoverSpec__get_serialized_size(
  const void * untyped_ros_message)
{
  auto typed_message =
    static_cast<const space_msgs::msg::RoverSpec *>(
    untyped_ros_message);
  return static_cast<uint32_t>(get_serialized_size(*typed_message, 0));
}

static size_t _RoverSpec__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_RoverSpec(full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}

static message_type_support_callbacks_t _RoverSpec__callbacks = {
  "space_msgs::msg",
  "RoverSpec",
  _RoverSpec__cdr_serialize,
  _RoverSpec__cdr_deserialize,
  _RoverSpec__get_serialized_size,
  _RoverSpec__max_serialized_size,
  nullptr
};

static rosidl_message_type_support_t _RoverSpec__handle = {
  rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
  &_RoverSpec__callbacks,
  get_message_typesupport_handle_function,
  &space_msgs__msg__RoverSpec__get_type_hash,
  &space_msgs__msg__RoverSpec__get_type_description,
  &space_msgs__msg__RoverSpec__get_type_description_sources,
};

}  // namespace typesupport_fastrtps_cpp

}  // namespace msg

}  // namespace space_msgs

namespace rosidl_typesupport_fastrtps_cpp
{

template<>
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_EXPORT_space_msgs
const rosidl_message_type_support_t *
get_message_type_support_handle<space_msgs::msg::RoverSpec>()
{
  return &space_msgs::msg::typesupport_fastrtps_cpp::_RoverSpec__handle;
}

}  // namespace rosidl_typesupport_fastrtps_cpp

#ifdef __cplusplus
extern "C"
{
#endif

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, space_msgs, msg, RoverSpec)() {
  return &space_msgs::msg::typesupport_fastrtps_cpp::_RoverSpec__handle;
}

#ifdef __cplusplus
}
#endif
