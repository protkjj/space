# generated from rosidl_generator_py/resource/_idl.py.em
# with input from space_msgs:msg/RoverSpec.idl
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


class Metaclass_RoverSpec(type):
    """Metaclass of message 'RoverSpec'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
        'PROVENANCE_UNKNOWN': 0,
        'PROVENANCE_MEASURED': 1,
        'PROVENANCE_ASSUMED': 2,
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
                'space_msgs.msg.RoverSpec')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__rover_spec
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__rover_spec
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__rover_spec
            cls._TYPE_SUPPORT = module.type_support_msg__msg__rover_spec
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__rover_spec

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
            'PROVENANCE_UNKNOWN': cls.__constants['PROVENANCE_UNKNOWN'],
            'PROVENANCE_MEASURED': cls.__constants['PROVENANCE_MEASURED'],
            'PROVENANCE_ASSUMED': cls.__constants['PROVENANCE_ASSUMED'],
        }

    @property
    def PROVENANCE_UNKNOWN(self):
        """Message constant 'PROVENANCE_UNKNOWN'."""
        return Metaclass_RoverSpec.__constants['PROVENANCE_UNKNOWN']

    @property
    def PROVENANCE_MEASURED(self):
        """Message constant 'PROVENANCE_MEASURED'."""
        return Metaclass_RoverSpec.__constants['PROVENANCE_MEASURED']

    @property
    def PROVENANCE_ASSUMED(self):
        """Message constant 'PROVENANCE_ASSUMED'."""
        return Metaclass_RoverSpec.__constants['PROVENANCE_ASSUMED']


class RoverSpec(metaclass=Metaclass_RoverSpec):
    """
    Message class 'RoverSpec'.

    Constants:
      PROVENANCE_UNKNOWN
      PROVENANCE_MEASURED
      PROVENANCE_ASSUMED
    """

    __slots__ = [
        '_rover_id',
        '_mass_kg',
        '_wheel_radius_m',
        '_wheel_width_m',
        '_ground_pressure_kpa',
        '_max_climb_angle_rad',
        '_min_passable_width_m',
        '_ground_clearance_m',
        '_has_grousers',
        '_provenance',
        '_provenance_note',
        '_check_fields',
    ]

    _fields_and_field_types = {
        'rover_id': 'string',
        'mass_kg': 'float',
        'wheel_radius_m': 'float',
        'wheel_width_m': 'float',
        'ground_pressure_kpa': 'float',
        'max_climb_angle_rad': 'float',
        'min_passable_width_m': 'float',
        'ground_clearance_m': 'float',
        'has_grousers': 'boolean',
        'provenance': 'uint8',
        'provenance_note': 'string',
    }

    # This attribute is used to store an rosidl_parser.definition variable
    # related to the data type of each of the components the message.
    SLOT_TYPES = (
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
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
        self.rover_id = kwargs.get('rover_id', str())
        self.mass_kg = kwargs.get('mass_kg', float())
        self.wheel_radius_m = kwargs.get('wheel_radius_m', float())
        self.wheel_width_m = kwargs.get('wheel_width_m', float())
        self.ground_pressure_kpa = kwargs.get('ground_pressure_kpa', float())
        self.max_climb_angle_rad = kwargs.get('max_climb_angle_rad', float())
        self.min_passable_width_m = kwargs.get('min_passable_width_m', float())
        self.ground_clearance_m = kwargs.get('ground_clearance_m', float())
        self.has_grousers = kwargs.get('has_grousers', bool())
        self.provenance = kwargs.get('provenance', int())
        self.provenance_note = kwargs.get('provenance_note', str())

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
        if self.rover_id != other.rover_id:
            return False
        if self.mass_kg != other.mass_kg:
            return False
        if self.wheel_radius_m != other.wheel_radius_m:
            return False
        if self.wheel_width_m != other.wheel_width_m:
            return False
        if self.ground_pressure_kpa != other.ground_pressure_kpa:
            return False
        if self.max_climb_angle_rad != other.max_climb_angle_rad:
            return False
        if self.min_passable_width_m != other.min_passable_width_m:
            return False
        if self.ground_clearance_m != other.ground_clearance_m:
            return False
        if self.has_grousers != other.has_grousers:
            return False
        if self.provenance != other.provenance:
            return False
        if self.provenance_note != other.provenance_note:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

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
    def mass_kg(self):
        """Message field 'mass_kg'."""
        return self._mass_kg

    @mass_kg.setter
    def mass_kg(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'mass_kg' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'mass_kg' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._mass_kg = value

    @builtins.property
    def wheel_radius_m(self):
        """Message field 'wheel_radius_m'."""
        return self._wheel_radius_m

    @wheel_radius_m.setter
    def wheel_radius_m(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'wheel_radius_m' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'wheel_radius_m' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._wheel_radius_m = value

    @builtins.property
    def wheel_width_m(self):
        """Message field 'wheel_width_m'."""
        return self._wheel_width_m

    @wheel_width_m.setter
    def wheel_width_m(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'wheel_width_m' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'wheel_width_m' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._wheel_width_m = value

    @builtins.property
    def ground_pressure_kpa(self):
        """Message field 'ground_pressure_kpa'."""
        return self._ground_pressure_kpa

    @ground_pressure_kpa.setter
    def ground_pressure_kpa(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'ground_pressure_kpa' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'ground_pressure_kpa' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._ground_pressure_kpa = value

    @builtins.property
    def max_climb_angle_rad(self):
        """Message field 'max_climb_angle_rad'."""
        return self._max_climb_angle_rad

    @max_climb_angle_rad.setter
    def max_climb_angle_rad(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'max_climb_angle_rad' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'max_climb_angle_rad' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._max_climb_angle_rad = value

    @builtins.property
    def min_passable_width_m(self):
        """Message field 'min_passable_width_m'."""
        return self._min_passable_width_m

    @min_passable_width_m.setter
    def min_passable_width_m(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'min_passable_width_m' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'min_passable_width_m' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._min_passable_width_m = value

    @builtins.property
    def ground_clearance_m(self):
        """Message field 'ground_clearance_m'."""
        return self._ground_clearance_m

    @ground_clearance_m.setter
    def ground_clearance_m(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'ground_clearance_m' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'ground_clearance_m' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._ground_clearance_m = value

    @builtins.property
    def has_grousers(self):
        """Message field 'has_grousers'."""
        return self._has_grousers

    @has_grousers.setter
    def has_grousers(self, value):
        if self._check_fields:
            assert \
                isinstance(value, bool), \
                "The 'has_grousers' field must be of type 'bool'"
        self._has_grousers = value

    @builtins.property
    def provenance(self):
        """Message field 'provenance'."""
        return self._provenance

    @provenance.setter
    def provenance(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'provenance' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'provenance' field must be an unsigned integer in [0, 255]"
        self._provenance = value

    @builtins.property
    def provenance_note(self):
        """Message field 'provenance_note'."""
        return self._provenance_note

    @provenance_note.setter
    def provenance_note(self, value):
        if self._check_fields:
            assert \
                isinstance(value, str), \
                "The 'provenance_note' field must be of type 'str'"
        self._provenance_note = value
