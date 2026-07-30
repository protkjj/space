// generated from rosidl_typesupport_introspection_cpp/resource/idl__type_support.cpp.em
// with input from space_msgs:msg/TerrainEstimate.idl
// generated code does not contain a copyright notice

#include "array"
#include "cstddef"
#include "string"
#include "vector"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_interface/macros.h"
#include "space_msgs/msg/detail/terrain_estimate__functions.h"
#include "space_msgs/msg/detail/terrain_estimate__struct.hpp"
#include "rosidl_typesupport_introspection_cpp/field_types.hpp"
#include "rosidl_typesupport_introspection_cpp/identifier.hpp"
#include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
#include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace space_msgs
{

namespace msg
{

namespace rosidl_typesupport_introspection_cpp
{

void TerrainEstimate_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) space_msgs::msg::TerrainEstimate(_init);
}

void TerrainEstimate_fini_function(void * message_memory)
{
  auto typed_message = static_cast<space_msgs::msg::TerrainEstimate *>(message_memory);
  typed_message->~TerrainEstimate();
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember TerrainEstimate_message_member_array[4] = {
  {
    "header",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<std_msgs::msg::Header>(),  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(space_msgs::msg::TerrainEstimate, header),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "grid",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<grid_map_msgs::msg::GridMap>(),  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(space_msgs::msg::TerrainEstimate, grid),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "soil_model_id",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(space_msgs::msg::TerrainEstimate, soil_model_id),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "soil_model_version",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(space_msgs::msg::TerrainEstimate, soil_model_version),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers TerrainEstimate_message_members = {
  "space_msgs::msg",  // message namespace
  "TerrainEstimate",  // message name
  4,  // number of fields
  sizeof(space_msgs::msg::TerrainEstimate),
  false,  // has_any_key_member_
  TerrainEstimate_message_member_array,  // message members
  TerrainEstimate_init_function,  // function to initialize message memory (memory has to be allocated)
  TerrainEstimate_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t TerrainEstimate_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &TerrainEstimate_message_members,
  get_message_typesupport_handle_function,
  &space_msgs__msg__TerrainEstimate__get_type_hash,
  &space_msgs__msg__TerrainEstimate__get_type_description,
  &space_msgs__msg__TerrainEstimate__get_type_description_sources,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace msg

}  // namespace space_msgs


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<space_msgs::msg::TerrainEstimate>()
{
  return &::space_msgs::msg::rosidl_typesupport_introspection_cpp::TerrainEstimate_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, space_msgs, msg, TerrainEstimate)() {
  return &::space_msgs::msg::rosidl_typesupport_introspection_cpp::TerrainEstimate_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif
