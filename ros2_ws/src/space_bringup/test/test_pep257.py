"""Run pydocstyle for the bringup package."""

from ament_pep257.main import main
import pytest


@pytest.mark.linter
@pytest.mark.pep257
def test_pep257():
    """Check Python docstring style."""
    assert main(argv=['.']) == 0
