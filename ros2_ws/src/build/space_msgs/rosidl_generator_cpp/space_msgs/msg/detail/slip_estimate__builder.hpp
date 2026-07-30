// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from space_msgs:msg/SlipEstimate.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "space_msgs/msg/slip_estimate.hpp"


#ifndef SPACE_MSGS__MSG__DETAIL__SLIP_ESTIMATE__BUILDER_HPP_
#define SPACE_MSGS__MSG__DETAIL__SLIP_ESTIMATE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "space_msgs/msg/detail/slip_estimate__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace space_msgs
{

namespace msg
{

namespace builder
{

class Init_SlipEstimate_source
{
public:
  explicit Init_SlipEstimate_source(::space_msgs::msg::SlipEstimate & msg)
  : msg_(msg)
  {}
  ::space_msgs::msg::SlipEstimate source(::space_msgs::msg::SlipEstimate::_source_type arg)
  {
    msg_.source = std::move(arg);
    return std::move(msg_);
  }

private:
  ::space_msgs::msg::SlipEstimate msg_;
};

class Init_SlipEstimate_quality
{
public:
  explicit Init_SlipEstimate_quality(::space_msgs::msg::SlipEstimate & msg)
  : msg_(msg)
  {}
  Init_SlipEstimate_source quality(::space_msgs::msg::SlipEstimate::_quality_type arg)
  {
    msg_.quality = std::move(arg);
    return Init_SlipEstimate_source(msg_);
  }

private:
  ::space_msgs::msg::SlipEstimate msg_;
};

class Init_SlipEstimate_valid
{
public:
  explicit Init_SlipEstimate_valid(::space_msgs::msg::SlipEstimate & msg)
  : msg_(msg)
  {}
  Init_SlipEstimate_quality valid(::space_msgs::msg::SlipEstimate::_valid_type arg)
  {
    msg_.valid = std::move(arg);
    return Init_SlipEstimate_quality(msg_);
  }

private:
  ::space_msgs::msg::SlipEstimate msg_;
};

class Init_SlipEstimate_v_actual
{
public:
  explicit Init_SlipEstimate_v_actual(::space_msgs::msg::SlipEstimate & msg)
  : msg_(msg)
  {}
  Init_SlipEstimate_valid v_actual(::space_msgs::msg::SlipEstimate::_v_actual_type arg)
  {
    msg_.v_actual = std::move(arg);
    return Init_SlipEstimate_valid(msg_);
  }

private:
  ::space_msgs::msg::SlipEstimate msg_;
};

class Init_SlipEstimate_v_wheel
{
public:
  explicit Init_SlipEstimate_v_wheel(::space_msgs::msg::SlipEstimate & msg)
  : msg_(msg)
  {}
  Init_SlipEstimate_v_actual v_wheel(::space_msgs::msg::SlipEstimate::_v_wheel_type arg)
  {
    msg_.v_wheel = std::move(arg);
    return Init_SlipEstimate_v_actual(msg_);
  }

private:
  ::space_msgs::msg::SlipEstimate msg_;
};

class Init_SlipEstimate_slip_ratio
{
public:
  explicit Init_SlipEstimate_slip_ratio(::space_msgs::msg::SlipEstimate & msg)
  : msg_(msg)
  {}
  Init_SlipEstimate_v_wheel slip_ratio(::space_msgs::msg::SlipEstimate::_slip_ratio_type arg)
  {
    msg_.slip_ratio = std::move(arg);
    return Init_SlipEstimate_v_wheel(msg_);
  }

private:
  ::space_msgs::msg::SlipEstimate msg_;
};

class Init_SlipEstimate_header
{
public:
  Init_SlipEstimate_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_SlipEstimate_slip_ratio header(::space_msgs::msg::SlipEstimate::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_SlipEstimate_slip_ratio(msg_);
  }

private:
  ::space_msgs::msg::SlipEstimate msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::space_msgs::msg::SlipEstimate>()
{
  return space_msgs::msg::builder::Init_SlipEstimate_header();
}

}  // namespace space_msgs

#endif  // SPACE_MSGS__MSG__DETAIL__SLIP_ESTIMATE__BUILDER_HPP_
