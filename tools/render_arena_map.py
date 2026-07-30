#!/usr/bin/env python3
"""
Paint measured traversability onto the arena's fixed grid, and score coverage.

Why not just plot the measured cells
------------------------------------
The perception pipeline is a rolling window: ``local_elevation_map_node`` keeps a
4 x 4 m grid around the rover and drops cells after ``cell_timeout`` = 2 s. Plotting
what it emits shows only where the rover is looking now, so cells appear and
vanish and the picture never reads as a map. Worse, "no colour" is ambiguous --
it could mean unmeasured, or measured and bad.

Rasterising the arena mesh gives a grid that exists from t=0, so every cell is
one of three states: MEASURED (coloured), NOT YET VISITED (grey), or off-arena.
Coverage becomes a number instead of an impression.

The CAD supplies the canvas and the shaded background ONLY. Every colour comes
from the rover's own measurements. Colouring from CAD geometry would make the map
a restatement of what we already knew, and the mission's claim (CLAUDE.md 1.1) is
that a rover on the terrain learns what geometry cannot tell you.
"""
import argparse
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LightSource


def accumulate(rows, truth, statistic='mean'):
    """
    Bin measured cells onto the truth grid.

    Returns the accumulated score grid (NaN where never measured) and the
    per-cell visit count. ``mean`` rather than ``latest`` because repeat visits
    are the whole point of driving on the terrain -- averaging is the crudest
    form of the confidence accrual that ``soil_confidence`` formalises.
    """
    nx, ny = int(truth['nx']), int(truth['ny'])
    res = float(truth['resolution'])
    min_x, min_y = float(truth['min_x']), float(truth['min_y'])

    valid = rows[:, 9] > 0.5
    v = rows[valid]
    ix = np.floor((v[:, 0] - min_x) / res).astype(int)
    iy = np.floor((v[:, 1] - min_y) / res).astype(int)
    inside = (ix >= 0) & (ix < nx) & (iy >= 0) & (iy < ny)
    ix, iy, v = ix[inside], iy[inside], v[inside]

    total = np.zeros((ny, nx))
    count = np.zeros((ny, nx))
    np.add.at(total, (iy, ix), v[:, 3])
    np.add.at(count, (iy, ix), 1.0)

    score = np.full((ny, nx), np.nan)
    hit = count > 0
    score[hit] = total[hit] / count[hit]
    if statistic == 'min':
        # Pessimistic variant: keep the worst reading per cell.
        worst = np.full((ny, nx), np.inf)
        np.minimum.at(worst, (iy, ix), v[:, 3])
        score[hit] = worst[hit]
    return score, count, int(inside.sum()), int(len(rows) - valid.sum())


def main(argv=None):
    """Render the arena map and print coverage statistics."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--truth', required=True)
    parser.add_argument('--measured', required=True)
    parser.add_argument('--out', default='arena_map.png')
    parser.add_argument('--statistic', default='mean', choices=('mean', 'min'))
    parser.add_argument(
        '--mode', default='driven', choices=('driven', 'survey'),
        help=('driven: overlay the odom path. survey: hide it, because in a '
              'survey the rover is PLACED at each pose, so the odom trace is a '
              'sequence of teleports and drawing it as a path would imply the '
              'rover drove a route it cannot actually traverse.'),
    )
    args = parser.parse_args(argv)

    truth = np.load(args.truth)
    data = np.load(args.measured)
    rows, path = data['rows'], data['path']

    score, count, used, invalid = accumulate(rows, truth, args.statistic)
    ny, nx = score.shape
    res = float(truth['resolution'])
    min_x, min_y = float(truth['min_x']), float(truth['min_y'])
    extent = (min_x, min_x + nx * res, min_y, min_y + ny * res)

    measured = np.isfinite(score)
    print(f'grid {nx} x {ny} at {res} m  ({nx * ny} cells)')
    print(f'cells binned {used}, rejected as invalid {invalid}')
    print(f'COVERAGE {measured.sum()} / {measured.size} '
          f'({100.0 * measured.mean():.1f}%) after {int(data["frames"])} frames')
    if measured.any():
        s = score[measured]
        print(f'score  min {s.min():.3f}  median {np.median(s):.3f}  '
              f'max {s.max():.3f}')
        print(f'visits per measured cell  median {np.median(count[measured]):.0f}'
              f'  max {count[measured].max():.0f}')

    elevation = truth['elevation']
    shade = LightSource(azdeg=315, altdeg=45).hillshade(
        np.nan_to_num(elevation, nan=float(np.nanmin(elevation))),
        vert_exag=3.0, dx=res, dy=res,
    )

    fig, ax = plt.subplots(figsize=(8.2, 8.6), dpi=140)
    ax.imshow(shade, cmap='gray', origin='lower', extent=extent,
              vmin=0.0, vmax=1.4, interpolation='bilinear')
    # Grey wash so unmeasured arena is visibly "not yet visited", not "bad".
    ax.imshow(np.ones_like(shade), cmap='gray', origin='lower', extent=extent,
              alpha=0.35, vmin=0.0, vmax=1.0)
    img = ax.imshow(np.ma.masked_invalid(score), cmap='RdYlGn', origin='lower',
                    extent=extent, vmin=0.6, vmax=1.0, interpolation='nearest')

    if len(path) and args.mode == 'driven':
        ax.plot(path[:, 0], path[:, 1], '-', color='#0b2fb5', lw=2.0,
                label='rover path')
        ax.plot(path[0, 0], path[0, 1], 'o', color='#0b2fb5', ms=8,
                label='start')
        ax.plot(path[-1, 0], path[-1, 1], '*', color='#000', ms=16, label='end')
        ax.legend(loc='lower left', fontsize=9, framealpha=0.92)

    cb = fig.colorbar(img, ax=ax, fraction=0.046, pad=0.03)
    cb.set_label('measured traversability (higher = easier)')
    ax.set_xlabel('x [m]')
    ax.set_ylabel('y [m]')
    how = ('driven traverse' if args.mode == 'driven'
           else 'survey poses -- rover PLACED, not driven')
    ax.set_title(
        f'Traversability accumulated on the arena grid ({how})\n'
        f'{measured.sum()} of {measured.size} cells measured '
        f'({100.0 * measured.mean():.1f}% coverage); grey = not yet visited\n'
        'shading is CAD ground truth for context only -- all colour is measured',
        fontsize=10,
    )
    ax.set_aspect('equal')
    fig.tight_layout()
    fig.savefig(args.out)
    print(f'wrote {args.out}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
