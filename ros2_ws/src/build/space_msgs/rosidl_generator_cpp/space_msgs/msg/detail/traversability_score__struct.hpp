// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from space_msgs:msg/TraversabilityScore.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "space_msgs/msg/traversability_score.hpp"


#ifndef SPACE_MSGS__MSG__DETAIL__TRAVERSABILITY_SCORE__STRUCT_HPP_
#define SPACE_MSGS__MSG__DETAIL__TRAVERSABILITY_SCORE__STRUCT_HPP_

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
// Member 'rover_spec'
#include "space_msgs/msg/detail/rover_spec__struct.hpp"
// Member 'grid'
#include "grid_map_msgs/msg/detail/grid_map__struct.hpp"
// Member 'terrain_stamp'
#include "builtin_interfaces/msg/detail/time__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__space_msgs__msg__TraversabilityScore __attribute__((deprecated))
#else
# define DEPRECATED__space_msgs__msg__TraversabilityScore __declspec(deprecated)
#endif

namespace space_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct TraversabilityScore_
{
  using Type = TraversabilityScore_<ContainerAllocator>;

  explicit TraversabilityScore_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init),
    rover_spec(_init),
    grid(_init),
    terrain_stamp(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->rover_id = "";
      this->soil_model_id = "";
      this->soil_model_version = "";
      this->evaluator_version = "";
    }
  }

  explicit TraversabilityScore_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init),
    rover_id(_alloc),
    rover_spec(_alloc, _init),
    grid(_alloc, _init),
    terrain_stamp(_alloc, _init),
    soil_model_id(_alloc),
    soil_model_version(_alloc),
    evaluator_version(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->rover_id = "";
      this->soil_model_id = "";
      this->soil_model_version = "";
      this->evaluator_version = "";
    }
  }

  // field types and members
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;
  using _rover_id_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _rover_id_type rover_id;
  using _rover_spec_type =
    space_msgs::msg::RoverSpec_<ContainerAllocator>;
  _rover_spec_type rover_spec;
  using _grid_type =
    grid_map_msgs::msg::GridMap_<ContainerAllocator>;
  _grid_type grid;
  using _terrain_stamp_type =
    builtin_interfaces::msg::Time_<ContainerAllocator>;
  _terrain_stamp_type terrain_stamp;
  using _soil_model_id_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _soil_model_id_type soil_model_id;
  using _soil_model_version_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _soil_model_version_type soil_model_version;
  using _evaluator_version_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _evaluator_version_type evaluator_version;

  // setters for named parameter idiom
  Type & set__header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->header = _arg;
    return *this;
  }
  Type & set__rover_id(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->rover_id = _arg;
    return *this;
  }
  Type & set__rover_spec(
    const space_msgs::msg::RoverSpec_<ContainerAllocator> & _arg)
  {
    this->rover_spec = _arg;
    return *this;
  }
  Type & set__grid(
    const grid_map_msgs::msg::GridMap_<ContainerAllocator> & _arg)
  {
    this->grid = _arg;
    return *this;
  }
  Type & set__terrain_stamp(
    const builtin_interfaces::msg::Time_<ContainerAllocator> & _arg)
  {
    this->terrain_stamp = _arg;
    return *this;
  }
  Type & set__soil_model_id(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->soil_model_id = _arg;
    return *this;
  }
  Type & set__soil_model_version(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->soil_model_version = _arg;
    return *this;
  }
  Type & set__evaluator_version(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->evaluator_version = _arg;
    return *this;
  }

  // constant declarations
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> LAYER_SCORE;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> LAYER_LIMITING_FACTOR;
  static constexpr uint8_t LIMIT_NONE =
    0u;
  static constexpr uint8_t LIMIT_SLOPE =
    1u;
  static constexpr uint8_t LIMIT_ROUGHNESS =
    2u;
  static constexpr uint8_t LIMIT_STEP =
    3u;
  static constexpr uint8_t LIMIT_SOIL =
    4u;
  static constexpr uint8_t LIMIT_CLEARANCE =
    5u;
  static constexpr uint8_t LIMIT_WIDTH =
    6u;
  static constexpr uint8_t LIMIT_NO_DATA =
    7u;

  // pointer types
  using RawPtr =
    space_msgs::msg::TraversabilityScore_<ContainerAllocator> *;
  using ConstRawPtr =
    const space_msgs::msg::TraversabilityScore_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<space_msgs::msg::TraversabilityScore_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<space_msgs::msg::TraversabilityScore_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      space_msgs::msg::TraversabilityScore_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<space_msgs::msg::TraversabilityScore_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      space_msgs::msg::TraversabilityScore_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<space_msgs::msg::TraversabilityScore_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<space_msgs::msg::TraversabilityScore_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<space_msgs::msg::TraversabilityScore_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__space_msgs__msg__TraversabilityScore
    std::shared_ptr<space_msgs::msg::TraversabilityScore_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__space_msgs__msg__TraversabilityScore
    std::shared_ptr<space_msgs::msg::TraversabilityScore_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const TraversabilityScore_ & other) const
  {
    if (this->header != other.header) {
      return false;
    }
    if (this->rover_id != other.rover_id) {
      return false;
    }
    if (this->rover_spec != other.rover_spec) {
      return false;
    }
    if (this->grid != other.grid) {
      return false;
    }
    if (this->terrain_stamp != other.terrain_stamp) {
      return false;
    }
    if (this->soil_model_id != other.soil_model_id) {
      return false;
    }
    if (this->soil_model_version != other.soil_model_version) {
      return false;
    }
    if (this->evaluator_version != other.evaluator_version) {
      return false;
    }
    return true;
  }
  bool operator!=(const TraversabilityScore_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct TraversabilityScore_

// alias to use template instance with default allocator
using TraversabilityScore =
  space_msgs::msg::TraversabilityScore_<std::allocator<void>>;

// constant definitions
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
TraversabilityScore_<ContainerAllocator>::LAYER_SCORE = "score";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
TraversabilityScore_<ContainerAllocator>::LAYER_LIMITING_FACTOR = "limiting_factor";
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t TraversabilityScore_<ContainerAllocator>::LIMIT_NONE;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t TraversabilityScore_<ContainerAllocator>::LIMIT_SLOPE;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t TraversabilityScore_<ContainerAllocator>::LIMIT_ROUGHNESS;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t TraversabilityScore_<ContainerAllocator>::LIMIT_STEP;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t TraversabilityScore_<ContainerAllocator>::LIMIT_SOIL;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t TraversabilityScore_<ContainerAllocator>::LIMIT_CLEARANCE;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t TraversabilityScore_<ContainerAllocator>::LIMIT_WIDTH;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t TraversabilityScore_<ContainerAllocator>::LIMIT_NO_DATA;
#endif  // __cplusplus < 201703L

}  // namespace msg

}  // namespace space_msgs

#endif  // SPACE_MSGS__MSG__DETAIL__TRAVERSABILITY_SCORE__STRUCT_HPP_
