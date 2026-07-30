# generated from rosidl_generator_py/resource/_idl.py.em
# with input from space_msgs:msg/TerrainEstimate.idl
# generated code does not contain a copyright notice

# This is being done at the module level and not on the instance level to avoid looking
# for the same variable multiple times on each instance. This variable is not supposed to
# change during runtime so it makes sense to only look for it once.
from os import getenv

ros_python_check_fields = getenv('ROS_PYTHON_CHECK_FIELDS', default='')


# Import statements for member types

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_TerrainEstimate(type):
    """Metaclass of message 'TerrainEstimate'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
        'LAYER_SLOPE': 'slope_rad',
        'LAYER_ROUGHNESS': 'roughness_m',
        'LAYER_STEP': 'step_height_m',
        'LAYER_SLIP_SMALL': 'slip_small',
        'LAYER_SLIP_QUALITY': 'slip_quality',
        'LAYER_SLIP_SAMPLES': 'slip_samples',
        'LAYER_SOIL_DIFFICULTY': 'soil_difficulty',
        'LAYER_SOIL_CONFIDENCE': 'soil_confidence',
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
                'space_msgs.msg.TerrainEstimate')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__terrain_estimate
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__terrain_estimate
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__terrain_estimate
            cls._TYPE_SUPPORT = module.type_support_msg__msg__terrain_estimate
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__terrain_estimate

            from grid_map_msgs.msg import GridMap
            if GridMap.__class__._TYPE_SUPPORT is None:
                GridMap.__class__.__import_type_support__()

            from std_msgs.msg import Header
            if Header.__class__._TYPE_SUPPORT is None:
                Header.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
            'LAYER_SLOPE': cls.__constants['LAYER_SLOPE'],
            'LAYER_ROUGHNESS': cls.__constants['LAYER_ROUGHNESS'],
            'LAYER_STEP': cls.__constants['LAYER_STEP'],
            'LAYER_SLIP_SMALL': cls.__constants['LAYER_SLIP_SMALL'],
            'LAYER_SLIP_QUALITY': cls.__constants['LAYER_SLIP_QUALITY'],
            'LAYER_SLIP_SAMPLES': cls.__constants['LAYER_SLIP_SAMPLES'],
            'LAYER_SOIL_DIFFICULTY': cls.__constants['LAYER_SOIL_DIFFICULTY'],
            'LAYER_SOIL_CONFIDENCE': cls.__constants['LAYER_SOIL_CONFIDENCE'],
        }

    @property
    def LAYER_SLOPE(self):
        """Message constant 'LAYER_SLOPE'."""
        return Metaclass_TerrainEstimate.__constants['LAYER_SLOPE']

    @property
    def LAYER_ROUGHNESS(self):
        """Message constant 'LAYER_ROUGHNESS'."""
        return Metaclass_TerrainEstimate.__constants['LAYER_ROUGHNESS']

    @property
    def LAYER_STEP(self):
        """Message constant 'LAYER_STEP'."""
        return Metaclass_TerrainEstimate.__constants['LAYER_STEP']

    @property
    def LAYER_SLIP_SMALL(self):
        """Message constant 'LAYER_SLIP_SMALL'."""
        return Metaclass_TerrainEstimate.__constants['LAYER_SLIP_SMALL']

    @property
    def LAYER_SLIP_QUALITY(self):
        """Message constant 'LAYER_SLIP_QUALITY'."""
        return Metaclass_TerrainEstimate.__constants['LAYER_SLIP_QUALITY']

    @property
    def LAYER_SLIP_SAMPLES(self):
        """Message constant 'LAYER_SLIP_SAMPLES'."""
        return Metaclass_TerrainEstimate.__constants['LAYER_SLIP_SAMPLES']

    @property
    def LAYER_SOIL_DIFFICULTY(self):
        """Message constant 'LAYER_SOIL_DIFFICULTY'."""
        return Metaclass_TerrainEstimate.__constants['LAYER_SOIL_DIFFICULTY']

    @property
    def LAYER_SOIL_CONFIDENCE(self):
        """Message constant 'LAYER_SOIL_CONFIDENCE'."""
        return Metaclass_TerrainEstimate.__constants['LAYER_SOIL_CONFIDENCE']


class TerrainEstimate(metaclass=Metaclass_TerrainEstimate):
    """
    Message class 'TerrainEstimate'.

    Constants:
      LAYER_SLOPE
      LAYER_ROUGHNESS
      LAYER_STEP
      LAYER_SLIP_SMALL
      LAYER_SLIP_QUALITY
      LAYER_SLIP_SAMPLES
      LAYER_SOIL_DIFFICULTY
      LAYER_SOIL_CONFIDENCE
    """

    __slots__ = [
        '_header',
        '_grid',
        '_soil_model_id',
        '_soil_model_version',
        '_check_fields',
    ]

    _fields_and_field_types = {
        'header': 'std_msgs/Header',
        'grid': 'grid_map_msgs/GridMap',
        'soil_model_id': 'string',
        'soil_model_version': 'string',
    }

    # This attribute is used to store an rosidl_parser.definition variable
    # related to the data type of each of the components the message.
    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['std_msgs', 'msg'], 'Header'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['grid_map_msgs', 'msg'], 'GridMap'),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
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
        from grid_map_msgs.msg import GridMap
        self.grid = kwargs.get('grid', GridMap())
        self.soil_model_id = kwargs.get('soil_model_id', str())
        self.soil_model_version = kwargs.get('soil_model_version', str())

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
        if self.grid != other.grid:
            return False
        if self.soil_model_id != other.soil_model_id:
            return False
        if self.soil_model_version != other.soil_model_version:
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
    def grid(self):
        """Message field 'grid'."""
        return self._grid

    @grid.setter
    def grid(self, value):
        if self._check_fields:
            from grid_map_msgs.msg import GridMap
            assert \
                isinstance(value, GridMap), \
                "The 'grid' field must be a sub message of type 'GridMap'"
        self._grid = value

    @builtins.property
    def soil_model_id(self):
        """Message field 'soil_model_id'."""
        return self._soil_model_id

    @soil_model_id.setter
    def soil_model_id(self, value):
        if self._check_fields:
            assert \
                isinstance(value, str), \
                "The 'soil_model_id' field must be of type 'str'"
        self._soil_model_id = value

    @builtins.property
    def soil_model_version(self):
        """Message field 'soil_model_version'."""
        return self._soil_model_version

    @soil_model_version.setter
    def soil_model_version(self, value):
        if self._check_fields:
            assert \
                isinstance(value, str), \
                "The 'soil_model_version' field must be of type 'str'"
        self._soil_model_version = value
