# generated from rosidl_generator_py/resource/_idl.py.em
# with input from space_msgs:msg/SlipEstimate.idl
# generated code does not contain a copyright notice

# This is being done at the module level and not on the instance level to avoid looking
# for the same variable multiple times on each instance. This variable is not supposed to
# change during runtime so it makes sense to only look for it once.
from os import getenv

ros_python_check_fields = getenv('ROS_PYTHON_CHECK_FIELDS', default='')


# Import statements for member types

import builtins  # noqa: E402, I100

import math  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_SlipEstimate(type):
    """Metaclass of message 'SlipEstimate'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
        'SOURCE_UNKNOWN': 0,
        'SOURCE_SIM_GROUND_TRUTH': 1,
        'SOURCE_VIO': 2,
        'SOURCE_EKF': 3,
    }

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('space_msgs')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'space_msgs.msg.SlipEstimate')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__slip_estimate
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__slip_estimate
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__slip_estimate
            cls._TYPE_SUPPORT = module.type_support_msg__msg__slip_estimate
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__slip_estimate

            from std_msgs.msg import Header
            if Header.__class__._TYPE_SUPPORT is None:
                Header.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
            'SOURCE_UNKNOWN': cls.__constants['SOURCE_UNKNOWN'],
            'SOURCE_SIM_GROUND_TRUTH': cls.__constants['SOURCE_SIM_GROUND_TRUTH'],
            'SOURCE_VIO': cls.__constants['SOURCE_VIO'],
            'SOURCE_EKF': cls.__constants['SOURCE_EKF'],
        }

    @property
    def SOURCE_UNKNOWN(self):
        """Message constant 'SOURCE_UNKNOWN'."""
        return Metaclass_SlipEstimate.__constants['SOURCE_UNKNOWN']

    @property
    def SOURCE_SIM_GROUND_TRUTH(self):
        """Message constant 'SOURCE_SIM_GROUND_TRUTH'."""
        return Metaclass_SlipEstimate.__constants['SOURCE_SIM_GROUND_TRUTH']

    @property
    def SOURCE_VIO(self):
        """Message constant 'SOURCE_VIO'."""
        return Metaclass_SlipEstimate.__constants['SOURCE_VIO']

    @property
    def SOURCE_EKF(self):
        """Message constant 'SOURCE_EKF'."""
        return Metaclass_SlipEstimate.__constants['SOURCE_EKF']


class SlipEstimate(metaclass=Metaclass_SlipEstimate):
    """
    Message class 'SlipEstimate'.

    Constants:
      SOURCE_UNKNOWN
      SOURCE_SIM_GROUND_TRUTH
      SOURCE_VIO
      SOURCE_EKF
    """

    __slots__ = [
        '_header',
        '_slip_ratio',
        '_v_wheel',
        '_v_actual',
        '_valid',
        '_quality',
        '_source',
        '_check_fields',
    ]

    _fields_and_field_types = {
        'header': 'std_msgs/Header',
        'slip_ratio': 'float',
        'v_wheel': 'float',
        'v_actual': 'float',
        'valid': 'boolean',
        'quality': 'float',
        'source': 'uint8',
    }

    # This attribute is used to store an rosidl_parser.definition variable
    # related to the data type of each of the components the message.
    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['std_msgs', 'msg'], 'Header'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        if 'check_fields' in kwargs:
            self._check_fields = kwargs['check_fields']
        else:
            self._check_fields = ros_python_check_fields == '1'
        if self._check_fields:
            assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
                'Invalid arguments passed to constructor: %s' % \
                ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        from std_msgs.msg import Header
        self.header = kwargs.get('header', Header())
        self.slip_ratio = kwargs.get('slip_ratio', float())
        self.v_wheel = kwargs.get('v_wheel', float())
        self.v_actual = kwargs.get('v_actual', float())
        self.valid = kwargs.get('valid', bool())
        self.quality = kwargs.get('quality', float())
        self.source = kwargs.get('source', int())

    def __repr__(self):
        typename = self.__class__.__module__.split('.')
        typename.pop()
        typename.append(self.__class__.__name__)
        args = []
        for s, t in zip(self.get_fields_and_field_types().keys(), self.SLOT_TYPES):
            field = getattr(self, s)
            fieldstr = repr(field)
            # We use Python array type for fields that can be directly stored
            # in them, and "normal" sequences for everything else.  If it is
            # a type that we store in an array, strip off the 'array' portion.
            if (
                isinstance(t, rosidl_parser.definition.AbstractSequence) and
                isinstance(t.value_type, rosidl_parser.definition.BasicType) and
                t.value_type.typename in ['float', 'double', 'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64']
            ):
                if len(field) == 0:
                    fieldstr = '[]'
                else:
                    if self._check_fields:
                        assert fieldstr.startswith('array(')
                    prefix = "array('X', "
                    suffix = ')'
                    fieldstr = fieldstr[len(prefix):-len(suffix)]
            args.append(s + '=' + fieldstr)
        return '%s(%s)' % ('.'.join(typename), ', '.join(args))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.header != other.header:
            return False
        if self.slip_ratio != other.slip_ratio:
            return False
        if self.v_wheel != other.v_wheel:
            return False
        if self.v_actual != other.v_actual:
            return False
        if self.valid != other.valid:
            return False
        if self.quality != other.quality:
            return False
        if self.source != other.source:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def header(self):
        """Message field 'header'."""
        return self._header

    @header.setter
    def header(self, value):
        if self._check_fields:
            from std_msgs.msg import Header
            assert \
                isinstance(value, Header), \
                "The 'header' field must be a sub message of type 'Header'"
        self._header = value

    @builtins.property
    def slip_ratio(self):
        """Message field 'slip_ratio'."""
        return self._slip_ratio

    @slip_ratio.setter
    def slip_ratio(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'slip_ratio' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'slip_ratio' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._slip_ratio = value

    @builtins.property
    def v_wheel(self):
        """Message field 'v_wheel'."""
        return self._v_wheel

    @v_wheel.setter
    def v_wheel(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'v_wheel' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'v_wheel' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._v_wheel = value

    @builtins.property
    def v_actual(self):
        """Message field 'v_actual'."""
        return self._v_actual

    @v_actual.setter
    def v_actual(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'v_actual' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'v_actual' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._v_actual = value

    @builtins.property
    def valid(self):
        """Message field 'valid'."""
        return self._valid

    @valid.setter
    def valid(self, value):
        if self._check_fields:
            assert \
                isinstance(value, bool), \
                "The 'valid' field must be of type 'bool'"
        self._valid = value

    @builtins.property
    def quality(self):
        """Message field 'quality'."""
        return self._quality

    @quality.setter
    def quality(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'quality' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'quality' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._quality = value

    @builtins.property
    def source(self):
        """Message field 'source'."""
        return self._source

    @source.setter
    def source(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'source' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'source' field must be an unsigned integer in [0, 255]"
        self._source = value
