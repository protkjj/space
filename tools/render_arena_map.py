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
from matplotlib.colors import LightSource, LinearSegmentedColormap, TwoSlopeNorm


#: Regolith tone for the "as it is" arena render. Deliberately not a
#: scientific colour ramp: the left panel answers "what does the arena look
#: like", so a data-product palette would invite reading values off it.
REGOLITH = LinearSegmentedColormap.from_list(
    'regolith',
    ['#2b2620', '#4a4238', '#6f6455', '#968875', '#bdb09b', '#ded5c4'],
)


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


def smooth_measured(grid, radius, iterations=1):
    """
    Box-average each cell over its neighbours, ignoring NaN.

    Purely a presentation step, and constrained so it cannot lie: the result is
    masked back to the ORIGINAL measured cells on every iteration, so smoothing
    never bleeds a value into a cell the rover has not observed. Without that
    mask a blur would silently inflate the coverage figure -- painting colour on
    unvisited ground is exactly the claim this map must not make.

    Neighbour averaging is honest for a different reason too: adjacent 5 cm cells
    are not independent samples of the terrain, they are the same surface seen
    through sensor noise, so averaging them recovers signal rather than
    discarding it.
    """
    if radius < 1:
        return grid
    measured = np.isfinite(grid)
    out = grid
    rows, cols = grid.shape
    for _ in range(max(1, iterations)):
        total = np.zeros_like(grid)
        count = np.zeros_like(grid)
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                shifted = np.full_like(grid, np.nan)
                src_y = slice(max(0, dy), rows + min(0, dy))
                dst_y = slice(max(0, -dy), rows + min(0, -dy))
                src_x = slice(max(0, dx), cols + min(0, dx))
                dst_x = slice(max(0, -dx), cols + min(0, -dx))
                shifted[dst_y, dst_x] = out[src_y, src_x]
                ok = np.isfinite(shifted)
                total[ok] += shifted[ok]
                count[ok] += 1.0
        averaged = np.where(count > 0, total / np.maximum(count, 1.0), np.nan)
        out = np.where(measured, averaged, np.nan)
    return out


def truncate_to_coverage(rows, truth, target):
    """
    Keep the earliest rows that reach ``target`` coverage, and drop the rest.

    Rows are stored in arrival order, so this is exactly "the survey stopped
    earlier" rather than a cherry-picked subset -- which matters, because
    choosing WHICH cells to keep could flatter the map, while choosing WHEN to
    stop cannot.
    """
    nx, ny = int(truth['nx']), int(truth['ny'])
    res = float(truth['resolution'])
    min_x, min_y = float(truth['min_x']), float(truth['min_y'])
    wanted = int(round(target * nx * ny))

    seen = set()
    for index, row in enumerate(rows):
        if row[9] <= 0.5:
            continue
        ix = int((row[0] - min_x) / res)
        iy = int((row[1] - min_y) / res)
        if 0 <= ix < nx and 0 <= iy < ny:
            seen.add(iy * nx + ix)
            if len(seen) >= wanted:
                print(f'coverage target {target:.0%}: stopped after '
                      f'{index + 1} of {len(rows)} captured cells')
                return rows[:index + 1]
    print(f'coverage target {target:.0%} not reachable; using all '
          f'{len(rows)} cells ({len(seen)} distinct)')
    return rows


def draw_truth(ax, truth, extent, layer):
    """Draw the CAD arena as a shaded relief map, and return the image."""
    res = float(truth['resolution'])
    elevation = truth['elevation']
    filled = np.nan_to_num(elevation, nan=float(np.nanmin(elevation)))
    light = LightSource(azdeg=315, altdeg=45)

    if layer == 'slope':
        values = np.degrees(truth['slope'])
        cmap, label = 'magma', 'CAD ground-truth slope [deg]'
    elif layer == 'elevation':
        values = elevation
        # Not 'terrain': its blue low end reads as water, which is misleading
        # for a regolith arena. cividis is perceptually uniform and
        # colour-vision-safe.
        cmap, label = 'cividis', 'CAD ground-truth elevation [m]'
    else:
        # 'arena': the surface as it looks, not as a measurement. No colour bar,
        # because there is no value to read off it -- that is the point. Strong
        # vertical exaggeration and low sun bring out the crater rims, which is
        # what the reader is being asked to compare against.
        values = elevation
        cmap, label = REGOLITH, None

    rgb = light.shade(
        np.nan_to_num(values, nan=float(np.nanmin(values))),
        cmap=(cmap if not isinstance(cmap, str) else plt.get_cmap(cmap)),
        blend_mode='overlay' if label is None else 'soft',
        vert_exag=6.0 if label is None else 3.0, dx=res, dy=res,
    )
    ax.imshow(rgb, origin='lower', extent=extent, interpolation='bilinear')
    if label is None:
        return None, None, values
    # A separate mappable carries the colour bar, since shade() returns RGB.
    mappable = ax.imshow(
        np.ma.masked_invalid(values), cmap=cmap, origin='lower',
        extent=extent, alpha=0.0,
    )
    return mappable, label, values


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
    parser.add_argument(
        '--smooth', type=int, default=1,
        help=('neighbour radius in cells for presentation smoothing; 0 disables. '
              'Never widens coverage -- see smooth_measured().'),
    )
    parser.add_argument('--smooth-iterations', type=int, default=1)
    parser.add_argument(
        '--left', default='arena',
        choices=('arena', 'elevation', 'slope', 'none'),
        help=('comparison panel: "arena" renders the CAD surface as it LOOKS '
              '(shaded relief, no colour bar) so the reader compares terrain '
              'against measurement rather than one heat map against another; '
              '"elevation"/"slope" draw it as a labelled data product'),
    )
    parser.add_argument(
        '--vmin', type=float, default=None,
        help='colour-scale floor; default is the 2nd percentile of the data',
    )
    parser.add_argument('--vmax', type=float, default=None)
    parser.add_argument(
        '--coverage-target', type=float, default=None,
        help=('stop consuming captured frames once this coverage fraction is '
              'reached. Equivalent to ending the survey earlier, since frames '
              'are consumed in the order they arrived -- it is a shorter '
              'survey, not a filtered one.'),
    )
    parser.add_argument(
        '--threshold', type=float, default=None,
        help=('score treated as the neutral point: the colour ramp is centred '
              'here so below reads red and above reads green, and the boundary '
              'is drawn as a contour. Presentation only -- it does not change '
              'any score, and it is NOT the CLAUDE.md 1.4 verdict boundary, '
              'which depends on measurements still pending (docs/pending.md).'),
    )
    args = parser.parse_args(argv)

    truth = np.load(args.truth)
    data = np.load(args.measured)
    rows, path = data['rows'], data['path']

    if args.coverage_target is not None:
        rows = truncate_to_coverage(rows, truth, args.coverage_target)

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

    shown = smooth_measured(score, args.smooth, args.smooth_iterations)
    if args.smooth >= 1:
        widened = int(np.isfinite(shown).sum() - measured.sum())
        print(f'smoothed r={args.smooth} x{args.smooth_iterations}, '
              f'coverage change {widened:+d} cells (must be 0)')
        assert widened == 0, 'smoothing widened coverage'

    # Scale colour to the data. The previous fixed 0.60-1.00 range clipped 47.4%
    # of cells to the bottom of the ramp and left the top 10% of the ramp for
    # 0.7% of cells, so the map looked uniformly hostile while actually carrying
    # a spread from 0.03 to 0.94.
    finite = shown[np.isfinite(shown)]
    vmin = args.vmin if args.vmin is not None else float(
        np.percentile(finite, 2))
    vmax = args.vmax if args.vmax is not None else float(
        np.percentile(finite, 98))
    print(f'colour scale {vmin:.3f} .. {vmax:.3f} '
          f'(data {finite.min():.3f} .. {finite.max():.3f})')

    panels = 1 if args.left == 'none' else 2
    fig, axes = plt.subplots(
        1, panels, figsize=(8.4 if panels == 1 else 15.0, 9.0), dpi=140,
        sharex=True, sharey=True, squeeze=False,
    )
    axes = axes[0]
    ax = axes[-1]

    if panels == 2:
        left = axes[0]
        mappable, label, _ = draw_truth(left, truth, extent, args.left)
        if mappable is not None:
            cbl = fig.colorbar(mappable, ax=left, fraction=0.046, pad=0.03)
            cbl.set_label(label)
            cbl.solids.set_alpha(1.0)
        else:
            # Keep the panels the same width even without a colour bar.
            cbl = fig.colorbar(
                plt.cm.ScalarMappable(cmap=REGOLITH), ax=left,
                fraction=0.046, pad=0.03,
            )
            cbl.outline.set_visible(False)
            cbl.set_ticks([])
            cbl.ax.set_visible(False)
        left.set_title(
            'The arena itself\n'
            'shaded relief of the CAD surface -- no measurement involved',
            fontsize=10,
        )
        left.set_xlabel('x [m]')
        left.set_ylabel('y [m]')
        left.set_aspect('equal')

    # Hillshade under the measurement panel too, so unmeasured ground still
    # reads as terrain rather than as a blank.
    elevation = truth['elevation']
    hill = LightSource(azdeg=315, altdeg=45).hillshade(
        np.nan_to_num(elevation, nan=float(np.nanmin(elevation))),
        vert_exag=3.0, dx=res, dy=res,
    )
    ax.imshow(hill, cmap='gray', origin='lower', extent=extent,
              vmin=-0.1, vmax=1.5, interpolation='bilinear')
    if args.threshold is not None:
        centre = float(args.threshold)
        # TwoSlopeNorm needs the centre strictly inside the range.
        lo = min(vmin, centre - 1e-3)
        hi = max(vmax, centre + 1e-3)
        norm = TwoSlopeNorm(vcenter=centre, vmin=lo, vmax=hi)
        img = ax.imshow(np.ma.masked_invalid(shown), cmap='RdYlGn',
                        origin='lower', extent=extent, norm=norm,
                        interpolation='nearest')
        below = float((finite < centre).mean())
        print(f'threshold {centre:.2f}: below {100 * below:.1f}%, '
              f'above {100 * (1 - below):.1f}%')
        # Draw the boundary itself so it is legible, not just implied by hue.
        ys = np.linspace(extent[2] + res / 2, extent[3] - res / 2, ny)
        xs = np.linspace(extent[0] + res / 2, extent[1] - res / 2, nx)
        ax.contour(xs, ys, np.nan_to_num(shown, nan=centre),
                   levels=[centre], colors='#111', linewidths=0.9, alpha=0.75)
    else:
        img = ax.imshow(np.ma.masked_invalid(shown), cmap='RdYlGn',
                        origin='lower', extent=extent, vmin=vmin, vmax=vmax,
                        interpolation='nearest')

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
    how = ('driven traverse' if args.mode == 'driven'
           else 'survey poses -- rover PLACED, not driven')
    smoothing = (f'{2 * args.smooth + 1}x{2 * args.smooth + 1} smoothed'
                 if args.smooth >= 1 else 'unsmoothed')
    if args.threshold is not None:
        smoothing += f'; ramp centred on {args.threshold:.2f} (contour)'
    ax.set_title(
        f'Rover-measured traversability ({how})\n'
        f'{measured.sum()} of {measured.size} cells = '
        f'{100.0 * measured.mean():.1f}% coverage; grey = not yet visited\n'
        f'{smoothing}; every colour is measured, none is taken from CAD',
        fontsize=10,
    )
    ax.set_aspect('equal')
    # Three-line titles need headroom, and bbox_inches='tight' then guarantees
    # nothing is trimmed -- reserving space by hand clipped the axis labels.
    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.95))
    fig.savefig(args.out, bbox_inches='tight')
    print(f'wrote {args.out}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
