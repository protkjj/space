#!/usr/bin/env python3
"""
Quantify how far the rover's measured slope is from the arena's true slope.

This is the one place the CAD is allowed to supply values: as ground truth for
validating perception, never as a source of map colour.

Method
------
The traversability cloud carries penalties, not raw slope, so the measured slope
is recovered by inverting the smoothstep the scorer applies:

    p = t^2 (3 - 2t),   t = (slope - slope_free) / (slope_max - slope_free)

The curve is monotonic on [0, 1], so the inversion is exact -- but it is only
invertible where the penalty is strictly between 0 and 1. Cells below
``slope_free`` all read p = 0 and cells above ``slope_max`` all read p = 1, and
those two groups carry no slope information at all. They are excluded and
counted, rather than being folded in at the boundary value, which would
manufacture agreement exactly where the measurement is least informative.
"""
import argparse
import math
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def invert_smoothstep(p):
    """Return t in [0, 1] with t^2(3-2t) = p, elementwise."""
    p = np.asarray(p, dtype=float)
    lo = np.zeros_like(p)
    hi = np.ones_like(p)
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        smaller = mid * mid * (3.0 - 2.0 * mid) < p
        lo = np.where(smaller, mid, lo)
        hi = np.where(smaller, hi, mid)
    return 0.5 * (lo + hi)


def main(argv=None):
    """Compare measured against CAD slope and write the figure."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--truth', required=True)
    parser.add_argument('--measured', required=True)
    parser.add_argument('--out', default='slope_validation.png')
    parser.add_argument('--slope-free', type=float, default=0.0872665)
    parser.add_argument('--slope-max', type=float, default=0.523599)
    args = parser.parse_args(argv)

    truth = np.load(args.truth)
    rows = np.load(args.measured)['rows']

    nx, ny = int(truth['nx']), int(truth['ny'])
    res, min_x, min_y = (float(truth[k]) for k in ('resolution', 'min_x', 'min_y'))
    true_slope = truth['slope']

    valid = rows[:, 9] > 0.5
    v = rows[valid]
    penalty = v[:, 4]

    informative = (penalty > 1e-6) & (penalty < 1.0 - 1e-6)
    below = int((penalty <= 1e-6).sum())
    above = int((penalty >= 1.0 - 1e-6).sum())
    v = v[informative]
    penalty = penalty[informative]
    print(f'valid cells {int(valid.sum())}')
    print(f'  saturated low  (slope < {math.degrees(args.slope_free):.1f} deg): {below}')
    print(f'  saturated high (slope > {math.degrees(args.slope_max):.1f} deg): {above}')
    print(f'  invertible, used: {len(v)}')
    if not len(v):
        sys.exit('no invertible cells')

    t = invert_smoothstep(penalty)
    measured = args.slope_free + t * (args.slope_max - args.slope_free)

    ix = np.floor((v[:, 0] - min_x) / res).astype(int)
    iy = np.floor((v[:, 1] - min_y) / res).astype(int)
    inside = (ix >= 0) & (ix < nx) & (iy >= 0) & (iy < ny)
    ix, iy, measured = ix[inside], iy[inside], measured[inside]
    truth_vals = true_slope[iy, ix]
    good = np.isfinite(truth_vals)
    measured, truth_vals = measured[good], truth_vals[good]

    md = np.degrees(measured)
    td = np.degrees(truth_vals)
    err = md - td
    print(f'  paired against CAD: {len(err)}')
    print(f'measured slope  median {np.median(md):.2f} deg')
    print(f'CAD slope       median {np.median(td):.2f} deg')
    print(f'error (measured - CAD)  mean {err.mean():+.2f}  median '
          f'{np.median(err):+.2f}  sd {err.std():.2f} deg')
    print(f'  |error| P50 {np.percentile(abs(err), 50):.2f}  '
          f'P90 {np.percentile(abs(err), 90):.2f} deg')
    if len(err) > 2:
        print(f'correlation {np.corrcoef(md, td)[0, 1]:+.3f}')

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.4), dpi=200)

    ax1.hexbin(td, md, gridsize=45, cmap='viridis', mincnt=1, bins='log')
    lims = [min(td.min(), md.min()), max(td.max(), md.max())]
    ax1.plot(lims, lims, 'r--', lw=1.4, label='perfect agreement')
    ax1.set_xlabel('CAD ground-truth slope [deg]')
    ax1.set_ylabel('rover-measured slope [deg]')
    ax1.set_title(f'Measured vs true slope, {len(err)} cells\n'
                  f'correlation {np.corrcoef(md, td)[0, 1]:+.3f}', fontsize=10)
    ax1.legend(fontsize=9)
    ax1.grid(alpha=0.25, ls=':')

    ax2.hist(err, bins=60, color='#3b6fd4', edgecolor='none')
    ax2.axvline(0, color='k', lw=1.0)
    ax2.axvline(np.median(err), color='#c0392b', ls='--', lw=1.4,
                label=f'median {np.median(err):+.2f} deg')
    ax2.set_xlabel('measured - CAD slope [deg]')
    ax2.set_ylabel('cells')
    ax2.set_title(f'Slope error: sd {err.std():.2f} deg, '
                  f'|err| P90 {np.percentile(abs(err), 90):.2f} deg', fontsize=10)
    ax2.legend(fontsize=9)
    ax2.grid(alpha=0.25, ls=':')

    fig.suptitle(
        'Perception validated against arena CAD '
        '(CAD used as ground truth only, never as map colour)', fontsize=11)
    fig.tight_layout()
    fig.savefig(args.out)
    print(f'wrote {args.out}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
