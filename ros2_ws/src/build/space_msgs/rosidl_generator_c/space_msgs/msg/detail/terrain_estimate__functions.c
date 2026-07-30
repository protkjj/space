// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from space_msgs:msg/TerrainEstimate.idl
// generated code does not contain a copyright notice
#include "space_msgs/msg/detail/terrain_estimate__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/detail/header__functions.h"
// Member `grid`
#include "grid_map_msgs/msg/detail/grid_map__functions.h"
// Member `soil_model_id`
// Member `soil_model_version`
#include "rosidl_runtime_c/string_functions.h"

bool
space_msgs__msg__TerrainEstimate__init(space_msgs__msg__TerrainEstimate * msg)
{
  if (!msg) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__init(&msg->header)) {
    space_msgs__msg__TerrainEstimate__fini(msg);
    return false;
  }
  // grid
  if (!grid_map_msgs__msg__GridMap__init(&msg->grid)) {
    space_msgs__msg__TerrainEstimate__fini(msg);
    return false;
  }
  // soil_model_id
  if (!rosidl_runtime_c__String__init(&msg->soil_model_id)) {
    space_msgs__msg__TerrainEstimate__fini(msg);
    return false;
  }
  // soil_model_version
  if (!rosidl_runtime_c__String__init(&msg->soil_model_version)) {
    space_msgs__msg__TerrainEstimate__fini(msg);
    return false;
  }
  return true;
}

void
space_msgs__msg__TerrainEstimate__fini(space_msgs__msg__TerrainEstimate * msg)
{
  if (!msg) {
    return;
  }
  // header
  std_msgs__msg__Header__fini(&msg->header);
  // grid
  grid_map_msgs__msg__GridMap__fini(&msg->grid);
  // soil_model_id
  rosidl_runtime_c__String__fini(&msg->soil_model_id);
  // soil_model_version
  rosidl_runtime_c__String__fini(&msg->soil_model_version);
}

bool
space_msgs__msg__TerrainEstimate__are_equal(const space_msgs__msg__TerrainEstimate * lhs, const space_msgs__msg__TerrainEstimate * rhs)
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
  // grid
  if (!grid_map_msgs__msg__GridMap__are_equal(
      &(lhs->grid), &(rhs->grid)))
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
  return true;
}

bool
space_msgs__msg__TerrainEstimate__copy(
  const space_msgs__msg__TerrainEstimate * input,
  space_msgs__msg__TerrainEstimate * output)
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
  // grid
  if (!grid_map_msgs__msg__GridMap__copy(
      &(input->grid), &(output->grid)))
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
  return true;
}

space_msgs__msg__TerrainEstimate *
space_msgs__msg__TerrainEstimate__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  space_msgs__msg__TerrainEstimate * msg = (space_msgs__msg__TerrainEstimate *)allocator.allocate(sizeof(space_msgs__msg__TerrainEstimate), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(space_msgs__msg__TerrainEstimate));
  bool success = space_msgs__msg__TerrainEstimate__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
space_msgs__msg__TerrainEstimate__destroy(space_msgs__msg__TerrainEstimate * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    space_msgs__msg__TerrainEstimate__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
space_msgs__msg__TerrainEstimate__Sequence__init(space_msgs__msg__TerrainEstimate__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  space_msgs__msg__TerrainEstimate * data = NULL;

  if (size) {
    data = (space_msgs__msg__TerrainEstimate *)allocator.zero_allocate(size, sizeof(space_msgs__msg__TerrainEstimate), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = space_msgs__msg__TerrainEstimate__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        space_msgs__msg__TerrainEstimate__fini(&data[i - 1]);
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
space_msgs__msg__TerrainEstimate__Sequence__fini(space_msgs__msg__TerrainEstimate__Sequence * array)
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
      space_msgs__msg__TerrainEstimate__fini(&array->data[i]);
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

space_msgs__msg__TerrainEstimate__Sequence *
space_msgs__msg__TerrainEstimate__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  space_msgs__msg__TerrainEstimate__Sequence * array = (space_msgs__msg__TerrainEstimate__Sequence *)allocator.allocate(sizeof(space_msgs__msg__TerrainEstimate__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = space_msgs__msg__TerrainEstimate__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
space_msgs__msg__TerrainEstimate__Sequence__destroy(space_msgs__msg__TerrainEstimate__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    space_msgs__msg__TerrainEstimate__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
space_msgs__msg__TerrainEstimate__Sequence__are_equal(const space_msgs__msg__TerrainEstimate__Sequence * lhs, const space_msgs__msg__TerrainEstimate__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!space_msgs__msg__TerrainEstimate__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
space_msgs__msg__TerrainEstimate__Sequence__copy(
  const space_msgs__msg__TerrainEstimate__Sequence * input,
  space_msgs__msg__TerrainEstimate__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(space_msgs__msg__TerrainEstimate);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    space_msgs__msg__TerrainEstimate * data =
      (space_msgs__msg__TerrainEstimate *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!space_msgs__msg__TerrainEstimate__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          space_msgs__msg__TerrainEstimate__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!space_msgs__msg__TerrainEstimate__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
