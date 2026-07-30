"""
Load rover geometry from the single source and derive everything else from it.

Pure and ROS-free apart from locating the installed share directory, so the
derivations can be unit-tested without a graph.

Why derivations live in code and not in config
----------------------------------------------
The CAD import in 51b34ac changed the wheel radius from 0.112 m to 0.070 m and
silently invalidated four values in four packages, because each had copied the
radius into its own config:

    space_mission/config/slip.yaml        wheel_radius -> slip ratios 1.6x high
    space_mission slip_estimator_node.py  the same default, the same effect
    space_perception TraversabilityConfig step_max = half the OLD radius
    space_bringup nav2_params.yaml        footprints sized to the old chassis

Every one failed quietly: the arithmetic downstream still succeeded and the
outputs still looked plausible. Storing a derived value is what made that
possible, so nothing derivable is stored -- it is computed here, from
``config/rover_geometry.yaml``, at load time.

This module belongs to ``space_description`` because that package owns the
rover's physical description and depends on nothing. Any consumer can import it
without inverting the dependency graph.
"""

import math
import os

import yaml


PACKAGE_NAME = 'space_description'
GEOMETRY_RELATIVE_PATH = os.path.join('config', 'rover_geometry.yaml')

#: Keys that must be present. Listed explicitly so a truncated or hand-edited
#: source file fails loudly at load instead of surfacing as a wrong map later.
REQUIRED_KEYS = (
    'wheel_radius',
    'wheel_width',
    'front_wheel_x',
    'rear_wheel_x',
    'wheel_y',
    'wheel_z',
    'chassis_min_x',
    'chassis_max_x',
    'chassis_half_y',
    'chassis_top_z',
    'chassis_ground_clearance',
    'camera_mount_x',
    'camera_collision_length',
    'camera_collision_width',
    'mass_total',
    'mass_limit',
    'mass_wheel',
    'mass_camera',
    'mass_imu',
    'base_inertia_per_kg',
    'assumed_sinkage',
    'step_limit_per_wheel_radius',
    'passable_width_margin',
)

#: Wheels on the rover. Named rather than hard-coded as 4 at each use site.
WHEEL_COUNT = 4

GRAVITY = 9.81


def geometry_path():
    """
    Return the installed path of the geometry source file.

    Resolved from the ament index rather than from ``__file__`` so the answer is
    the same whether the caller is a node, a launch file, or a test.
    """
    from ament_index_python.packages import get_package_share_directory
    return os.path.join(
        get_package_share_directory(PACKAGE_NAME), GEOMETRY_RELATIVE_PATH
    )


def load_geometry(path=None):
    """
    Read the geometry source file and validate that it is complete.

    Raises ``KeyError`` listing every missing key, rather than defaulting. A
    silently defaulted dimension is precisely the failure this module exists to
    prevent: it would produce a plausible number for a rover that does not
    exist.
    """
    if path is None:
        path = geometry_path()
    with open(path, 'r', encoding='utf-8') as handle:
        geom = yaml.safe_load(handle)
    if not isinstance(geom, dict):
        raise ValueError(f'{path} did not parse to a mapping')
    missing = [key for key in REQUIRED_KEYS if key not in geom]
    if missing:
        raise KeyError(f'{path} is missing required keys: {sorted(missing)}')
    return geom


def max_step_height(geom):
    """
    Return the tallest step the wheels clear unaided, in metres.

    ``docs/traversability.md`` fixed the rule at half the wheel radius. Keeping
    it as a ratio times the single-source radius is what stops it going stale:
    ``step_max`` was 0.056 -- half of 0.112 -- and stayed 0.056 after the wheel
    became 0.070, judging steps against a rover 1.6x more capable than ours.
    """
    return geom['wheel_radius'] * geom['step_limit_per_wheel_radius']


def wheel_separation(geom):
    """Return the lateral distance between left and right wheel centres."""
    return 2.0 * geom['wheel_y']


def track_width(geom):
    """Return the rover's overall width across the outer tyre faces."""
    return 2.0 * (geom['wheel_y'] + geom['wheel_width'] / 2.0)


def wheelbase(geom):
    """Return the longitudinal distance between front and rear axles."""
    return geom['front_wheel_x'] - geom['rear_wheel_x']


def base_link_height(geom):
    """
    Return the height of ``base_link`` above ``base_footprint``.

    Equals ``wheel_radius - wheel_z``, which is what puts the wheel contact
    patch exactly on the ``base_footprint`` plane.
    """
    return geom['wheel_radius'] - geom['wheel_z']


def chassis_box_size(geom):
    """
    Return the collision box ``(length, width, height)`` for ``base_link``.

    Spans the measured chassis extents laterally and longitudinally, and
    vertically from the ground clearance to the chassis top. It stops at the
    clearance rather than the mesh minimum because a box reaching the mesh
    minimum dips 8 mm below the ground plane, which would rest the rover on its
    chassis instead of its wheels.
    """
    return (
        geom['chassis_max_x'] - geom['chassis_min_x'],
        2.0 * geom['chassis_half_y'],
        geom['chassis_top_z'] - geom['chassis_ground_clearance'],
    )


def chassis_box_origin(geom):
    """
    Return the collision box centre ``(x, y, z)`` expressed in ``base_link``.

    The chassis is not centred on ``base_link``: the axles sit forward of the
    body centre, so the box needs an explicit offset. The old box was centred
    implicitly, which is part of why it misrepresented the envelope.
    """
    centre_x = (geom['chassis_min_x'] + geom['chassis_max_x']) / 2.0
    centre_ground_z = (
        geom['chassis_ground_clearance'] + geom['chassis_top_z']
    ) / 2.0
    return centre_x, 0.0, centre_ground_z - base_link_height(geom)


def footprint_half_extents(geom):
    """
    Return ``(half_x, half_y)`` of the rover's collision envelope, in metres.

    The union of EVERY collision shape, not just the obvious ones. Each of the
    three contributes the maximum on some axis: the chassis is wider at
    mid-length than the wheels sit, the front wheel reaches further forward than
    the chassis, and the camera mount reaches further forward than either.
    Omitting the camera left this 43.8 mm short of what Gazebo actually collides
    with -- the dangerous direction, because nav2 would then plan the rover into
    contact.

    ``test_footprint_covers_every_collision`` re-derives this by parsing the
    generated URDF rather than by repeating the list below, so a link added
    later fails the test even though this function was not touched. That is the
    point: the previous guard test checked the same two shapes the derivation
    did, so it shared the blind spot instead of catching it.
    """
    half_x = max(
        geom['chassis_max_x'],
        -geom['chassis_min_x'],
        geom['front_wheel_x'] + geom['wheel_radius'],
        -geom['rear_wheel_x'] + geom['wheel_radius'],
        geom['camera_mount_x'] + geom['camera_collision_length'] / 2.0,
    )
    half_y = max(
        geom['chassis_half_y'],
        track_width(geom) / 2.0,
        geom['camera_collision_width'] / 2.0,
    )
    return half_x, half_y


def mass_base(geom):
    """
    Return the ``base_link`` mass, as the remainder of the total.

    Derived rather than configured. ``mass_total`` is the constrained quantity
    and the chassis is the least-known component, so the chassis absorbs the
    balance. Letting the parts define the total is exactly how the URDF came to
    sum to 2.450 kg against a 2.725 kg design estimate.
    """
    return (
        geom['mass_total']
        - WHEEL_COUNT * geom['mass_wheel']
        - geom['mass_camera']
        - geom['mass_imu']
    )


def base_inertia(geom):
    """
    Return ``base_link``'s inertia as ``(ixx, iyy, izz)``, scaled to its mass.

    Inertia is linear in mass for a fixed shape, so the per-kilogram triple in
    the source times the derived mass keeps the two consistent. A fixed triple
    would silently keep describing the old 1.8 kg chassis.
    """
    per_kg = geom['base_inertia_per_kg']
    mass = mass_base(geom)
    return tuple(per_kg[axis] * mass for axis in ('ixx', 'iyy', 'izz'))


def contact_patch_area(geom):
    """
    Return the total tyre-ground contact area, in square metres.

    Rigid-wheel-on-soft-soil approximation: a wheel sunk by ``assumed_sinkage``
    contacts over a chord of ``2*sqrt(2*R*z)``. The sinkage is a guess, which
    makes this the weakest quantity derived here.
    """
    chord = 2.0 * math.sqrt(
        2.0 * geom['wheel_radius'] * geom['assumed_sinkage']
    )
    return chord * geom['wheel_width'] * WHEEL_COUNT


def ground_pressure_kpa(geom):
    """
    Return static ground pressure in kPa, from the total mass and contact patch.

    Derived so it tracks the mass. It was hand-written as 3.47 kPa, computed
    from the 3.0 kg competition ceiling rather than the 2.725 kg design
    estimate.
    """
    force = geom['mass_total'] * GRAVITY
    return force / contact_patch_area(geom) / 1000.0


def footprint_string(geom):
    """
    Return the collision envelope as the string nav2's ``footprint`` expects.

    nav2 parses this parameter as a string, so it is formatted here rather than
    hand-written into ``nav2_params.yaml`` where it could not track the CAD.
    """
    half_x, half_y = footprint_half_extents(geom)
    corners = (
        (half_x, half_y), (half_x, -half_y), (-half_x, -half_y), (-half_x, half_y)
    )
    inner = ', '.join(f'[{x:.5f}, {y:.5f}]' for x, y in corners)
    return f'[{inner}]'


def min_passable_width(geom):
    """
    Return the narrowest gap the rover should be planned through.

    Its own width plus a margin: a skid-steer yaws while translating, so it
    sweeps wider than its static outline.
    """
    return track_width(geom) + geom['passable_width_margin']


def derived(geom):
    """
    Return every derived quantity as a mapping, for callers that want them all.

    Used by launch files to inject overrides, so that the list of things derived
    from the CAD has exactly one definition.
    """
    half_x, half_y = footprint_half_extents(geom)
    box_x, box_y, box_z = chassis_box_size(geom)
    origin_x, origin_y, origin_z = chassis_box_origin(geom)
    ixx, iyy, izz = base_inertia(geom)
    return {
        'max_step_height': max_step_height(geom),
        'wheel_separation': wheel_separation(geom),
        'track_width': track_width(geom),
        'wheelbase': wheelbase(geom),
        'base_link_height': base_link_height(geom),
        'footprint_half_x': half_x,
        'footprint_half_y': half_y,
        'footprint_string': footprint_string(geom),
        'min_passable_width': min_passable_width(geom),
        'chassis_box_length': box_x,
        'chassis_box_width': box_y,
        'chassis_box_height': box_z,
        'chassis_box_origin_x': origin_x,
        'chassis_box_origin_y': origin_y,
        'chassis_box_origin_z': origin_z,
        'mass_base': mass_base(geom),
        'base_inertia_ixx': ixx,
        'base_inertia_iyy': iyy,
        'base_inertia_izz': izz,
        'contact_patch_area': contact_patch_area(geom),
        'ground_pressure_kpa': ground_pressure_kpa(geom),
    }
