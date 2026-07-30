// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from space_msgs:msg/RoverSpec.idl
// generated code does not contain a copyright notice

// IWYU pragma: private, include "space_msgs/msg/rover_spec.hpp"


#ifndef SPACE_MSGS__MSG__DETAIL__ROVER_SPEC__STRUCT_HPP_
#define SPACE_MSGS__MSG__DETAIL__ROVER_SPEC__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__space_msgs__msg__RoverSpec __attribute__((deprecated))
#else
# define DEPRECATED__space_msgs__msg__RoverSpec __declspec(deprecated)
#endif

namespace space_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct RoverSpec_
{
  using Type = RoverSpec_<ContainerAllocator>;

  explicit RoverSpec_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->rover_id = "";
      this->mass_kg = 0.0f;
      this->wheel_radius_m = 0.0f;
      this->wheel_width_m = 0.0f;
      this->ground_pressure_kpa = 0.0f;
      this->max_climb_angle_rad = 0.0f;
      this->min_passable_width_m = 0.0f;
      this->ground_clearance_m = 0.0f;
      this->has_grousers = false;
      this->provenance = 0;
      this->provenance_note = "";
    }
  }

  explicit RoverSpec_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : rover_id(_alloc),
    provenance_note(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->rover_id = "";
      this->mass_kg = 0.0f;
      this->wheel_radius_m = 0.0f;
      this->wheel_width_m = 0.0f;
      this->ground_pressure_kpa = 0.0f;
      this->max_climb_angle_rad = 0.0f;
      this->min_passable_width_m = 0.0f;
      this->ground_clearance_m = 0.0f;
      this->has_grousers = false;
      this->provenance = 0;
      this->provenance_note = "";
    }
  }

  // field types and members
  using _rover_id_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _rover_id_type rover_id;
  using _mass_kg_type =
    float;
  _mass_kg_type mass_kg;
  using _wheel_radius_m_type =
    float;
  _wheel_radius_m_type wheel_radius_m;
  using _wheel_width_m_type =
    float;
  _wheel_width_m_type wheel_width_m;
  using _ground_pressure_kpa_type =
    float;
  _ground_pressure_kpa_type ground_pressure_kpa;
  using _max_climb_angle_rad_type =
    float;
  _max_climb_angle_rad_type max_climb_angle_rad;
  using _min_passable_width_m_type =
    float;
  _min_passable_width_m_type min_passable_width_m;
  using _ground_clearance_m_type =
    float;
  _ground_clearance_m_type ground_clearance_m;
  using _has_grousers_type =
    bool;
  _has_grousers_type has_grousers;
  using _provenance_type =
    uint8_t;
  _provenance_type provenance;
  using _provenance_note_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _provenance_note_type provenance_note;

  // setters for named parameter idiom
  Type & set__rover_id(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->rover_id = _arg;
    return *this;
  }
  Type & set__mass_kg(
    const float & _arg)
  {
    this->mass_kg = _arg;
    return *this;
  }
  Type & set__wheel_radius_m(
    const float & _arg)
  {
    this->wheel_radius_m = _arg;
    return *this;
  }
  Type & set__wheel_width_m(
    const float & _arg)
  {
    this->wheel_width_m = _arg;
    return *this;
  }
  Type & set__ground_pressure_kpa(
    const float & _arg)
  {
    this->ground_pressure_kpa = _arg;
    return *this;
  }
  Type & set__max_climb_angle_rad(
    const float & _arg)
  {
    this->max_climb_angle_rad = _arg;
    return *this;
  }
  Type & set__min_passable_width_m(
    const float & _arg)
  {
    this->min_passable_width_m = _arg;
    return *this;
  }
  Type & set__ground_clearance_m(
    const float & _arg)
  {
    this->ground_clearance_m = _arg;
    return *this;
  }
  Type & set__has_grousers(
    const bool & _arg)
  {
    this->has_grousers = _arg;
    return *this;
  }
  Type & set__provenance(
    const uint8_t & _arg)
  {
    this->provenance = _arg;
    return *this;
  }
  Type & set__provenance_note(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->provenance_note = _arg;
    return *this;
  }

  // constant declarations
  static constexpr uint8_t PROVENANCE_UNKNOWN =
    0u;
  static constexpr uint8_t PROVENANCE_MEASURED =
    1u;
  static constexpr uint8_t PROVENANCE_ASSUMED =
    2u;

  // pointer types
  using RawPtr =
    space_msgs::msg::RoverSpec_<ContainerAllocator> *;
  using ConstRawPtr =
    const space_msgs::msg::RoverSpec_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<space_msgs::msg::RoverSpec_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<space_msgs::msg::RoverSpec_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      space_msgs::msg::RoverSpec_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<space_msgs::msg::RoverSpec_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      space_msgs::msg::RoverSpec_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<space_msgs::msg::RoverSpec_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<space_msgs::msg::RoverSpec_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<space_msgs::msg::RoverSpec_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__space_msgs__msg__RoverSpec
    std::shared_ptr<space_msgs::msg::RoverSpec_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__space_msgs__msg__RoverSpec
    std::shared_ptr<space_msgs::msg::RoverSpec_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const RoverSpec_ & other) const
  {
    if (this->rover_id != other.rover_id) {
      return false;
    }
    if (this->mass_kg != other.mass_kg) {
      return false;
    }
    if (this->wheel_radius_m != other.wheel_radius_m) {
      return false;
    }
    if (this->wheel_width_m != other.wheel_width_m) {
      return false;
    }
    if (this->ground_pressure_kpa != other.ground_pressure_kpa) {
      return false;
    }
    if (this->max_climb_angle_rad != other.max_climb_angle_rad) {
      return false;
    }
    if (this->min_passable_width_m != other.min_passable_width_m) {
      return false;
    }
    if (this->ground_clearance_m != other.ground_clearance_m) {
      return false;
    }
    if (this->has_grousers != other.has_grousers) {
      return false;
    }
    if (this->provenance != other.provenance) {
      return false;
    }
    if (this->provenance_note != other.provenance_note) {
      return false;
    }
    return true;
  }
  bool operator!=(const RoverSpec_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct RoverSpec_

// alias to use template instance with default allocator
using RoverSpec =
  space_msgs::msg::RoverSpec_<std::allocator<void>>;

// constant definitions
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t RoverSpec_<ContainerAllocator>::PROVENANCE_UNKNOWN;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t RoverSpec_<ContainerAllocator>::PROVENANCE_MEASURED;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t RoverSpec_<ContainerAllocator>::PROVENANCE_ASSUMED;
#endif  // __cplusplus < 201703L

}  // namespace msg

}  // namespace space_msgs

#endif  // SPACE_MSGS__MSG__DETAIL__ROVER_SPEC__STRUCT_HPP_
