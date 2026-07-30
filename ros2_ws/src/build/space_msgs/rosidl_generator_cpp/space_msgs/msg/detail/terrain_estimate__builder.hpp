// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from space_msgs:msg/TerrainEstimate.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "space_msgs/msg/terrain_estimate.hpp"


#ifndef SPACE_MSGS__MSG__DETAIL__TERRAIN_ESTIMATE__BUILDER_HPP_
#define SPACE_MSGS__MSG__DETAIL__TERRAIN_ESTIMATE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "space_msgs/msg/detail/terrain_estimate__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace space_msgs
{

namespace msg
{

namespace builder
{

class Init_TerrainEstimate_soil_model_version
{
public:
  explicit Init_TerrainEstimate_soil_model_version(::space_msgs::msg::TerrainEstimate & msg)
  : msg_(msg)
  {}
  ::space_msgs::msg::TerrainEstimate soil_model_version(::space_msgs::msg::TerrainEstimate::_soil_model_version_type arg)
  {
    msg_.soil_model_version = std::move(arg);
    return std::move(msg_);
  }

private:
  ::space_msgs::msg::TerrainEstimate msg_;
};

class Init_TerrainEstimate_soil_model_id
{
public:
  explicit Init_TerrainEstimate_soil_model_id(::space_msgs::msg::TerrainEstimate & msg)
  : msg_(msg)
  {}
  Init_TerrainEstimate_soil_model_version soil_model_id(::space_msgs::msg::TerrainEstimate::_soil_model_id_type arg)
  {
    msg_.soil_model_id = std::move(arg);
    return Init_TerrainEstimate_soil_model_version(msg_);
  }

private:
  ::space_msgs::msg::TerrainEstimate msg_;
};

class Init_TerrainEstimate_grid
{
public:
  explicit Init_TerrainEstimate_grid(::space_msgs::msg::TerrainEstimate & msg)
  : msg_(msg)
  {}
  Init_TerrainEstimate_soil_model_id grid(::space_msgs::msg::TerrainEstimate::_grid_type arg)
  {
    msg_.grid = std::move(arg);
    return Init_TerrainEstimate_soil_model_id(msg_);
  }

private:
  ::space_msgs::msg::TerrainEstimate msg_;
};

class Init_TerrainEstimate_header
{
public:
  Init_TerrainEstimate_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_TerrainEstimate_grid header(::space_msgs::msg::TerrainEstimate::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_TerrainEstimate_grid(msg_);
  }

private:
  ::space_msgs::msg::TerrainEstimate msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::space_msgs::msg::TerrainEstimate>()
{
  return space_msgs::msg::builder::Init_TerrainEstimate_header();
}

}  // namespace space_msgs

#endif  // SPACE_MSGS__MSG__DETAIL__TERRAIN_ESTIMATE__BUILDER_HPP_
