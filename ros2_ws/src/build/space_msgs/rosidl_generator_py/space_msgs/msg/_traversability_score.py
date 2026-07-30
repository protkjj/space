# generated from rosidl_generator_py/resource/_idl.py.em
# with input from space_msgs:msg/TraversabilityScore.idl
# generated code does not contain a copyright notice

# This is being done at the module level and not on the instance level to avoid looking
# for the same variable multiple times on each instance. This variable is not supposed to
# change during runtime so it makes sense to only look for it once.
from os import getenv

ros_python_check_fields = getenv('ROS_PYTHON_CHECK_FIELDS', default='')


# Import statements for member types

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_TraversabilityScore(type):
    """Metaclass of message 'TraversabilityScore'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
        'LAYER_SCORE': 'score',
        'LAYER_LIMITING_FACTOR': 'limiting_factor',
        'LIMIT_NONE': 0,
        'LIMIT_SLOPE': 1,
        'LIMIT_ROUGHNESS': 2,
        'LIMIT_STEP': 3,
        'LIMIT_SOIL': 4,
        'LIMIT_CLEARANCE': 5,
        'LIMIT_WIDTH': 6,
        'LIMIT_NO_DATA': 7,
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
                'space_msgs.msg.TraversabilityScore')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__traversability_score
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__traversability_score
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__traversability_score
            cls._TYPE_SUPPORT = module.type_support_msg__msg__traversability_score
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__traversability_score

            from builtin_interfaces.msg import Time
            if Time.__class__._TYPE_SUPPORT is None:
                Time.__class__.__import_type_support__()

            from grid_map_msgs.msg import GridMap
            if GridMap.__class__._TYPE_SUPPORT is None:
                GridMap.__class__.__import_type_support__()

            from space_msgs.msg import RoverSpec
            if RoverSpec.__class__._TYPE_SUPPORT is None:
                RoverSpec.__class__.__import_type_support__()

            from std_msgs.msg import Header
            if Header.__class__._TYPE_SUPPORT is None:
                Header.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
            'LAYER_SCORE': cls.__constants['LAYER_SCORE'],
            'LAYER_LIMITING_FACTOR': cls.__constants['LAYER_LIMITING_FACTOR'],
            'LIMIT_NONE': cls.__constants['LIMIT_NONE'],
            'LIMIT_SLOPE': cls.__constants['LIMIT_SLOPE'],
            'LIMIT_ROUGHNESS': cls.__constants['LIMIT_ROUGHNESS'],
            'LIMIT_STEP': cls.__constants['LIMIT_STEP'],
            'LIMIT_SOIL': cls.__constants['LIMIT_SOIL'],
            'LIMIT_CLEARANCE': cls.__constants['LIMIT_CLEARANCE'],
            'LIMIT_WIDTH': cls.__constants['LIMIT_WIDTH'],
            'LIMIT_NO_DATA': cls.__constants['LIMIT_NO_DATA'],
        }

    @property
    def LAYER_SCORE(self):
        """Message constant 'LAYER_SCORE'."""
        return Metaclass_TraversabilityScore.__constants['LAYER_SCORE']

    @property
    def LAYER_LIMITING_FACTOR(self):
        """Message constant 'LAYER_LIMITING_FACTOR'."""
        return Metaclass_TraversabilityScore.__constants['LAYER_LIMITING_FACTOR']

    @property
    def LIMIT_NONE(self):
        """Message constant 'LIMIT_NONE'."""
        return Metaclass_TraversabilityScore.__constants['LIMIT_NONE']

    @property
    def LIMIT_SLOPE(self):
        """Message constant 'LIMIT_SLOPE'."""
        return Metaclass_TraversabilityScore.__constants['LIMIT_SLOPE']

    @property
    def LIMIT_ROUGHNESS(self):
        """Message constant 'LIMIT_ROUGHNESS'."""
        return Metaclass_TraversabilityScore.__constants['LIMIT_ROUGHNESS']

    @property
    def LIMIT_STEP(self):
        """Message constant 'LIMIT_STEP'."""
        return Metaclass_TraversabilityScore.__constants['LIMIT_STEP']

    @property
    def LIMIT_SOIL(self):
        """Message constant 'LIMIT_SOIL'."""
        return Metaclass_TraversabilityScore.__constants['LIMIT_SOIL']

    @property
    def LIMIT_CLEARANCE(self):
        """Message constant 'LIMIT_CLEARANCE'."""
        return Metaclass_TraversabilityScore.__constants['LIMIT_CLEARANCE']

    @property
    def LIMIT_WIDTH(self):
        """Message constant 'LIMIT_WIDTH'."""
        return Metaclass_TraversabilityScore.__constants['LIMIT_WIDTH']

    @property
    def LIMIT_NO_DATA(self):
        """Message constant 'LIMIT_NO_DATA'."""
        return Metaclass_TraversabilityScore.__constants['LIMIT_NO_DATA']


class TraversabilityScore(metaclass=Metaclass_TraversabilityScore):
    """
    Message class 'TraversabilityScore'.

    Constants:
      LAYER_SCORE
      LAYER_LIMITING_FACTOR
      LIMIT_NONE
      LIMIT_SLOPE
      LIMIT_ROUGHNESS
      LIMIT_STEP
      LIMIT_SOIL
      LIMIT_CLEARANCE
      LIMIT_WIDTH
      LIMIT_NO_DATA
    """

    __slots__ = [
        '_header',
        '_rover_id',
        '_rover_spec',
        '_grid',
        '_terrain_stamp',
        '_soil_model_id',
        '_soil_model_version',
        '_evaluator_version',
        '_check_fields',
    ]

    _fields_and_field_types = {
        'header': 'std_msgs/Header',
        'rover_id': 'string',
        'rover_spec': 'space_msgs/RoverSpec',
        'grid': 'grid_map_msgs/GridMap',
        'terrain_stamp': 'builtin_interfaces/Time',
        'soil_model_id': 'string',
        'soil_model_version': 'string',
        'evaluator_version': 'string',
    }

    # This attribute is used to store an rosidl_parser.definition variable
    # related to the data type of each of the components the message.
    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['std_msgs', 'msg'], 'Header'),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['space_msgs', 'msg'], 'RoverSpec'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['grid_map_msgs', 'msg'], 'GridMap'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['builtin_interfaces', 'msg'], 'Time'),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
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
        self.rover_id = kwargs.get('rover_id', str())
        from space_msgs.msg import RoverSpec
        self.rover_spec = kwargs.get('rover_spec', RoverSpec())
        from grid_map_msgs.msg import GridMap
        self.grid = kwargs.get('grid', GridMap())
        from builtin_interfaces.msg import Time
        self.terrain_stamp = kwargs.get('terrain_stamp', Time())
        self.soil_model_id = kwargs.get('soil_model_id', str())
        self.soil_model_version = kwargs.get('soil_model_version', str())
        self.evaluator_version = kwargs.get('evaluator_version', str())

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
        if self.rover_id != other.rover_id:
            return False
        if self.rover_spec != other.rover_spec:
            return False
        if self.grid != other.grid:
            return False
        if self.terrain_stamp != other.terrain_stamp:
            return False
        if self.soil_model_id != other.soil_model_id:
            return False
        if self.soil_model_version != other.soil_model_version:
            return False
        if self.evaluator_version != other.evaluator_version:
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
    def rover_id(self):
        """Message field 'rover_id'."""
        return self._rover_id

    @rover_id.setter
    def rover_id(self, value):
        if self._check_fields:
            assert \
                isinstance(value, str), \
                "The 'rover_id' field must be of type 'str'"
        self._rover_id = value

    @builtins.property
    def rover_spec(self):
        """Message field 'rover_spec'."""
        return self._rover_spec

    @rover_spec.setter
    def rover_spec(self, value):
        if self._check_fields:
            from space_msgs.msg import RoverSpec
            assert \
                isinstance(value, RoverSpec), \
                "The 'rover_spec' field must be a sub message of type 'RoverSpec'"
        self._rover_spec = value

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
    def terrain_stamp(self):
        """Message field 'terrain_stamp'."""
        return self._terrain_stamp

    @terrain_stamp.setter
    def terrain_stamp(self, value):
        if self._check_fields:
            from builtin_interfaces.msg import Time
            assert \
                isinstance(value, Time), \
                "The 'terrain_stamp' field must be a sub message of type 'Time'"
        self._terrain_stamp = value

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

    @builtins.property
    def evaluator_version(self):
        """Message field 'evaluator_version'."""
        return self._evaluator_version

    @evaluator_version.setter
    def evaluator_version(self, value):
        if self._check_fields:
            assert \
                isinstance(value, str), \
                "The 'evaluator_version' field must be of type 'str'"
        self._evaluator_version = value
