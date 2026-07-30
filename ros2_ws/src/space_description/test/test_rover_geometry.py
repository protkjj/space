"""
Guard the single source of truth for rover geometry.

These tests exist because of a specific failure. The CAD import in 51b34ac
changed the wheel radius from 0.112 m to 0.070 m, and four values derived from
it across four packages silently kept the old numbers -- slip ratios ran 1.6x
high, traversability judged steps against a rover 1.6x more capable than ours,
and the nav2 footprint described the previous chassis. Every one of them failed
quietly, because the arithmetic downstream still succeeded and the outputs still
looked plausible.

So the point of this file is not to check arithmetic. It is to make the NEXT CAD
change loud: if a dimension moves and a derived value does not follow, something
here fails.
"""

import math
import os

import pytest
from space_description import rover_geometry as rg
import yaml


def _source():
    return rg.load_geometry()


def test_geometry_source_is_installed():
    """The source file must be found through the ament index, not by guessing."""
    path = rg.geometry_path()
    assert os.path.isfile(path), f'geometry source missing at {path}'


def test_every_required_key_is_present():
    """A truncated source must fail at load, not surface later as a wrong map."""
    geom = _source()
    missing = [key for key in rg.REQUIRED_KEYS if key not in geom]
    assert missing == []


def _load_from_mapping(geom):
    """Write ``geom`` to a temp file and load it, so validation runs on it."""
    import tempfile
    with tempfile.NamedTemporaryFile(
        'w', suffix='.yaml', delete=False, encoding='utf-8'
    ) as handle:
        yaml.safe_dump(geom, handle)
        name = handle.name
    try:
        return rg.load_geometry(name)
    finally:
        os.unlink(name)


def test_missing_key_raises_rather_than_defaulting():
    """
    Dropping a key must raise.

    A silently defaulted dimension is the exact failure mode the single source
    exists to prevent: it produces a confident number for a rover that does not
    exist.
    """
    geom = _source()
    del geom['wheel_radius']
    with pytest.raises(KeyError):
        _load_from_mapping(geom)


def test_complete_mapping_round_trips():
    """The temp-file helper must accept a valid source, or the test above lies."""
    assert _load_from_mapping(_source())['wheel_radius'] > 0.0


def test_step_limit_is_half_the_wheel_radius():
    """
    docs/traversability.md fixes the step limit at half the wheel radius.

    Encoded as a ratio times the single-source radius so it cannot go stale
    independently of the wheel it describes.
    """
    geom = _source()
    assert rg.max_step_height(geom) == pytest.approx(
        geom['wheel_radius'] * 0.5
    )


def test_wheel_contact_lands_exactly_on_base_footprint():
    """
    The wheel bottom must sit at z = 0 in ``base_footprint``, for any wheel size.

    base_link sits ``wheel_radius - wheel_z`` up and each wheel centre ``wheel_z``
    from base_link, so the contact point is identically zero. Two documentation
    sites claimed -0.005 m, which was the pre-CAD value.
    """
    geom = _source()
    contact = rg.base_link_height(geom) + geom['wheel_z'] - geom['wheel_radius']
    assert contact == pytest.approx(0.0, abs=1e-12)


def test_footprint_covers_both_chassis_box_and_wheels():
    """
    The footprint envelope must contain the collision box AND the wheels.

    The box is longer than the wheels reach but narrower than they sit, so
    taking either alone understates the envelope on one axis. A footprint
    smaller than what Gazebo collides with lets nav2 plan the rover into
    contact.
    """
    geom = _source()
    half_x, half_y = rg.footprint_half_extents(geom)

    assert half_x >= geom['base_length'] / 2.0
    assert half_x >= geom['front_wheel_x'] + geom['wheel_radius']
    assert half_x >= -geom['rear_wheel_x'] + geom['wheel_radius']

    assert half_y >= geom['base_width'] / 2.0
    assert half_y >= geom['wheel_y'] + geom['wheel_width'] / 2.0


def test_footprint_string_parses_to_the_derived_extents():
    """nav2 receives this as a string, so round-trip it rather than trust it."""
    geom = _source()
    half_x, half_y = rg.footprint_half_extents(geom)
    corners = yaml.safe_load(rg.footprint_string(geom))

    assert len(corners) == 4
    assert sorted(abs(x) for x, _ in corners) == pytest.approx([half_x] * 4)
    assert sorted(abs(y) for _, y in corners) == pytest.approx([half_y] * 4)
    # All four sign combinations must appear, or it is not a rectangle.
    assert {(x > 0, y > 0) for x, y in corners} == {
        (True, True), (True, False), (False, True), (False, False)
    }


def test_min_passable_width_exceeds_the_rover_width():
    """A skid-steer yaws while translating, so it sweeps wider than it stands."""
    geom = _source()
    assert rg.min_passable_width(geom) > rg.track_width(geom)


def test_ground_clearance_is_below_the_collision_box_underside():
    """
    Clearance must come from the mesh, not the collision primitive.

    The box implies 0.084 m; the real chassis has 0.030 m. Asserting the
    measured value stays under the box-derived one keeps anyone from "tidying"
    it back to the primitive, which would claim 2.76x the clearance the vehicle
    has -- and clearance decides whether it straddles a rock or bellies out.
    """
    geom = _source()
    box_underside = rg.base_link_height(geom) - geom['base_height'] / 2.0
    assert geom['chassis_ground_clearance'] < box_underside


def test_derived_mapping_matches_the_individual_functions():
    """``derived()`` is what launch files inject, so it must not drift."""
    geom = _source()
    derived = rg.derived(geom)

    assert derived['max_step_height'] == rg.max_step_height(geom)
    assert derived['wheel_separation'] == rg.wheel_separation(geom)
    assert derived['track_width'] == rg.track_width(geom)
    assert derived['wheelbase'] == rg.wheelbase(geom)
    assert derived['base_link_height'] == rg.base_link_height(geom)
    assert derived['min_passable_width'] == rg.min_passable_width(geom)
    assert derived['footprint_string'] == rg.footprint_string(geom)


def test_wheel_geometry_matches_the_measured_wheel_stl():
    """
    The recorded wheel must still match the mesh it was measured from.

    A CAD re-export that changes the wheel without updating the YAML would
    otherwise leave every derived threshold describing the previous wheel --
    exactly what happened last time, just in the other direction.
    """
    import struct

    geom = _source()
    # geometry_path() is <share>/config/rover_geometry.yaml, so the package
    # share root is two levels up, not one.
    share_root = os.path.dirname(os.path.dirname(rg.geometry_path()))
    mesh = os.path.join(share_root, 'meshes', 'rover', 'left_front_wheel.stl')
    assert os.path.isfile(mesh), (
        f'wheel mesh not found at {mesh}; this test must not silently skip, '
        'it is the only check that the recorded wheel still matches the CAD'
    )

    with open(mesh, 'rb') as handle:
        handle.read(80)
        count = struct.unpack('<I', handle.read(4))[0]
        payload = handle.read(count * 50)

    lo = [math.inf] * 3
    hi = [-math.inf] * 3
    for triangle in range(count):
        base = triangle * 50 + 12
        for vertex in range(3):
            for axis in range(3):
                value = struct.unpack_from(
                    '<f', payload, base + vertex * 12 + axis * 4
                )[0]
                lo[axis] = min(lo[axis], value)
                hi[axis] = max(hi[axis], value)

    spans_m = sorted((hi[axis] - lo[axis]) / 1000.0 for axis in range(3))
    width, diameter = spans_m[0], spans_m[2]

    assert width == pytest.approx(geom['wheel_width'], abs=5e-4)
    assert diameter == pytest.approx(2.0 * geom['wheel_radius'], abs=5e-4)
