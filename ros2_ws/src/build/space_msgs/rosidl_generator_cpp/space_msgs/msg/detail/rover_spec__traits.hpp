// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from space_msgs:msg/RoverSpec.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "space_msgs/msg/rover_spec.hpp"


#ifndef SPACE_MSGS__MSG__DETAIL__ROVER_SPEC__TRAITS_HPP_
#define SPACE_MSGS__MSG__DETAIL__ROVER_SPEC__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "space_msgs/msg/detail/rover_spec__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace space_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const RoverSpec & msg,
  std::ostream & out)
{
  out << "{";
  // member: rover_id
  {
    out << "rover_id: ";
    rosidl_generator_traits::value_to_yaml(msg.rover_id, out);
    out << ", ";
  }

  // member: mass_kg
  {
    out << "mass_kg: ";
    rosidl_generator_traits::value_to_yaml(msg.mass_kg, out);
    out << ", ";
  }

  // member: wheel_radius_m
  {
    out << "wheel_radius_m: ";
    rosidl_generator_traits::value_to_yaml(msg.wheel_radius_m, out);
    out << ", ";
  }

  // member: wheel_width_m
  {
    out << "wheel_width_m: ";
    rosidl_generator_traits::value_to_yaml(msg.wheel_width_m, out);
    out << ", ";
  }

  // member: ground_pressure_kpa
  {
    out << "ground_pressure_kpa: ";
    rosidl_generator_traits::value_to_yaml(msg.ground_pressure_kpa, out);
    out << ", ";
  }

  // member: max_climb_angle_rad
  {
    out << "max_climb_angle_rad: ";
    rosidl_generator_traits::value_to_yaml(msg.max_climb_angle_rad, out);
    out << ", ";
  }

  // member: min_passable_width_m
  {
    out << "min_passable_width_m: ";
    rosidl_generator_traits::value_to_yaml(msg.min_passable_width_m, out);
    out << ", ";
  }

  // member: ground_clearance_m
  {
    out << "ground_clearance_m: ";
    rosidl_generator_traits::value_to_yaml(msg.ground_clearance_m, out);
    out << ", ";
  }

  // member: has_grousers
  {
    out << "has_grousers: ";
    rosidl_generator_traits::value_to_yaml(msg.has_grousers, out);
    out << ", ";
  }

  // member: provenance
  {
    out << "provenance: ";
    rosidl_generator_traits::value_to_yaml(msg.provenance, out);
    out << ", ";
  }

  // member: provenance_note
  {
    out << "provenance_note: ";
    rosidl_generator_traits::value_to_yaml(msg.provenance_note, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const RoverSpec & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: rover_id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "rover_id: ";
    rosidl_generator_traits::value_to_yaml(msg.rover_id, out);
    out << "\n";
  }

  // member: mass_kg
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "mass_kg: ";
    rosidl_generator_traits::value_to_yaml(msg.mass_kg, out);
    out << "\n";
  }

  // member: wheel_radius_m
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "wheel_radius_m: ";
    rosidl_generator_traits::value_to_yaml(msg.wheel_radius_m, out);
    out << "\n";
  }

  // member: wheel_width_m
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "wheel_width_m: ";
    rosidl_generator_traits::value_to_yaml(msg.wheel_width_m, out);
    out << "\n";
  }

  // member: ground_pressure_kpa
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "ground_pressure_kpa: ";
    rosidl_generator_traits::value_to_yaml(msg.ground_pressure_kpa, out);
    out << "\n";
  }

  // member: max_climb_angle_rad
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "max_climb_angle_rad: ";
    rosidl_generator_traits::value_to_yaml(msg.max_climb_angle_rad, out);
    out << "\n";
  }

  // member: min_passable_width_m
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "min_passable_width_m: ";
    rosidl_generator_traits::value_to_yaml(msg.min_passable_width_m, out);
    out << "\n";
  }

  // member: ground_clearance_m
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "ground_clearance_m: ";
    rosidl_generator_traits::value_to_yaml(msg.ground_clearance_m, out);
    out << "\n";
  }

  // member: has_grousers
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "has_grousers: ";
    rosidl_generator_traits::value_to_yaml(msg.has_grousers, out);
    out << "\n";
  }

  // member: provenance
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "provenance: ";
    rosidl_generator_traits::value_to_yaml(msg.provenance, out);
    out << "\n";
  }

  // member: provenance_note
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "provenance_note: ";
    rosidl_generator_traits::value_to_yaml(msg.provenance_note, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const RoverSpec & msg, bool use_flow_style = false)
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
  const space_msgs::msg::RoverSpec & msg,
  std::ostream & out, size_t indentation = 0)
{
  space_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use space_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const space_msgs::msg::RoverSpec & msg)
{
  return space_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<space_msgs::msg::RoverSpec>()
{
  return "space_msgs::msg::RoverSpec";
}

template<>
inline const char * name<space_msgs::msg::RoverSpec>()
{
  return "space_msgs/msg/RoverSpec";
}

template<>
struct has_fixed_size<space_msgs::msg::RoverSpec>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<space_msgs::msg::RoverSpec>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<space_msgs::msg::RoverSpec>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // SPACE_MSGS__MSG__DETAIL__ROVER_SPEC__TRAITS_HPP_
