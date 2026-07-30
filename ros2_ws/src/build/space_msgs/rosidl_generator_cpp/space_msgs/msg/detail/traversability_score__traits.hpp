// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from space_msgs:msg/TraversabilityScore.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "space_msgs/msg/traversability_score.hpp"


#ifndef SPACE_MSGS__MSG__DETAIL__TRAVERSABILITY_SCORE__TRAITS_HPP_
#define SPACE_MSGS__MSG__DETAIL__TRAVERSABILITY_SCORE__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "space_msgs/msg/detail/traversability_score__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"
// Member 'rover_spec'
#include "space_msgs/msg/detail/rover_spec__traits.hpp"
// Member 'grid'
#include "grid_map_msgs/msg/detail/grid_map__traits.hpp"
// Member 'terrain_stamp'
#include "builtin_interfaces/msg/detail/time__traits.hpp"

namespace space_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const TraversabilityScore & msg,
  std::ostream & out)
{
  out << "{";
  // member: header
  {
    out << "header: ";
    to_flow_style_yaml(msg.header, out);
    out << ", ";
  }

  // member: rover_id
  {
    out << "rover_id: ";
    rosidl_generator_traits::value_to_yaml(msg.rover_id, out);
    out << ", ";
  }

  // member: rover_spec
  {
    out << "rover_spec: ";
    to_flow_style_yaml(msg.rover_spec, out);
    out << ", ";
  }

  // member: grid
  {
    out << "grid: ";
    to_flow_style_yaml(msg.grid, out);
    out << ", ";
  }

  // member: terrain_stamp
  {
    out << "terrain_stamp: ";
    to_flow_style_yaml(msg.terrain_stamp, out);
    out << ", ";
  }

  // member: soil_model_id
  {
    out << "soil_model_id: ";
    rosidl_generator_traits::value_to_yaml(msg.soil_model_id, out);
    out << ", ";
  }

  // member: soil_model_version
  {
    out << "soil_model_version: ";
    rosidl_generator_traits::value_to_yaml(msg.soil_model_version, out);
    out << ", ";
  }

  // member: evaluator_version
  {
    out << "evaluator_version: ";
    rosidl_generator_traits::value_to_yaml(msg.evaluator_version, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const TraversabilityScore & msg,
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

  // member: rover_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "rover_id: ";
    rosidl_generator_traits::value_to_yaml(msg.rover_id, out);
    out << "\n";
  }

  // member: rover_spec
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "rover_spec:\n";
    to_block_style_yaml(msg.rover_spec, out, indentation + 2);
  }

  // member: grid
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "grid:\n";
    to_block_style_yaml(msg.grid, out, indentation + 2);
  }

  // member: terrain_stamp
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "terrain_stamp:\n";
    to_block_style_yaml(msg.terrain_stamp, out, indentation + 2);
  }

  // member: soil_model_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "soil_model_id: ";
    rosidl_generator_traits::value_to_yaml(msg.soil_model_id, out);
    out << "\n";
  }

  // member: soil_model_version
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "soil_model_version: ";
    rosidl_generator_traits::value_to_yaml(msg.soil_model_version, out);
    out << "\n";
  }

  // member: evaluator_version
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "evaluator_version: ";
    rosidl_generator_traits::value_to_yaml(msg.evaluator_version, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const TraversabilityScore & msg, bool use_flow_style = false)
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
  const space_msgs::msg::TraversabilityScore & msg,
  std::ostream & out, size_t indentation = 0)
{
  space_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use space_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const space_msgs::msg::TraversabilityScore & msg)
{
  return space_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<space_msgs::msg::TraversabilityScore>()
{
  return "space_msgs::msg::TraversabilityScore";
}

template<>
inline const char * name<space_msgs::msg::TraversabilityScore>()
{
  return "space_msgs/msg/TraversabilityScore";
}

template<>
struct has_fixed_size<space_msgs::msg::TraversabilityScore>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<space_msgs::msg::TraversabilityScore>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<space_msgs::msg::TraversabilityScore>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // SPACE_MSGS__MSG__DETAIL__TRAVERSABILITY_SCORE__TRAITS_HPP_
