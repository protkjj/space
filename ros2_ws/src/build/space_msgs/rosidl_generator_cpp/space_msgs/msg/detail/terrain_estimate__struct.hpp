// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from space_msgs:msg/TerrainEstimate.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "space_msgs/msg/terrain_estimate.hpp"


#ifndef SPACE_MSGS__MSG__DETAIL__TERRAIN_ESTIMATE__STRUCT_HPP_
#define SPACE_MSGS__MSG__DETAIL__TERRAIN_ESTIMATE__STRUCT_HPP_

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
// Member 'grid'
#include "grid_map_msgs/msg/detail/grid_map__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__space_msgs__msg__TerrainEstimate __attribute__((deprecated))
#else
# define DEPRECATED__space_msgs__msg__TerrainEstimate __declspec(deprecated)
#endif

namespace space_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct TerrainEstimate_
{
  using Type = TerrainEstimate_<ContainerAllocator>;

  explicit TerrainEstimate_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init),
    grid(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->soil_model_id = "";
      this->soil_model_version = "";
    }
  }

  explicit TerrainEstimate_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init),
    grid(_alloc, _init),
    soil_model_id(_alloc),
    soil_model_version(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->soil_model_id = "";
      this->soil_model_version = "";
    }
  }

  // field types and members
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;
  using _grid_type =
    grid_map_msgs::msg::GridMap_<ContainerAllocator>;
  _grid_type grid;
  using _soil_model_id_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _soil_model_id_type soil_model_id;
  using _soil_model_version_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _soil_model_version_type soil_model_version;

  // setters for named parameter idiom
  Type & set__header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->header = _arg;
    return *this;
  }
  Type & set__grid(
    const grid_map_msgs::msg::GridMap_<ContainerAllocator> & _arg)
  {
    this->grid = _arg;
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

  // constant declarations
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> LAYER_SLOPE;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> LAYER_ROUGHNESS;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> LAYER_STEP;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> LAYER_SLIP_SMALL;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> LAYER_SLIP_QUALITY;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> LAYER_SLIP_SAMPLES;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> LAYER_SOIL_DIFFICULTY;
  static const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> LAYER_SOIL_CONFIDENCE;

  // pointer types
  using RawPtr =
    space_msgs::msg::TerrainEstimate_<ContainerAllocator> *;
  using ConstRawPtr =
    const space_msgs::msg::TerrainEstimate_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<space_msgs::msg::TerrainEstimate_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<space_msgs::msg::TerrainEstimate_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      space_msgs::msg::TerrainEstimate_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<space_msgs::msg::TerrainEstimate_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      space_msgs::msg::TerrainEstimate_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<space_msgs::msg::TerrainEstimate_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<space_msgs::msg::TerrainEstimate_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<space_msgs::msg::TerrainEstimate_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__space_msgs__msg__TerrainEstimate
    std::shared_ptr<space_msgs::msg::TerrainEstimate_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__space_msgs__msg__TerrainEstimate
    std::shared_ptr<space_msgs::msg::TerrainEstimate_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const TerrainEstimate_ & other) const
  {
    if (this->header != other.header) {
      return false;
    }
    if (this->grid != other.grid) {
      return false;
    }
    if (this->soil_model_id != other.soil_model_id) {
      return false;
    }
    if (this->soil_model_version != other.soil_model_version) {
      return false;
    }
    return true;
  }
  bool operator!=(const TerrainEstimate_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct TerrainEstimate_

// alias to use template instance with default allocator
using TerrainEstimate =
  space_msgs::msg::TerrainEstimate_<std::allocator<void>>;

// constant definitions
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
TerrainEstimate_<ContainerAllocator>::LAYER_SLOPE = "slope_rad";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
TerrainEstimate_<ContainerAllocator>::LAYER_ROUGHNESS = "roughness_m";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
TerrainEstimate_<ContainerAllocator>::LAYER_STEP = "step_height_m";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
TerrainEstimate_<ContainerAllocator>::LAYER_SLIP_SMALL = "slip_small";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
TerrainEstimate_<ContainerAllocator>::LAYER_SLIP_QUALITY = "slip_quality";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
TerrainEstimate_<ContainerAllocator>::LAYER_SLIP_SAMPLES = "slip_samples";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
TerrainEstimate_<ContainerAllocator>::LAYER_SOIL_DIFFICULTY = "soil_difficulty";
template<typename ContainerAllocator>
const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>
TerrainEstimate_<ContainerAllocator>::LAYER_SOIL_CONFIDENCE = "soil_confidence";

}  // namespace msg

}  // namespace space_msgs

#endif  // SPACE_MSGS__MSG__DETAIL__TERRAIN_ESTIMATE__STRUCT_HPP_
