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
    The footprint envelope must contain the chassis AND the wheels.

    The chassis is wider at mid-length than the wheels sit, while the front
    wheel reaches further forward than the chassis, so taking either alone
    understates the envelope on one axis. A footprint smaller than what Gazebo
    collides with lets nav2 plan the rover into contact.
    """
    geom = _source()
    half_x, half_y = rg.footprint_half_extents(geom)

    assert half_x >= geom['chassis_max_x']
    assert half_x >= -geom['chassis_min_x']
    assert half_x >= geom['front_wheel_x'] + geom['wheel_radius']
    assert half_x >= -geom['rear_wheel_x'] + geom['wheel_radius']

    assert half_y >= geom['chassis_half_y']
    assert half_y >= geom['wheel_y'] + geom['wheel_width'] / 2.0


def _urdf_root():
    """Return the parsed generated URDF, or skip if xacro cannot run."""
    import subprocess
    import xml.etree.ElementTree as ElementTree

    path = os.path.join(
        os.path.dirname(os.path.dirname(rg.geometry_path())),
        'urdf', 'space_rover.urdf.xacro',
    )
    assert os.path.isfile(path), f'xacro not installed at {path}'
    result = subprocess.run(
        ['xacro', path], capture_output=True, text=True, check=True
    )
    return ElementTree.fromstring(result.stdout)


def _link_offsets(root):
    """Return {link name: (x, y)} in base_link, following fixed joints."""
    offsets = {'base_link': (0.0, 0.0)}
    pending = list(root.findall('joint'))
    for _ in range(len(pending) + 1):
        for joint in list(pending):
            parent = joint.find('parent').get('link')
            child = joint.find('child').get('link')
            if parent not in offsets:
                continue
            origin = joint.find('origin')
            xyz = (origin.get('xyz', '0 0 0').split() if origin is not None
                   else ['0', '0', '0'])
            px, py = offsets[parent]
            offsets[child] = (px + float(xyz[0]), py + float(xyz[1]))
            pending.remove(joint)
    return offsets


def test_footprint_covers_every_collision():
    """
    Re-derive the envelope from the URDF, not from the derivation's own list.

    This replaces a test that checked the same two shapes
    ``footprint_half_extents`` checked, and therefore shared its blind spot: the
    camera mount reaches 0.1975 m forward, 43.8 mm beyond a footprint built from
    the chassis and wheels alone. A footprint smaller than what Gazebo collides
    with lets nav2 plan the rover into contact.

    Walking the URDF means a link added later fails here even if nobody
    remembers to update the derivation.
    """
    geom = _source()
    root = _urdf_root()
    offsets = _link_offsets(root)
    half_x, half_y = rg.footprint_half_extents(geom)

    checked = 0
    for link in root.findall('link'):
        name = link.get('name')
        base = offsets.get(name)
        if base is None:
            continue
        for collision in link.findall('collision'):
            origin = collision.find('origin')
            xyz = (origin.get('xyz', '0 0 0').split() if origin is not None
                   else ['0', '0', '0'])
            cx = base[0] + float(xyz[0])
            cy = base[1] + float(xyz[1])

            box = collision.find('geometry/box')
            cylinder = collision.find('geometry/cylinder')
            if box is not None:
                sx, sy, _ = (float(v) for v in box.get('size').split())
                reach_x, reach_y = sx / 2.0, sy / 2.0
            elif cylinder is not None:
                # Wheels are rotated onto y, so the radius spans x/z and the
                # length spans y.
                radius = float(cylinder.get('radius'))
                reach_x = radius
                reach_y = float(cylinder.get('length')) / 2.0
            else:
                continue

            checked += 1
            assert abs(cx) + reach_x <= half_x + 1e-9, (
                f'{name} reaches {abs(cx) + reach_x:.5f} m in x, beyond the '
                f'{half_x:.5f} m footprint'
            )
            assert abs(cy) + reach_y <= half_y + 1e-9, (
                f'{name} reaches {abs(cy) + reach_y:.5f} m in y, beyond the '
                f'{half_y:.5f} m footprint'
            )

    assert checked >= 6, f'only found {checked} collision shapes, expected 6+'


def test_collision_box_is_not_narrower_than_the_chassis():
    """
    The collision box must cover the chassis laterally.

    The box it replaces was 13 mm too narrow. Over-size is merely conservative;
    under-size lets Gazebo pass the rover through gaps it would physically hit,
    and judging passable gaps is part of the mission -- so this is the assertion
    that matters most about the box.
    """
    geom = _source()
    _, width, _ = rg.chassis_box_size(geom)
    assert width >= 2.0 * geom['chassis_half_y'] - 1e-12


def test_collision_box_does_not_clip_the_ground():
    """
    The box underside must sit at or above the contact plane.

    A box reaching the mesh minimum would dip 8 mm below it and the rover would
    rest on its chassis instead of its wheels, which changes every contact
    result in the simulation.
    """
    geom = _source()
    _, _, height = rg.chassis_box_size(geom)
    _, _, origin_z = rg.chassis_box_origin(geom)
    underside_ground = (
        rg.base_link_height(geom) + origin_z - height / 2.0
    )
    assert underside_ground >= 0.0
    # And it should sit exactly at the measured clearance, not above it.
    assert underside_ground == pytest.approx(geom['chassis_ground_clearance'])


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


def test_ground_clearance_stays_well_under_the_axle_height():
    """
    Clearance must come from the mesh, and stay physically plausible.

    The old collision box implied 0.084 m against a real 0.030 m -- 2.76x too
    optimistic, and clearance decides whether the rover straddles a rock or
    bellies out. Bounding it by the axle height catches anyone "tidying" it back
    to a primitive-derived figure: a chassis cannot hang higher than the axles it
    is mounted on.
    """
    geom = _source()
    axle_height = rg.base_link_height(geom) + geom['wheel_z']
    assert 0.0 < geom['chassis_ground_clearance'] < axle_height


def test_masses_sum_to_the_recorded_total():
    """
    The parts must add up to ``mass_total``, by construction.

    They did not before: the URDF summed to 2.450 kg against a 2.725 kg design
    estimate, so the simulated rover was 10.1% light. For a mission whose
    signature measurement is slip, a light rover slips less, climbs better, and
    finds more traction than the real one -- a validation run on it validates
    nothing.
    """
    geom = _source()
    parts = (
        rg.mass_base(geom)
        + rg.WHEEL_COUNT * geom['mass_wheel']
        + geom['mass_camera']
        + geom['mass_imu']
    )
    assert parts == pytest.approx(geom['mass_total'])


def test_design_mass_stays_under_the_competition_limit():
    """
    ``mass_total`` is a design estimate; ``mass_limit`` is a hard ceiling.

    They were previously conflated -- the 3.0 kg limit was being used as the
    design figure. If a future estimate exceeds the ceiling, that is a
    disqualification, so it fails here rather than being discovered later.
    """
    geom = _source()
    assert geom['mass_total'] <= geom['mass_limit']
    assert rg.mass_base(geom) > 0.0, 'components already exceed the total'


def test_base_inertia_scales_with_the_derived_mass():
    """
    Inertia is linear in mass for a fixed shape, so it must track ``mass_base``.

    A fixed triple would keep describing the old 1.8 kg chassis while the mass
    around it changed.
    """
    geom = _source()
    ixx, iyy, izz = rg.base_inertia(geom)
    mass = rg.mass_base(geom)
    per_kg = geom['base_inertia_per_kg']

    assert ixx == pytest.approx(per_kg['ixx'] * mass)
    assert iyy == pytest.approx(per_kg['iyy'] * mass)
    assert izz == pytest.approx(per_kg['izz'] * mass)
    # izz > iyy > ixx for a body longer than it is wide and wider than tall.
    assert izz > iyy > ixx


def test_ground_pressure_tracks_the_design_mass():
    """
    Ground pressure must be derived, not typed.

    It was hand-written as 3.47 kPa, computed from the 3.0 kg competition
    ceiling rather than the design estimate, so it overstated the load the soil
    actually sees.
    """
    geom = _source()
    expected = (
        geom['mass_total'] * rg.GRAVITY
        / rg.contact_patch_area(geom) / 1000.0
    )
    assert rg.ground_pressure_kpa(geom) == pytest.approx(expected)
    assert 1.0 < rg.ground_pressure_kpa(geom) < 20.0, 'implausible for 2.7 kg'


def test_generated_urdf_total_mass_equals_the_source():
    """
    Sum the masses out of the generated URDF, not out of the derivation.

    Checking the derivation against itself would pass even if the xacro forgot
    to consume it. This runs xacro and adds up what the simulator will actually
    load, which is the only number that affects physics.
    """
    import subprocess
    import xml.etree.ElementTree as ElementTree

    geom = _source()
    urdf_path = os.path.join(
        os.path.dirname(os.path.dirname(rg.geometry_path())),
        'urdf', 'space_rover.urdf.xacro',
    )
    assert os.path.isfile(urdf_path), f'xacro not installed at {urdf_path}'

    result = subprocess.run(
        ['xacro', urdf_path], capture_output=True, text=True, check=True
    )
    root = ElementTree.fromstring(result.stdout)
    total = sum(
        float(mass.get('value'))
        for mass in root.findall('link/inertial/mass')
    )

    assert total == pytest.approx(geom['mass_total'])
    assert total <= geom['mass_limit']


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
