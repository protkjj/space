// generated from rosidl_generator_py/resource/_idl_support.c.em
// with input from space_msgs:msg/SlipEstimate.idl
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
#include "space_msgs/msg/detail/slip_estimate__struct.h"
#include "space_msgs/msg/detail/slip_estimate__functions.h"

ROSIDL_GENERATOR_C_IMPORT
bool std_msgs__msg__header__convert_from_py(PyObject * _pymsg, void * _ros_message);
ROSIDL_GENERATOR_C_IMPORT
PyObject * std_msgs__msg__header__convert_to_py(void * raw_ros_message);

ROSIDL_GENERATOR_C_EXPORT
bool space_msgs__msg__slip_estimate__convert_from_py(PyObject * _pymsg, void * _ros_message)
{
  // check that the passed message is of the expected Python class
  {
    char full_classname_dest[43];
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
    assert(strncmp("space_msgs.msg._slip_estimate.SlipEstimate", full_classname_dest, 42) == 0);
  }
  space_msgs__msg__SlipEstimate * ros_message = _ros_message;
  {  // header
    PyObject * field = PyObject_GetAttrString(_pymsg, "header");
    if (!field) {
      return false;
    }
    if (!std_msgs__msg__header__convert_from_py(field, &ros_message->header)) {
      Py_DECREF(field);
      return false;
    }
    Py_DECREF(field);
  }
  {  // slip_ratio
    PyObject * field = PyObject_GetAttrString(_pymsg, "slip_ratio");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->slip_ratio = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // v_wheel
    PyObject * field = PyObject_GetAttrString(_pymsg, "v_wheel");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->v_wheel = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // v_actual
    PyObject * field = PyObject_GetAttrString(_pymsg, "v_actual");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->v_actual = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // valid
    PyObject * field = PyObject_GetAttrString(_pymsg, "valid");
    if (!field) {
      return false;
    }
    assert(PyBool_Check(field));
    ros_message->valid = (Py_True == field);
    Py_DECREF(field);
  }
  {  // quality
    PyObject * field = PyObject_GetAttrString(_pymsg, "quality");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->quality = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // source
    PyObject * field = PyObject_GetAttrString(_pymsg, "source");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->source = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }

  return true;
}

ROSIDL_GENERATOR_C_EXPORT
PyObject * space_msgs__msg__slip_estimate__convert_to_py(void * raw_ros_message)
{
  /* NOTE(esteve): Call constructor of SlipEstimate */
  PyObject * _pymessage = NULL;
  {
    PyObject * pymessage_module = PyImport_ImportModule("space_msgs.msg._slip_estimate");
    assert(pymessage_module);
    PyObject * pymessage_class = PyObject_GetAttrString(pymessage_module, "SlipEstimate");
    assert(pymessage_class);
    Py_DECREF(pymessage_module);
    _pymessage = PyObject_CallObject(pymessage_class, NULL);
    Py_DECREF(pymessage_class);
    if (!_pymessage) {
      return NULL;
    }
  }
  space_msgs__msg__SlipEstimate * ros_message = (space_msgs__msg__SlipEstimate *)raw_ros_message;
  {  // header
    PyObject * field = NULL;
    field = std_msgs__msg__header__convert_to_py(&ros_message->header);
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "header", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // slip_ratio
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->slip_ratio);
    {
      int rc = PyObject_SetAttrString(_pymessage, "slip_ratio", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // v_wheel
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->v_wheel);
    {
      int rc = PyObject_SetAttrString(_pymessage, "v_wheel", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // v_actual
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->v_actual);
    {
      int rc = PyObject_SetAttrString(_pymessage, "v_actual", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // valid
    PyObject * field = NULL;
    field = PyBool_FromLong(ros_message->valid ? 1 : 0);
    {
      int rc = PyObject_SetAttrString(_pymessage, "valid", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // quality
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->quality);
    {
      int rc = PyObject_SetAttrString(_pymessage, "quality", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // source
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->source);
    {
      int rc = PyObject_SetAttrString(_pymessage, "source", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }

  // ownership of _pymessage is transferred to the caller
  return _pymessage;
}
