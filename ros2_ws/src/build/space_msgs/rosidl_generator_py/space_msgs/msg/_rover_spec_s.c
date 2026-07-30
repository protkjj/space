// generated from rosidl_generator_py/resource/_idl_support.c.em
// with input from space_msgs:msg/RoverSpec.idl
// generated code does not contain a copyright notice
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <Python.h>
#include <stdbool.h>
#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-function"
#endif
#include "numpy/ndarrayobject.h"
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif
#include "rosidl_runtime_c/visibility_control.h"
#include "space_msgs/msg/detail/rover_spec__struct.h"
#include "space_msgs/msg/detail/rover_spec__functions.h"

#include "rosidl_runtime_c/string.h"
#include "rosidl_runtime_c/string_functions.h"


ROSIDL_GENERATOR_C_EXPORT
bool space_msgs__msg__rover_spec__convert_from_py(PyObject * _pymsg, void * _ros_message)
{
  // check that the passed message is of the expected Python class
  {
    char full_classname_dest[37];
    {
      char * class_name = NULL;
      char * module_name = NULL;
      {
        PyObject * class_attr = PyObject_GetAttrString(_pymsg, "__class__");
        if (class_attr) {
          PyObject * name_attr = PyObject_GetAttrString(class_attr, "__name__");
          if (name_attr) {
            class_name = (char *)PyUnicode_1BYTE_DATA(name_attr);
            Py_DECREF(name_attr);
          }
          PyObject * module_attr = PyObject_GetAttrString(class_attr, "__module__");
          if (module_attr) {
            module_name = (char *)PyUnicode_1BYTE_DATA(module_attr);
            Py_DECREF(module_attr);
          }
          Py_DECREF(class_attr);
        }
      }
      if (!class_name || !module_name) {
        return false;
      }
      snprintf(full_classname_dest, sizeof(full_classname_dest), "%s.%s", module_name, class_name);
    }
    assert(strncmp("space_msgs.msg._rover_spec.RoverSpec", full_classname_dest, 36) == 0);
  }
  space_msgs__msg__RoverSpec * ros_message = _ros_message;
  {  // rover_id
    PyObject * field = PyObject_GetAttrString(_pymsg, "rover_id");
    if (!field) {
      return false;
    }
    assert(PyUnicode_Check(field));
    PyObject * encoded_field = PyUnicode_AsUTF8String(field);
    if (!encoded_field) {
      Py_DECREF(field);
      return false;
    }
    rosidl_runtime_c__String__assign(&ros_message->rover_id, PyBytes_AS_STRING(encoded_field));
    Py_DECREF(encoded_field);
    Py_DECREF(field);
  }
  {  // mass_kg
    PyObject * field = PyObject_GetAttrString(_pymsg, "mass_kg");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->mass_kg = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // wheel_radius_m
    PyObject * field = PyObject_GetAttrString(_pymsg, "wheel_radius_m");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->wheel_radius_m = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // wheel_width_m
    PyObject * field = PyObject_GetAttrString(_pymsg, "wheel_width_m");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->wheel_width_m = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // ground_pressure_kpa
    PyObject * field = PyObject_GetAttrString(_pymsg, "ground_pressure_kpa");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->ground_pressure_kpa = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // max_climb_angle_rad
    PyObject * field = PyObject_GetAttrString(_pymsg, "max_climb_angle_rad");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->max_climb_angle_rad = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // min_passable_width_m
    PyObject * field = PyObject_GetAttrString(_pymsg, "min_passable_width_m");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->min_passable_width_m = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // ground_clearance_m
    PyObject * field = PyObject_GetAttrString(_pymsg, "ground_clearance_m");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->ground_clearance_m = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // has_grousers
    PyObject * field = PyObject_GetAttrString(_pymsg, "has_grousers");
    if (!field) {
      return false;
    }
    assert(PyBool_Check(field));
    ros_message->has_grousers = (Py_True == field);
    Py_DECREF(field);
  }
  {  // provenance
    PyObject * field = PyObject_GetAttrString(_pymsg, "provenance");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->provenance = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // provenance_note
    PyObject * field = PyObject_GetAttrString(_pymsg, "provenance_note");
    if (!field) {
      return false;
    }
    assert(PyUnicode_Check(field));
    PyObject * encoded_field = PyUnicode_AsUTF8String(field);
    if (!encoded_field) {
      Py_DECREF(field);
      return false;
    }
    rosidl_runtime_c__String__assign(&ros_message->provenance_note, PyBytes_AS_STRING(encoded_field));
    Py_DECREF(encoded_field);
    Py_DECREF(field);
  }

  return true;
}

ROSIDL_GENERATOR_C_EXPORT
PyObject * space_msgs__msg__rover_spec__convert_to_py(void * raw_ros_message)
{
  /* NOTE(esteve): Call constructor of RoverSpec */
  PyObject * _pymessage = NULL;
  {
    PyObject * pymessage_module = PyImport_ImportModule("space_msgs.msg._rover_spec");
    assert(pymessage_module);
    PyObject * pymessage_class = PyObject_GetAttrString(pymessage_module, "RoverSpec");
    assert(pymessage_class);
    Py_DECREF(pymessage_module);
    _pymessage = PyObject_CallObject(pymessage_class, NULL);
    Py_DECREF(pymessage_class);
    if (!_pymessage) {
      return NULL;
    }
  }
  space_msgs__msg__RoverSpec * ros_message = (space_msgs__msg__RoverSpec *)raw_ros_message;
  {  // rover_id
    PyObject * field = NULL;
    field = PyUnicode_DecodeUTF8(
      ros_message->rover_id.data,
      strlen(ros_message->rover_id.data),
      "replace");
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "rover_id", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // mass_kg
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->mass_kg);
    {
      int rc = PyObject_SetAttrString(_pymessage, "mass_kg", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // wheel_radius_m
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->wheel_radius_m);
    {
      int rc = PyObject_SetAttrString(_pymessage, "wheel_radius_m", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // wheel_width_m
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->wheel_width_m);
    {
      int rc = PyObject_SetAttrString(_pymessage, "wheel_width_m", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // ground_pressure_kpa
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->ground_pressure_kpa);
    {
      int rc = PyObject_SetAttrString(_pymessage, "ground_pressure_kpa", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // max_climb_angle_rad
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->max_climb_angle_rad);
    {
      int rc = PyObject_SetAttrString(_pymessage, "max_climb_angle_rad", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // min_passable_width_m
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->min_passable_width_m);
    {
      int rc = PyObject_SetAttrString(_pymessage, "min_passable_width_m", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // ground_clearance_m
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->ground_clearance_m);
    {
      int rc = PyObject_SetAttrString(_pymessage, "ground_clearance_m", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // has_grousers
    PyObject * field = NULL;
    field = PyBool_FromLong(ros_message->has_grousers ? 1 : 0);
    {
      int rc = PyObject_SetAttrString(_pymessage, "has_grousers", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // provenance
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->provenance);
    {
      int rc = PyObject_SetAttrString(_pymessage, "provenance", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // provenance_note
    PyObject * field = NULL;
    field = PyUnicode_DecodeUTF8(
      ros_message->provenance_note.data,
      strlen(ros_message->provenance_note.data),
      "replace");
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "provenance_note", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }

  // ownership of _pymessage is transferred to the caller
  return _pymessage;
}
