// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from space_msgs:msg/TraversabilityScore.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "space_msgs/msg/traversability_score.hpp"


#ifndef SPACE_MSGS__MSG__DETAIL__TRAVERSABILITY_SCORE__BUILDER_HPP_
#define SPACE_MSGS__MSG__DETAIL__TRAVERSABILITY_SCORE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "space_msgs/msg/detail/traversability_score__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace space_msgs
{

namespace msg
{

namespace builder
{

class Init_TraversabilityScore_evaluator_version
{
public:
  explicit Init_TraversabilityScore_evaluator_version(::space_msgs::msg::TraversabilityScore & msg)
  : msg_(msg)
  {}
  ::space_msgs::msg::TraversabilityScore evaluator_version(::space_msgs::msg::TraversabilityScore::_evaluator_version_type arg)
  {
    msg_.evaluator_version = std::move(arg);
    return std::move(msg_);
  }

private:
  ::space_msgs::msg::TraversabilityScore msg_;
};

class Init_TraversabilityScore_soil_model_version
{
public:
  explicit Init_TraversabilityScore_soil_model_version(::space_msgs::msg::TraversabilityScore & msg)
  : msg_(msg)
  {}
  Init_TraversabilityScore_evaluator_version soil_model_version(::space_msgs::msg::TraversabilityScore::_soil_model_version_type arg)
  {
    msg_.soil_model_version = std::move(arg);
    return Init_TraversabilityScore_evaluator_version(msg_);
  }

private:
  ::space_msgs::msg::TraversabilityScore msg_;
};

class Init_TraversabilityScore_soil_model_id
{
public:
  explicit Init_TraversabilityScore_soil_model_id(::space_msgs::msg::TraversabilityScore & msg)
  : msg_(msg)
  {}
  Init_TraversabilityScore_soil_model_version soil_model_id(::space_msgs::msg::TraversabilityScore::_soil_model_id_type arg)
  {
    msg_.soil_model_id = std::move(arg);
    return Init_TraversabilityScore_soil_model_version(msg_);
  }

private:
  ::space_msgs::msg::TraversabilityScore msg_;
};

class Init_TraversabilityScore_terrain_stamp
{
public:
  explicit Init_TraversabilityScore_terrain_stamp(::space_msgs::msg::TraversabilityScore & msg)
  : msg_(msg)
  {}
  Init_TraversabilityScore_soil_model_id terrain_stamp(::space_msgs::msg::TraversabilityScore::_terrain_stamp_type arg)
  {
    msg_.terrain_stamp = std::move(arg);
    return Init_TraversabilityScore_soil_model_id(msg_);
  }

private:
  ::space_msgs::msg::TraversabilityScore msg_;
};

class Init_TraversabilityScore_grid
{
public:
  explicit Init_TraversabilityScore_grid(::space_msgs::msg::TraversabilityScore & msg)
  : msg_(msg)
  {}
  Init_TraversabilityScore_terrain_stamp grid(::space_msgs::msg::TraversabilityScore::_grid_type arg)
  {
    msg_.grid = std::move(arg);
    return Init_TraversabilityScore_terrain_stamp(msg_);
  }

private:
  ::space_msgs::msg::TraversabilityScore msg_;
};

class Init_TraversabilityScore_rover_spec
{
public:
  explicit Init_TraversabilityScore_rover_spec(::space_msgs::msg::TraversabilityScore & msg)
  : msg_(msg)
  {}
  Init_TraversabilityScore_grid rover_spec(::space_msgs::msg::TraversabilityScore::_rover_spec_type arg)
  {
    msg_.rover_spec = std::move(arg);
    return Init_TraversabilityScore_grid(msg_);
  }

private:
  ::space_msgs::msg::TraversabilityScore msg_;
};

class Init_TraversabilityScore_rover_id
{
public:
  explicit Init_TraversabilityScore_rover_id(::space_msgs::msg::TraversabilityScore & msg)
  : msg_(msg)
  {}
  Init_TraversabilityScore_rover_spec rover_id(::space_msgs::msg::TraversabilityScore::_rover_id_type arg)
  {
    msg_.rover_id = std::move(arg);
    return Init_TraversabilityScore_rover_spec(msg_);
  }

private:
  ::space_msgs::msg::TraversabilityScore msg_;
};

class Init_TraversabilityScore_header
{
public:
  Init_TraversabilityScore_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_TraversabilityScore_rover_id header(::space_msgs::msg::TraversabilityScore::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_TraversabilityScore_rover_id(msg_);
  }

private:
  ::space_msgs::msg::TraversabilityScore msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::space_msgs::msg::TraversabilityScore>()
{
  return space_msgs::msg::builder::Init_TraversabilityScore_header();
}

}  // namespace space_msgs

#endif  // SPACE_MSGS__MSG__DETAIL__TRAVERSABILITY_SCORE__BUILDER_HPP_
