"""
Soil-property proxy: lambda measured by our rover -> a terrain difficulty RANK.

PLACEHOLDER. Swap this module, not its callers.
====================================================
Everything here is provisional. CLAUDE.md 4 forbids a real terramechanics
model before we have field data, for the same reason it puts geometry first:
a sophisticated model fitted to nothing is worse than a crude one that is
honest about being crude.

The output is a RANK, not a measurement. "This cell is harder than that cell"
is the only claim it supports. An absolute soil property, a bearing strength
in kPa, or a number comparable across missions is NOT. Consumers must never
threshold it against a physical constant.

This module is deliberately the whole estimation layer, isolated behind two
functions, so replacing it with a calibrated model touches nothing else.
:data:`SOIL_MODEL_ID` and :data:`SOIL_MODEL_VERSION` are stamped into every
``space_msgs/TerrainEstimate``, which is what lets old records be re-derived
once a real model exists.

Non-circularity
---------------
lambda enters here already gated on quality (see :func:`accepts_sample`). The
gate must run BEFORE estimation, never after: a low-confidence lambda that
reaches the soil proxy corrupts the estimation layer, and because both
S_small and S_medium derive from that layer, one bad input breaks both maps at
once. Gating at the score stage would be too late.
"""

#: Stamped into TerrainEstimate. Bump the version on any change to the
#: arithmetic below; change the id when the model is genuinely replaced.
SOIL_MODEL_ID = 'relative_difficulty_placeholder'
SOIL_MODEL_VERSION = '0.1.0'


def accepts_sample(slip_quality, min_slip_quality):
    """
    Return whether a lambda sample may enter the estimation layer.

    Applied before :func:`estimate_soil_difficulty`, per the module note: a
    rejected sample must not reach the soil proxy at all.
    """
    raise NotImplementedError


def estimate_soil_difficulty(slip_small, slope_rad, spec):
    """
    Return a relative terrain-difficulty index in ``[0, 1]``, or ``None``.

    ``None`` means "not estimable here" -- too few accepted samples, or inputs
    that do not support a comparison. Callers write NaN into the grid for those
    cells, distinct from a measured zero.

    Intent of the placeholder arithmetic: compare the lambda actually observed
    against the lambda that slope alone would explain for a rover of this
    ``spec``. Slipping 30% on a 25 deg slope says little about the soil;
    slipping 30% on flat ground says a great deal. What survives that
    comparison is the soil's contribution, which is what we want to rank.

    ``spec`` is the rover that DID the measuring (ours), not the rover being
    evaluated. lambda is a terrain x rover interaction, so removing our own
    rover's contribution is precisely what makes the residue reusable for
    scoring a different rover.
    """
    raise NotImplementedError


def estimate_soil_confidence(sample_count, mean_slip_quality):
    """
    Return confidence in a cell's soil estimate, ``[0, 1]``.

    Must rise with ``sample_count``: a cell crossed once and a cell crossed
    three times are not equally trustworthy, and the whole point of a rover
    that drives on the terrain is that confidence accumulates as it works.
    A model that ignored sample count would report the same confidence on the
    first pass as on the tenth.

    ``mean_slip_quality`` folds in how good those samples were, so three poor
    crossings do not outrank one clean one.
    """
    raise NotImplementedError
