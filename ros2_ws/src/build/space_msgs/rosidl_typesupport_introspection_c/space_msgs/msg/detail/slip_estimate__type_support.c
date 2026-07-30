// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from space_msgs:msg/SlipEstimate.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "space_msgs/msg/detail/slip_estimate__rosidl_typesupport_introspection_c.h"
#include "space_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "space_msgs/msg/detail/slip_estimate__functions.h"
#include "space_msgs/msg/detail/slip_estimate__struct.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/header.h"
// Member `header`
#include "std_msgs/msg/detail/header__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void space_msgs__msg__SlipEstimate__rosidl_typesupport_introspection_c__SlipEstimate_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  space_msgs__msg__SlipEstimate__init(message_memory);
}

void space_msgs__msg__SlipEstimate__rosidl_typesupport_introspection_c__SlipEstimate_fini_function(void * message_memory)
{
  space_msgs__msg__SlipEstimate__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember space_msgs__msg__SlipEstimate__rosidl_typesupport_introspection_c__SlipEstimate_message_member_array[7] = {
  {
    "header",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(space_msgs__msg__SlipEstimate, header),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "slip_ratio",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(space_msgs__msg__SlipEstimate, slip_ratio),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "v_wheel",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(space_msgs__msg__SlipEstimate, v_wheel),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "v_actual",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(space_msgs__msg__SlipEstimate, v_actual),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "valid",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_BOOLEAN,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(space_msgs__msg__SlipEstimate, valid),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "quality",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(space_msgs__msg__SlipEstimate, quality),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "source",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is key
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(space_msgs__msg__SlipEstimate, source),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers space_msgs__msg__SlipEstimate__rosidl_typesupport_introspection_c__SlipEstimate_message_members = {
  "space_msgs__msg",  // message namespace
  "SlipEstimate",  // message name
  7,  // number of fields
  sizeof(space_msgs__msg__SlipEstimate),
  false,  // has_any_key_member_
  space_msgs__msg__SlipEstimate__rosidl_typesupport_introspection_c__SlipEstimate_message_member_array,  // message members
  space_msgs__msg__SlipEstimate__rosidl_typesupport_introspection_c__SlipEstimate_init_function,  // function to initialize message memory (memory has to be allocated)
  space_msgs__msg__SlipEstimate__rosidl_typesupport_introspection_c__SlipEstimate_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t space_msgs__msg__SlipEstimate__rosidl_typesupport_introspection_c__SlipEstimate_message_type_support_handle = {
  0,
  &space_msgs__msg__SlipEstimate__rosidl_typesupport_introspection_c__SlipEstimate_message_members,
  get_message_typesupport_handle_function,
  &space_msgs__msg__SlipEstimate__get_type_hash,
  &space_msgs__msg__SlipEstimate__get_type_description,
  &space_msgs__msg__SlipEstimate__get_type_description_sources,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_space_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, space_msgs, msg, SlipEstimate)() {
  space_msgs__msg__SlipEstimate__rosidl_typesupport_introspection_c__SlipEstimate_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, std_msgs, msg, Header)();
  if (!space_msgs__msg__SlipEstimate__rosidl_typesupport_introspection_c__SlipEstimate_message_type_support_handle.typesupport_identifier) {
    space_msgs__msg__SlipEstimate__rosidl_typesupport_introspection_c__SlipEstimate_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &space_msgs__msg__SlipEstimate__rosidl_typesupport_introspection_c__SlipEstimate_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
