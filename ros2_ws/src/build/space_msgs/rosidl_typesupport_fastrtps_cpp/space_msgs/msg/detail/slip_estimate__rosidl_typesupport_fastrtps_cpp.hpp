// generated from rosidl_typesupport_fastrtps_cpp/resource/idl__rosidl_typesupport_fastrtps_cpp.hpp.em
// with input from space_msgs:msg/SlipEstimate.idl
// generated code does not contain a copyright notice

#ifndef SPACE_MSGS__MSG__DETAIL__SLIP_ESTIMATE__ROSIDL_TYPESUPPORT_FASTRTPS_CPP_HPP_
#define SPACE_MSGS__MSG__DETAIL__SLIP_ESTIMATE__ROSIDL_TYPESUPPORT_FASTRTPS_CPP_HPP_

#include <cstddef>
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_interface/macros.h"
#include "space_msgs/msg/rosidl_typesupport_fastrtps_cpp__visibility_control.h"
#include "space_msgs/msg/detail/slip_estimate__struct.hpp"

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

#include "fastcdr/Cdr.h"

namespace space_msgs
{

namespace msg
{

namespace typesupport_fastrtps_cpp
{

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_space_msgs
cdr_serialize(
  const space_msgs::msg::SlipEstimate & ros_message,
  eprosima::fastcdr::Cdr & cdr);

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_space_msgs
cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  space_msgs::msg::SlipEstimate & ros_message);

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_space_msgs
get_serialized_size(
  const space_msgs::msg::SlipEstimate & ros_message,
  size_t current_alignment);

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_space_msgs
max_serialized_size_SlipEstimate(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_space_msgs
cdr_serialize_key(
  const space_msgs::msg::SlipEstimate & ros_message,
  eprosima::fastcdr::Cdr &);

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_space_msgs
get_serialized_size_key(
  const space_msgs::msg::SlipEstimate & ros_message,
  size_t current_alignment);

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_space_msgs
max_serialized_size_key_SlipEstimate(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

}  // namespace typesupport_fastrtps_cpp

}  // namespace msg

}  // namespace space_msgs

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_space_msgs
const rosidl_message_type_support_t *
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, space_msgs, msg, SlipEstimate)();

#ifdef __cplusplus
}
#endif

#endif  // SPACE_MSGS__MSG__DETAIL__SLIP_ESTIMATE__ROSIDL_TYPESUPPORT_FASTRTPS_CPP_HPP_
