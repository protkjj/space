// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from space_msgs:msg/SlipEstimate.idl
// generated code does not contain a copyright notice
#include "space_msgs/msg/detail/slip_estimate__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/detail/header__functions.h"

bool
space_msgs__msg__SlipEstimate__init(space_msgs__msg__SlipEstimate * msg)
{
  if (!msg) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__init(&msg->header)) {
    space_msgs__msg__SlipEstimate__fini(msg);
    return false;
  }
  // slip_ratio
  // v_wheel
  // v_actual
  // valid
  // quality
  // source
  return true;
}

void
space_msgs__msg__SlipEstimate__fini(space_msgs__msg__SlipEstimate * msg)
{
  if (!msg) {
    return;
  }
  // header
  std_msgs__msg__Header__fini(&msg->header);
  // slip_ratio
  // v_wheel
  // v_actual
  // valid
  // quality
  // source
}

bool
space_msgs__msg__SlipEstimate__are_equal(const space_msgs__msg__SlipEstimate * lhs, const space_msgs__msg__SlipEstimate * rhs)
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
  // slip_ratio
  if (lhs->slip_ratio != rhs->slip_ratio) {
    return false;
  }
  // v_wheel
  if (lhs->v_wheel != rhs->v_wheel) {
    return false;
  }
  // v_actual
  if (lhs->v_actual != rhs->v_actual) {
    return false;
  }
  // valid
  if (lhs->valid != rhs->valid) {
    return false;
  }
  // quality
  if (lhs->quality != rhs->quality) {
    return false;
  }
  // source
  if (lhs->source != rhs->source) {
    return false;
  }
  return true;
}

bool
space_msgs__msg__SlipEstimate__copy(
  const space_msgs__msg__SlipEstimate * input,
  space_msgs__msg__SlipEstimate * output)
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
  // slip_ratio
  output->slip_ratio = input->slip_ratio;
  // v_wheel
  output->v_wheel = input->v_wheel;
  // v_actual
  output->v_actual = input->v_actual;
  // valid
  output->valid = input->valid;
  // quality
  output->quality = input->quality;
  // source
  output->source = input->source;
  return true;
}

space_msgs__msg__SlipEstimate *
space_msgs__msg__SlipEstimate__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  space_msgs__msg__SlipEstimate * msg = (space_msgs__msg__SlipEstimate *)allocator.allocate(sizeof(space_msgs__msg__SlipEstimate), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(space_msgs__msg__SlipEstimate));
  bool success = space_msgs__msg__SlipEstimate__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
space_msgs__msg__SlipEstimate__destroy(space_msgs__msg__SlipEstimate * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    space_msgs__msg__SlipEstimate__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
space_msgs__msg__SlipEstimate__Sequence__init(space_msgs__msg__SlipEstimate__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  space_msgs__msg__SlipEstimate * data = NULL;

  if (size) {
    data = (space_msgs__msg__SlipEstimate *)allocator.zero_allocate(size, sizeof(space_msgs__msg__SlipEstimate), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = space_msgs__msg__SlipEstimate__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        space_msgs__msg__SlipEstimate__fini(&data[i - 1]);
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
space_msgs__msg__SlipEstimate__Sequence__fini(space_msgs__msg__SlipEstimate__Sequence * array)
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
      space_msgs__msg__SlipEstimate__fini(&array->data[i]);
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

space_msgs__msg__SlipEstimate__Sequence *
space_msgs__msg__SlipEstimate__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  space_msgs__msg__SlipEstimate__Sequence * array = (space_msgs__msg__SlipEstimate__Sequence *)allocator.allocate(sizeof(space_msgs__msg__SlipEstimate__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = space_msgs__msg__SlipEstimate__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
space_msgs__msg__SlipEstimate__Sequence__destroy(space_msgs__msg__SlipEstimate__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    space_msgs__msg__SlipEstimate__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
space_msgs__msg__SlipEstimate__Sequence__are_equal(const space_msgs__msg__SlipEstimate__Sequence * lhs, const space_msgs__msg__SlipEstimate__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!space_msgs__msg__SlipEstimate__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
space_msgs__msg__SlipEstimate__Sequence__copy(
  const space_msgs__msg__SlipEstimate__Sequence * input,
  space_msgs__msg__SlipEstimate__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(space_msgs__msg__SlipEstimate);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    space_msgs__msg__SlipEstimate * data =
      (space_msgs__msg__SlipEstimate *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!space_msgs__msg__SlipEstimate__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          space_msgs__msg__SlipEstimate__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!space_msgs__msg__SlipEstimate__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
