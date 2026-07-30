// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from space_msgs:msg/RoverSpec.idl
// generated code does not contain a copyright notice
#include "space_msgs/msg/detail/rover_spec__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `rover_id`
// Member `provenance_note`
#include "rosidl_runtime_c/string_functions.h"

bool
space_msgs__msg__RoverSpec__init(space_msgs__msg__RoverSpec * msg)
{
  if (!msg) {
    return false;
  }
  // rover_id
  if (!rosidl_runtime_c__String__init(&msg->rover_id)) {
    space_msgs__msg__RoverSpec__fini(msg);
    return false;
  }
  // mass_kg
  // wheel_radius_m
  // wheel_width_m
  // ground_pressure_kpa
  // max_climb_angle_rad
  // min_passable_width_m
  // ground_clearance_m
  // has_grousers
  // provenance
  // provenance_note
  if (!rosidl_runtime_c__String__init(&msg->provenance_note)) {
    space_msgs__msg__RoverSpec__fini(msg);
    return false;
  }
  return true;
}

void
space_msgs__msg__RoverSpec__fini(space_msgs__msg__RoverSpec * msg)
{
  if (!msg) {
    return;
  }
  // rover_id
  rosidl_runtime_c__String__fini(&msg->rover_id);
  // mass_kg
  // wheel_radius_m
  // wheel_width_m
  // ground_pressure_kpa
  // max_climb_angle_rad
  // min_passable_width_m
  // ground_clearance_m
  // has_grousers
  // provenance
  // provenance_note
  rosidl_runtime_c__String__fini(&msg->provenance_note);
}

bool
space_msgs__msg__RoverSpec__are_equal(const space_msgs__msg__RoverSpec * lhs, const space_msgs__msg__RoverSpec * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // rover_id
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->rover_id), &(rhs->rover_id)))
  {
    return false;
  }
  // mass_kg
  if (lhs->mass_kg != rhs->mass_kg) {
    return false;
  }
  // wheel_radius_m
  if (lhs->wheel_radius_m != rhs->wheel_radius_m) {
    return false;
  }
  // wheel_width_m
  if (lhs->wheel_width_m != rhs->wheel_width_m) {
    return false;
  }
  // ground_pressure_kpa
  if (lhs->ground_pressure_kpa != rhs->ground_pressure_kpa) {
    return false;
  }
  // max_climb_angle_rad
  if (lhs->max_climb_angle_rad != rhs->max_climb_angle_rad) {
    return false;
  }
  // min_passable_width_m
  if (lhs->min_passable_width_m != rhs->min_passable_width_m) {
    return false;
  }
  // ground_clearance_m
  if (lhs->ground_clearance_m != rhs->ground_clearance_m) {
    return false;
  }
  // has_grousers
  if (lhs->has_grousers != rhs->has_grousers) {
    return false;
  }
  // provenance
  if (lhs->provenance != rhs->provenance) {
    return false;
  }
  // provenance_note
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->provenance_note), &(rhs->provenance_note)))
  {
    return false;
  }
  return true;
}

bool
space_msgs__msg__RoverSpec__copy(
  const space_msgs__msg__RoverSpec * input,
  space_msgs__msg__RoverSpec * output)
{
  if (!input || !output) {
    return false;
  }
  // rover_id
  if (!rosidl_runtime_c__String__copy(
      &(input->rover_id), &(output->rover_id)))
  {
    return false;
  }
  // mass_kg
  output->mass_kg = input->mass_kg;
  // wheel_radius_m
  output->wheel_radius_m = input->wheel_radius_m;
  // wheel_width_m
  output->wheel_width_m = input->wheel_width_m;
  // ground_pressure_kpa
  output->ground_pressure_kpa = input->ground_pressure_kpa;
  // max_climb_angle_rad
  output->max_climb_angle_rad = input->max_climb_angle_rad;
  // min_passable_width_m
  output->min_passable_width_m = input->min_passable_width_m;
  // ground_clearance_m
  output->ground_clearance_m = input->ground_clearance_m;
  // has_grousers
  output->has_grousers = input->has_grousers;
  // provenance
  output->provenance = input->provenance;
  // provenance_note
  if (!rosidl_runtime_c__String__copy(
      &(input->provenance_note), &(output->provenance_note)))
  {
    return false;
  }
  return true;
}

space_msgs__msg__RoverSpec *
space_msgs__msg__RoverSpec__create(void)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  space_msgs__msg__RoverSpec * msg = (space_msgs__msg__RoverSpec *)allocator.allocate(sizeof(space_msgs__msg__RoverSpec), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(space_msgs__msg__RoverSpec));
  bool success = space_msgs__msg__RoverSpec__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
space_msgs__msg__RoverSpec__destroy(space_msgs__msg__RoverSpec * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    space_msgs__msg__RoverSpec__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
space_msgs__msg__RoverSpec__Sequence__init(space_msgs__msg__RoverSpec__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  space_msgs__msg__RoverSpec * data = NULL;

  if (size) {
    data = (space_msgs__msg__RoverSpec *)allocator.zero_allocate(size, sizeof(space_msgs__msg__RoverSpec), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = space_msgs__msg__RoverSpec__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        space_msgs__msg__RoverSpec__fini(&data[i - 1]);
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
space_msgs__msg__RoverSpec__Sequence__fini(space_msgs__msg__RoverSpec__Sequence * array)
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
      space_msgs__msg__RoverSpec__fini(&array->data[i]);
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

space_msgs__msg__RoverSpec__Sequence *
space_msgs__msg__RoverSpec__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  space_msgs__msg__RoverSpec__Sequence * array = (space_msgs__msg__RoverSpec__Sequence *)allocator.allocate(sizeof(space_msgs__msg__RoverSpec__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = space_msgs__msg__RoverSpec__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
space_msgs__msg__RoverSpec__Sequence__destroy(space_msgs__msg__RoverSpec__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    space_msgs__msg__RoverSpec__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
space_msgs__msg__RoverSpec__Sequence__are_equal(const space_msgs__msg__RoverSpec__Sequence * lhs, const space_msgs__msg__RoverSpec__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!space_msgs__msg__RoverSpec__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
space_msgs__msg__RoverSpec__Sequence__copy(
  const space_msgs__msg__RoverSpec__Sequence * input,
  space_msgs__msg__RoverSpec__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(space_msgs__msg__RoverSpec);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    space_msgs__msg__RoverSpec * data =
      (space_msgs__msg__RoverSpec *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!space_msgs__msg__RoverSpec__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          space_msgs__msg__RoverSpec__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!space_msgs__msg__RoverSpec__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
