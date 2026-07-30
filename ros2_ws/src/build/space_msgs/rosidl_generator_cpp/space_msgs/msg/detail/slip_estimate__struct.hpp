// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from space_msgs:msg/SlipEstimate.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "space_msgs/msg/slip_estimate.hpp"


#ifndef SPACE_MSGS__MSG__DETAIL__SLIP_ESTIMATE__STRUCT_HPP_
#define SPACE_MSGS__MSG__DETAIL__SLIP_ESTIMATE__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__space_msgs__msg__SlipEstimate __attribute__((deprecated))
#else
# define DEPRECATED__space_msgs__msg__SlipEstimate __declspec(deprecated)
#endif

namespace space_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct SlipEstimate_
{
  using Type = SlipEstimate_<ContainerAllocator>;

  explicit SlipEstimate_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->slip_ratio = 0.0f;
      this->v_wheel = 0.0f;
      this->v_actual = 0.0f;
      this->valid = false;
      this->quality = 0.0f;
      this->source = 0;
    }
  }

  explicit SlipEstimate_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->slip_ratio = 0.0f;
      this->v_wheel = 0.0f;
      this->v_actual = 0.0f;
      this->valid = false;
      this->quality = 0.0f;
      this->source = 0;
    }
  }

  // field types and members
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;
  using _slip_ratio_type =
    float;
  _slip_ratio_type slip_ratio;
  using _v_wheel_type =
    float;
  _v_wheel_type v_wheel;
  using _v_actual_type =
    float;
  _v_actual_type v_actual;
  using _valid_type =
    bool;
  _valid_type valid;
  using _quality_type =
    float;
  _quality_type quality;
  using _source_type =
    uint8_t;
  _source_type source;

  // setters for named parameter idiom
  Type & set__header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->header = _arg;
    return *this;
  }
  Type & set__slip_ratio(
    const float & _arg)
  {
    this->slip_ratio = _arg;
    return *this;
  }
  Type & set__v_wheel(
    const float & _arg)
  {
    this->v_wheel = _arg;
    return *this;
  }
  Type & set__v_actual(
    const float & _arg)
  {
    this->v_actual = _arg;
    return *this;
  }
  Type & set__valid(
    const bool & _arg)
  {
    this->valid = _arg;
    return *this;
  }
  Type & set__quality(
    const float & _arg)
  {
    this->quality = _arg;
    return *this;
  }
  Type & set__source(
    const uint8_t & _arg)
  {
    this->source = _arg;
    return *this;
  }

  // constant declarations
  static constexpr uint8_t SOURCE_UNKNOWN =
    0u;
  static constexpr uint8_t SOURCE_SIM_GROUND_TRUTH =
    1u;
  static constexpr uint8_t SOURCE_VIO =
    2u;
  static constexpr uint8_t SOURCE_EKF =
    3u;

  // pointer types
  using RawPtr =
    space_msgs::msg::SlipEstimate_<ContainerAllocator> *;
  using ConstRawPtr =
    const space_msgs::msg::SlipEstimate_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<space_msgs::msg::SlipEstimate_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<space_msgs::msg::SlipEstimate_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      space_msgs::msg::SlipEstimate_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<space_msgs::msg::SlipEstimate_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      space_msgs::msg::SlipEstimate_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<space_msgs::msg::SlipEstimate_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<space_msgs::msg::SlipEstimate_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<space_msgs::msg::SlipEstimate_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__space_msgs__msg__SlipEstimate
    std::shared_ptr<space_msgs::msg::SlipEstimate_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__space_msgs__msg__SlipEstimate
    std::shared_ptr<space_msgs::msg::SlipEstimate_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const SlipEstimate_ & other) const
  {
    if (this->header != other.header) {
      return false;
    }
    if (this->slip_ratio != other.slip_ratio) {
      return false;
    }
    if (this->v_wheel != other.v_wheel) {
      return false;
    }
    if (this->v_actual != other.v_actual) {
      return false;
    }
    if (this->valid != other.valid) {
      return false;
    }
    if (this->quality != other.quality) {
      return false;
    }
    if (this->source != other.source) {
      return false;
    }
    return true;
  }
  bool operator!=(const SlipEstimate_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct SlipEstimate_

// alias to use template instance with default allocator
using SlipEstimate =
  space_msgs::msg::SlipEstimate_<std::allocator<void>>;

// constant definitions
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t SlipEstimate_<ContainerAllocator>::SOURCE_UNKNOWN;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t SlipEstimate_<ContainerAllocator>::SOURCE_SIM_GROUND_TRUTH;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t SlipEstimate_<ContainerAllocator>::SOURCE_VIO;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t SlipEstimate_<ContainerAllocator>::SOURCE_EKF;
#endif  // __cplusplus < 201703L

}  // namespace msg

}  // namespace space_msgs

#endif  // SPACE_MSGS__MSG__DETAIL__SLIP_ESTIMATE__STRUCT_HPP_
