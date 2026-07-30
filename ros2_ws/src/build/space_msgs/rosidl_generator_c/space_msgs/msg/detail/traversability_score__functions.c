// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from space_msgs:msg/TraversabilityScore.idl
// generated code does not contain a copyright notice
#include "space_msgs/msg/detail/traversability_score__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/detail/header__functions.h"
// Member `rover_id`
// Member `soil_model_id`
// Member `soil_model_version`
// Member `evaluator_version`
#include "rosidl_runtime_c/string_functions.h"
// Member `rover_spec`
#include "space_msgs/msg/detail/rover_spec__functions.h"
// Member `grid`
#include "grid_map_msgs/msg/detail/grid_map__functions.h"
// Member `terrain_stamp`
#include "builtin_interfaces/msg/detail/time__functions.h"

bool
space_msgs__msg__TraversabilityScore__init(space_msgs__msg__TraversabilityScore * msg)
{
  if (!msg) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__init(&msg->header)) {
    space_msgs__msg__TraversabilityScore__fini(msg);
    return false;
  }
  // rover_id
  if (!rosidl_runtime_c__String__init(&msg->rover_id)) {
    space_msgs__msg__TraversabilityScore__fini(msg);
    return false;
  }
  // rover_spec
  if (!space_msgs__msg__RoverSpec__init(&msg->rover_spec)) {
    space_msgs__msg__TraversabilityScore__fini(msg);
    return false;
  }
  // grid
  if (!grid_map_msgs__msg__GridMap__init(&msg->grid)) {
    space_msgs__msg__TraversabilityScore__fini(msg);
    return false;
  }
  // terrain_stamp
  if (!builtin_interfaces__msg__Time__init(&msg->terrain_stamp)) {
    space_msgs__msg__TraversabilityScore__fini(msg);
    return false;
  }
  // soil_model_id
  if (!rosidl_runtime_c__String__init(&msg->soil_model_id)) {
    space_msgs__msg__TraversabilityScore__fini(msg);
    return false;
  }
  // soil_model_version
  if (!rosidl_runtime_c__String__init(&msg->soil_model_version)) {
    space_msgs__msg__TraversabilityScore__fini(msg);
    return false;
  }
  // evaluator_version
  if (!rosidl_runtime_c__String__init(&msg->evaluator_version)) {
    space_msgs__msg__TraversabilityScore__fini(msg);
    return false;
  }
  return true;
}

void
space_msgs__msg__TraversabilityScore__fini(space_msgs__msg__TraversabilityScore * msg)
{
  if (!msg) {
    return;
  }
  // header
  std_msgs__msg__Header__fini(&msg->header);
  // rover_id
  rosidl_runtime_c__String__fini(&msg->rover_id);
  // rover_spec
  space_msgs__msg__RoverSpec__fini(&msg->rover_spec);
  // grid
  grid_map_msgs__msg__GridMap__fini(&msg->grid);
  // terrain_stamp
  builtin_interfaces__msg__Time__fini(&msg->terrain_stamp);
  // soil_model_id
  rosidl_runtime_c__String__fini(&msg->soil_model_id);
  // soil_model_version
  rosidl_runtime_c__String__fini(&msg->soil_model_version);
  // evaluator_version
  rosidl_runtime_c__String__fini(&msg->evaluator_version);
}

bool
space_msgs__msg__TraversabilityScore__are_equal(const space_msgs__msg__TraversabilityScore * lhs, const space_msgs__msg__TraversabilityScore * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__are_equal(
      &(lhs->header), &(rhs->header)))
  {
    return false;
  }
  // rover_id
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->rover_id), &(rhs->rover_id)))
  {
    return false;
  }
  // rover_spec
  if (!space_msgs__msg__RoverSpec__are_equal(
      &(lhs->rover_spec), &(rhs->rover_spec)))
  {
    return false;
  }
  // grid
  if (!grid_map_msgs__msg__GridMap__are_equal(
      &(lhs->grid), &(rhs->grid)))
  {
    return false;
  }
  // terrain_stamp
  if (!builtin_interfaces__msg__Time__are_equal(
      &(lhs->terrain_stamp), &(rhs->terrain_stamp)))
  {
    return false;
  }
  // soil_model_id
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->soil_model_id), &(rhs->soil_model_id)))
  {
    return false;
  }
  // soil_model_version
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->soil_model_version), &(rhs->soil_model_version)))
  {
    return false;
  }
  // evaluator_version
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->evaluator_version), &(rhs->evaluator_version)))
  {
    return false;
  }
  return true;
}

bool
space_msgs__msg__TraversabilityScore__copy(
  const space_msgs__msg__TraversabilityScore * input,
  space_msgs__msg__TraversabilityScore * output)
{
  if (!input || !output) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__copy(
      &(input->header), &(output->header)))
  {
    return false;
  }
  // rover_id
  if (!rosidl_runtime_c__String__copy(
      &(input->rover_id), &(output->rover_id)))
  {
    return false;
  }
  // rover_spec
  if (!space_msgs__msg__RoverSpec__copy(
      &(input->rover_spec), &(output->rover_spec)))
  {
    return false;
  }
  // grid
  if (!grid_map_msgs__msg__GridMap__copy(
      &(input->grid), &(output->grid)))
  {
    return false;
  }
  // terrain_stamp
  if (!builtin_interfaces__msg__Time__copy(
      &(input->terrain_stamp), &(output->terrain_stamp)))
  {
    return false;
  }
  // soil_model_id
  if (!rosidl_runtime_c__String__copy(
      &(input->soil_model_id), &(output->soil_model_id)))
  {
    return false;
  }
  // soil_model_version
  if (!rosidl_runtime_c__String__copy(
      &(input->soil_model_version), &(output->soil_model_version)))
  {
    return false;
  }
  // evaluator_version
  if (!rosidl_runtime_c__String__copy(
      &(input->evaluator_version), &(output->evaluator_version)))
  {
    return false;
  }
  return true;
}

space_msgs__msg__TraversabilityScore *
space_msgs__msg__TraversabilityScore__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  space_msgs__msg__TraversabilityScore * msg = (space_msgs__msg__TraversabilityScore *)allocator.allocate(sizeof(space_msgs__msg__TraversabilityScore), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(space_msgs__msg__TraversabilityScore));
  bool success = space_msgs__msg__TraversabilityScore__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
space_msgs__msg__TraversabilityScore__destroy(space_msgs__msg__TraversabilityScore * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    space_msgs__msg__TraversabilityScore__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
space_msgs__msg__TraversabilityScore__Sequence__init(space_msgs__msg__TraversabilityScore__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  space_msgs__msg__TraversabilityScore * data = NULL;

  if (size) {
    data = (space_msgs__msg__TraversabilityScore *)allocator.zero_allocate(size, sizeof(space_msgs__msg__TraversabilityScore), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = space_msgs__msg__TraversabilityScore__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        space_msgs__msg__TraversabilityScore__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
space_msgs__msg__TraversabilityScore__Sequence__fini(space_msgs__msg__TraversabilityScore__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      space_msgs__msg__TraversabilityScore__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

space_msgs__msg__TraversabilityScore__Sequence *
space_msgs__msg__TraversabilityScore__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  space_msgs__msg__TraversabilityScore__Sequence * array = (space_msgs__msg__TraversabilityScore__Sequence *)allocator.allocate(sizeof(space_msgs__msg__TraversabilityScore__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = space_msgs__msg__TraversabilityScore__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
space_msgs__msg__TraversabilityScore__Sequence__destroy(space_msgs__msg__TraversabilityScore__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    space_msgs__msg__TraversabilityScore__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
space_msgs__msg__TraversabilityScore__Sequence__are_equal(const space_msgs__msg__TraversabilityScore__Sequence * lhs, const space_msgs__msg__TraversabilityScore__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!space_msgs__msg__TraversabilityScore__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
space_msgs__msg__TraversabilityScore__Sequence__copy(
  const space_msgs__msg__TraversabilityScore__Sequence * input,
  space_msgs__msg__TraversabilityScore__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(space_msgs__msg__TraversabilityScore);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    space_msgs__msg__TraversabilityScore * data =
      (space_msgs__msg__TraversabilityScore *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!space_msgs__msg__TraversabilityScore__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          space_msgs__msg__TraversabilityScore__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!space_msgs__msg__TraversabilityScore__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
