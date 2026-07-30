// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from space_msgs:msg/SlipEstimate.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "space_msgs/msg/slip_estimate.hpp"


#ifndef SPACE_MSGS__MSG__DETAIL__SLIP_ESTIMATE__TRAITS_HPP_
#define SPACE_MSGS__MSG__DETAIL__SLIP_ESTIMATE__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "space_msgs/msg/detail/slip_estimate__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"

namespace space_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const SlipEstimate & msg,
  std::ostream & out)
{
  out << "{";
  // member: header
  {
    out << "header: ";
    to_flow_style_yaml(msg.header, out);
    out << ", ";
  }

  // member: slip_ratio
  {
    out << "slip_ratio: ";
    rosidl_generator_traits::value_to_yaml(msg.slip_ratio, out);
    out << ", ";
  }

  // member: v_wheel
  {
    out << "v_wheel: ";
    rosidl_generator_traits::value_to_yaml(msg.v_wheel, out);
    out << ", ";
  }

  // member: v_actual
  {
    out << "v_actual: ";
    rosidl_generator_traits::value_to_yaml(msg.v_actual, out);
    out << ", ";
  }

  // member: valid
  {
    out << "valid: ";
    rosidl_generator_traits::value_to_yaml(msg.valid, out);
    out << ", ";
  }

  // member: quality
  {
    out << "quality: ";
    rosidl_generator_traits::value_to_yaml(msg.quality, out);
    out << ", ";
  }

  // member: source
  {
    out << "source: ";
    rosidl_generator_traits::value_to_yaml(msg.source, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const SlipEstimate & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: header
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "header:\n";
    to_block_style_yaml(msg.header, out, indentation + 2);
  }

  // member: slip_ratio
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "slip_ratio: ";
    rosidl_generator_traits::value_to_yaml(msg.slip_ratio, out);
    out << "\n";
  }

  // member: v_wheel
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "v_wheel: ";
    rosidl_generator_traits::value_to_yaml(msg.v_wheel, out);
    out << "\n";
  }

  // member: v_actual
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "v_actual: ";
    rosidl_generator_traits::value_to_yaml(msg.v_actual, out);
    out << "\n";
  }

  // member: valid
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "valid: ";
    rosidl_generator_traits::value_to_yaml(msg.valid, out);
    out << "\n";
  }

  // member: quality
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "quality: ";
    rosidl_generator_traits::value_to_yaml(msg.quality, out);
    out << "\n";
  }

  // member: source
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "source: ";
    rosidl_generator_traits::value_to_yaml(msg.source, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const SlipEstimate & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace space_msgs

namespace rosidl_generator_traits
{

[[deprecated("use space_msgs::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const space_msgs::msg::SlipEstimate & msg,
  std::ostream & out, size_t indentation = 0)
{
  space_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use space_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const space_msgs::msg::SlipEstimate & msg)
{
  return space_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<space_msgs::msg::SlipEstimate>()
{
  return "space_msgs::msg::SlipEstimate";
}

template<>
inline const char * name<space_msgs::msg::SlipEstimate>()
{
  return "space_msgs/msg/SlipEstimate";
}

template<>
struct has_fixed_size<space_msgs::msg::SlipEstimate>
  : std::integral_constant<bool, has_fixed_size<std_msgs::msg::Header>::value> {};

template<>
struct has_bounded_size<space_msgs::msg::SlipEstimate>
  : std::integral_constant<bool, has_bounded_size<std_msgs::msg::Header>::value> {};

template<>
struct is_message<space_msgs::msg::SlipEstimate>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // SPACE_MSGS__MSG__DETAIL__SLIP_ESTIMATE__TRAITS_HPP_
