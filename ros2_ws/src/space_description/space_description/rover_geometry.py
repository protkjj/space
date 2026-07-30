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
    'base_length',
    'base_width',
    'base_height',
    'chassis_ground_clearance',
    'mass_total',
    'mass_base',
    'mass_wheel',
    'step_limit_per_wheel_radius',
    'passable_width_margin',
)


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


def footprint_half_extents(geom):
    """
    Return ``(half_x, half_y)`` of the rover's collision envelope, in metres.

    The union of the chassis collision box and the four wheel cylinders, not
    either alone: the box is longer than the wheels reach but narrower than they
    sit, so taking one of them alone understates the envelope on one axis. nav2
    plans against this, and a footprint smaller than what Gazebo collides with
    would let the planner route the rover into contact.
    """
    half_x = max(
        geom['base_length'] / 2.0,
        geom['front_wheel_x'] + geom['wheel_radius'],
        -geom['rear_wheel_x'] + geom['wheel_radius'],
    )
    half_y = max(geom['base_width'] / 2.0, track_width(geom) / 2.0)
    return half_x, half_y


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
    }
