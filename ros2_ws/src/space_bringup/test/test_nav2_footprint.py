"""
Guard the nav2 footprint against the rover CAD.

nav2 requires a footprint to be present in its params file, so the value cannot
simply be deleted the way ``step_max`` was removed from
``terrain_perception.yaml``. That leaves a copy, and a copy is what went stale:
both costmaps carried footprints sized to the pre-51b34ac chassis, oversized by
up to 60 mm against the rover we actually have.

An oversized footprint is not "safely conservative" here. The mission includes
deciding whether gaps are passable, so inflating the outline throws away routes
the rover can physically take -- a loss of capability, not a safety margin.

``simulation.launch.py`` overwrites the value from the CAD at launch, so runtime
is already correct. These tests exist so the file itself cannot mislead anyone
reading it, and so the next CAD change fails loudly instead of quietly.
"""

import os

from ament_index_python.packages import get_package_share_directory
import pytest
from space_description.rover_geometry import (
    footprint_half_extents,
    footprint_string,
    load_geometry,
)
import yaml


COSTMAPS = ('local_costmap', 'global_costmap')


def _nav2_params():
    path = os.path.join(
        get_package_share_directory('space_bringup'),
        'config', 'navigation', 'nav2_params.yaml',
    )
    with open(path, 'r', encoding='utf-8') as handle:
        return yaml.safe_load(handle)


@pytest.mark.parametrize('costmap', COSTMAPS)
def test_footprint_matches_the_rover_cad(costmap):
    """
    Each costmap's footprint must equal the envelope derived from the CAD.

    If this fails, a rover dimension moved and this copy did not follow. Correct
    the YAML from space_description/config/rover_geometry.yaml; do not relax the
    assertion.
    """
    params = _nav2_params()
    written = params[costmap][costmap]['ros__parameters']['footprint']
    assert yaml.safe_load(written) == yaml.safe_load(
        footprint_string(load_geometry())
    )


@pytest.mark.parametrize('costmap', COSTMAPS)
def test_footprint_is_not_smaller_than_the_collision_envelope(costmap):
    """
    The footprint must never be tighter than what Gazebo actually collides with.

    Undersizing is the dangerous direction: nav2 would plan the rover into
    contact. Checked separately from equality so the intent survives even if the
    derivation changes.
    """
    geom = load_geometry()
    half_x, half_y = footprint_half_extents(geom)
    corners = yaml.safe_load(
        _nav2_params()[costmap][costmap]['ros__parameters']['footprint']
    )

    # An explicit tolerance rather than pytest.approx: approx objects do not
    # support ordering comparisons, and silently comparing against one would
    # raise instead of asserting.
    tolerance = 1e-9
    assert max(abs(x) for x, _ in corners) >= half_x - tolerance
    assert max(abs(y) for _, y in corners) >= half_y - tolerance


@pytest.mark.parametrize('costmap', COSTMAPS)
def test_robot_radius_does_not_shadow_the_footprint(costmap):
    """
    ``robot_radius`` must stay unset, because nav2 prefers it over ``footprint``.

    A stray radius would silently reinstate a circular outline and make every
    assertion above meaningless while still passing.
    """
    params = _nav2_params()[costmap][costmap]['ros__parameters']
    assert 'robot_radius' not in params
