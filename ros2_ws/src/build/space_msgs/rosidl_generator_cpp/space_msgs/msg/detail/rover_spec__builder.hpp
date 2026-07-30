// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from space_msgs:msg/RoverSpec.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "space_msgs/msg/rover_spec.hpp"


#ifndef SPACE_MSGS__MSG__DETAIL__ROVER_SPEC__BUILDER_HPP_
#define SPACE_MSGS__MSG__DETAIL__ROVER_SPEC__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "space_msgs/msg/detail/rover_spec__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace space_msgs
{

namespace msg
{

namespace builder
{

class Init_RoverSpec_provenance_note
{
public:
  explicit Init_RoverSpec_provenance_note(::space_msgs::msg::RoverSpec & msg)
  : msg_(msg)
  {}
  ::space_msgs::msg::RoverSpec provenance_note(::space_msgs::msg::RoverSpec::_provenance_note_type arg)
  {
    msg_.provenance_note = std::move(arg);
    return std::move(msg_);
  }

private:
  ::space_msgs::msg::RoverSpec msg_;
};

class Init_RoverSpec_provenance
{
public:
  explicit Init_RoverSpec_provenance(::space_msgs::msg::RoverSpec & msg)
  : msg_(msg)
  {}
  Init_RoverSpec_provenance_note provenance(::space_msgs::msg::RoverSpec::_provenance_type arg)
  {
    msg_.provenance = std::move(arg);
    return Init_RoverSpec_provenance_note(msg_);
  }

private:
  ::space_msgs::msg::RoverSpec msg_;
};

class Init_RoverSpec_has_grousers
{
public:
  explicit Init_RoverSpec_has_grousers(::space_msgs::msg::RoverSpec & msg)
  : msg_(msg)
  {}
  Init_RoverSpec_provenance has_grousers(::space_msgs::msg::RoverSpec::_has_grousers_type arg)
  {
    msg_.has_grousers = std::move(arg);
    return Init_RoverSpec_provenance(msg_);
  }

private:
  ::space_msgs::msg::RoverSpec msg_;
};

class Init_RoverSpec_ground_clearance_m
{
public:
  explicit Init_RoverSpec_ground_clearance_m(::space_msgs::msg::RoverSpec & msg)
  : msg_(msg)
  {}
  Init_RoverSpec_has_grousers ground_clearance_m(::space_msgs::msg::RoverSpec::_ground_clearance_m_type arg)
  {
    msg_.ground_clearance_m = std::move(arg);
    return Init_RoverSpec_has_grousers(msg_);
  }

private:
  ::space_msgs::msg::RoverSpec msg_;
};

class Init_RoverSpec_min_passable_width_m
{
public:
  explicit Init_RoverSpec_min_passable_width_m(::space_msgs::msg::RoverSpec & msg)
  : msg_(msg)
  {}
  Init_RoverSpec_ground_clearance_m min_passable_width_m(::space_msgs::msg::RoverSpec::_min_passable_width_m_type arg)
  {
    msg_.min_passable_width_m = std::move(arg);
    return Init_RoverSpec_ground_clearance_m(msg_);
  }

private:
  ::space_msgs::msg::RoverSpec msg_;
};

class Init_RoverSpec_max_climb_angle_rad
{
public:
  explicit Init_RoverSpec_max_climb_angle_rad(::space_msgs::msg::RoverSpec & msg)
  : msg_(msg)
  {}
  Init_RoverSpec_min_passable_width_m max_climb_angle_rad(::space_msgs::msg::RoverSpec::_max_climb_angle_rad_type arg)
  {
    msg_.max_climb_angle_rad = std::move(arg);
    return Init_RoverSpec_min_passable_width_m(msg_);
  }

private:
  ::space_msgs::msg::RoverSpec msg_;
};

class Init_RoverSpec_ground_pressure_kpa
{
public:
  explicit Init_RoverSpec_ground_pressure_kpa(::space_msgs::msg::RoverSpec & msg)
  : msg_(msg)
  {}
  Init_RoverSpec_max_climb_angle_rad ground_pressure_kpa(::space_msgs::msg::RoverSpec::_ground_pressure_kpa_type arg)
  {
    msg_.ground_pressure_kpa = std::move(arg);
    return Init_RoverSpec_max_climb_angle_rad(msg_);
  }

private:
  ::space_msgs::msg::RoverSpec msg_;
};

class Init_RoverSpec_wheel_width_m
{
public:
  explicit Init_RoverSpec_wheel_width_m(::space_msgs::msg::RoverSpec & msg)
  : msg_(msg)
  {}
  Init_RoverSpec_ground_pressure_kpa wheel_width_m(::space_msgs::msg::RoverSpec::_wheel_width_m_type arg)
  {
    msg_.wheel_width_m = std::move(arg);
    return Init_RoverSpec_ground_pressure_kpa(msg_);
  }

private:
  ::space_msgs::msg::RoverSpec msg_;
};

class Init_RoverSpec_wheel_radius_m
{
public:
  explicit Init_RoverSpec_wheel_radius_m(::space_msgs::msg::RoverSpec & msg)
  : msg_(msg)
  {}
  Init_RoverSpec_wheel_width_m wheel_radius_m(::space_msgs::msg::RoverSpec::_wheel_radius_m_type arg)
  {
    msg_.wheel_radius_m = std::move(arg);
    return Init_RoverSpec_wheel_width_m(msg_);
  }

private:
  ::space_msgs::msg::RoverSpec msg_;
};

class Init_RoverSpec_mass_kg
{
public:
  explicit Init_RoverSpec_mass_kg(::space_msgs::msg::RoverSpec & msg)
  : msg_(msg)
  {}
  Init_RoverSpec_wheel_radius_m mass_kg(::space_msgs::msg::RoverSpec::_mass_kg_type arg)
  {
    msg_.mass_kg = std::move(arg);
    return Init_RoverSpec_wheel_radius_m(msg_);
  }

private:
  ::space_msgs::msg::RoverSpec msg_;
};

class Init_RoverSpec_rover_id
{
public:
  Init_RoverSpec_rover_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_RoverSpec_mass_kg rover_id(::space_msgs::msg::RoverSpec::_rover_id_type arg)
  {
    msg_.rover_id = std::move(arg);
    return Init_RoverSpec_mass_kg(msg_);
  }

private:
  ::space_msgs::msg::RoverSpec msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::space_msgs::msg::RoverSpec>()
{
  return space_msgs::msg::builder::Init_RoverSpec_rover_id();
}

}  // namespace space_msgs

#endif  // SPACE_MSGS__MSG__DETAIL__ROVER_SPEC__BUILDER_HPP_
