// generated from rosidl_typesupport_fastrtps_c/resource/idl__rosidl_typesupport_fastrtps_c.h.em
// with input from space_msgs:msg/SlipEstimate.idl
// generated code does not contain a copyright notice
#ifndef SPACE_MSGS__MSG__DETAIL__SLIP_ESTIMATE__ROSIDL_TYPESUPPORT_FASTRTPS_C_H_
#define SPACE_MSGS__MSG__DETAIL__SLIP_ESTIMATE__ROSIDL_TYPESUPPORT_FASTRTPS_C_H_


#include <stddef.h>
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_interface/macros.h"
#include "space_msgs/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "space_msgs/msg/detail/slip_estimate__struct.h"
#include "fastcdr/Cdr.h"

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_space_msgs
bool cdr_serialize_space_msgs__msg__SlipEstimate(
  const space_msgs__msg__SlipEstimate * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_space_msgs
bool cdr_deserialize_space_msgs__msg__SlipEstimate(
  eprosima::fastcdr::Cdr &,
  space_msgs__msg__SlipEstimate * ros_message);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_space_msgs
size_t get_serialized_size_space_msgs__msg__SlipEstimate(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_space_msgs
size_t max_serialized_size_space_msgs__msg__SlipEstimate(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_space_msgs
bool cdr_serialize_key_space_msgs__msg__SlipEstimate(
  const space_msgs__msg__SlipEstimate * ros_message,
  eprosima::fastcdr::Cdr & cdr);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_space_msgs
size_t get_serialized_size_key_space_msgs__msg__SlipEstimate(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_space_msgs
size_t max_serialized_size_key_space_msgs__msg__SlipEstimate(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_space_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, space_msgs, msg, SlipEstimate)();

#ifdef __cplusplus
}
#endif

#endif  // SPACE_MSGS__MSG__DETAIL__SLIP_ESTIMATE__ROSIDL_TYPESUPPORT_FASTRTPS_C_H_
