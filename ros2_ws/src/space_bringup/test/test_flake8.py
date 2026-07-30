"""Run flake8 for the bringup package."""

from ament_flake8.main import main_with_errors
import pytest


@pytest.mark.flake8
@pytest.mark.linter
def test_flake8():
    """Check Python style."""
    # Exclude colcon's generated prefix_override/sitecustomize.py. It is not
    # our code, it is gitignored, and its only "violation" is that it embeds the
    # absolute install path -- so the check passes or fails depending on how long
    # the checkout directory happens to be.
    return_code, errors = main_with_errors(
        argv=['--exclude', 'prefix_override']
    )
    assert return_code == 0, '\n'.join(errors)
