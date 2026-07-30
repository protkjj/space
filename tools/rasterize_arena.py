#!/usr/bin/env python3
"""
Rasterise an arena mesh into a ground-truth 2-D grid.

WHAT THIS IS FOR, AND WHAT IT MUST NOT BE USED FOR
--------------------------------------------------
The arena CAD is legitimate for three things:

  * deciding the grid extent, origin, and resolution, so the map covers the
    whole arena from t=0 and unmeasured cells are visibly UNKNOWN rather than
    simply absent;
  * a background layer (hillshade) so a figure reads as a map;
  * GROUND TRUTH, to quantify how far the rover's measured slope and roughness
    are from the real surface.

It must NOT supply traversability values. If the map were coloured from CAD
geometry it would stop being something the rover measured and become a restated
copy of what we already knew -- and the mission's whole claim (CLAUDE.md 1.1) is
that a rover on the terrain learns what geometry alone cannot tell you. That is
the same circularity trap as pointing the slip estimator's v_actual at the EKF:
the arithmetic would still succeed and the output would still look plausible.

Nothing at runtime depends on this file. The accumulating map node takes its
extent as plain parameters, so it works on terrain with no CAD at all -- which is
the actual mission environment.

Usage:
    tools/rasterize_arena.py MESH.stl --resolution 0.05 --out arena_truth.npz
"""

import argparse
import math
import struct
import sys

import numpy as np


def read_binary_stl(path):
    """Return (N, 3, 3) vertices from a binary STL, in the file's own units."""
    with open(path, 'rb') as handle:
        handle.read(80)
        count = struct.unpack('<I', handle.read(4))[0]
        payload = handle.read(count * 50)
    if len(payload) < count * 50:
        raise ValueError(f'{path}: truncated, expected {count} triangles')
    tris = np.empty((count, 3, 3), dtype=np.float64)
    for i in range(count):
        base = i * 50 + 12
        for v in range(3):
            tris[i, v] = struct.unpack_from('<3f', payload, base + v * 12)
    return tris


def rasterise(tris, resolution, surface_band=0.03):
    """
    Bin triangle vertices into a grid and return ground-truth layers.

    Elevation is the per-cell MAXIMUM z, not the median. These arena meshes are
    closed solids, not surfaces: exactly 50% of the vertices in
    ``arena_terrain_v04`` sit on a flat base at z = -0.2000. A median would land
    between the base and the top and describe a surface that does not exist,
    and the resulting "roughness" would be half the solid's thickness -- 0.163 m
    on this mesh, against a real micro-relief of a few millimetres.

    ``surface_band`` is how far below the cell maximum a vertex still counts as
    part of the driving surface. Roughness is the standard deviation of z within
    that band, which is the quantity the perception pipeline also calls
    roughness, so measured and truth are comparable rather than differently
    defined.
    """
    pts = tris.reshape(-1, 3)
    min_x, min_y = pts[:, 0].min(), pts[:, 1].min()
    max_x, max_y = pts[:, 0].max(), pts[:, 1].max()

    nx = int(math.ceil((max_x - min_x) / resolution))
    ny = int(math.ceil((max_y - min_y) / resolution))
    ix = np.clip(((pts[:, 0] - min_x) / resolution).astype(int), 0, nx - 1)
    iy = np.clip(((pts[:, 1] - min_y) / resolution).astype(int), 0, ny - 1)
    flat = iy * nx + ix

    elevation = np.full(nx * ny, np.nan)
    roughness = np.full(nx * ny, np.nan)
    counts = np.zeros(nx * ny, dtype=np.int64)

    order = np.argsort(flat, kind='stable')
    keys = flat[order]
    zs = pts[order, 2]
    edges = np.flatnonzero(np.diff(keys)) + 1
    for key, chunk in zip(
        np.concatenate(([keys[0]], keys[edges])), np.split(zs, edges)
    ):
        top = chunk.max()
        surface = chunk[chunk >= top - surface_band]
        elevation[key] = top
        roughness[key] = surface.std()
        counts[key] = surface.size

    elevation = elevation.reshape(ny, nx)
    roughness = roughness.reshape(ny, nx)
    counts = counts.reshape(ny, nx)

    # Slope from the elevation gradient. Cells with no vertices stay NaN and
    # propagate, so a slope is never invented where there is no surface.
    grad_y, grad_x = np.gradient(elevation, resolution, resolution)
    slope = np.arctan(np.hypot(grad_x, grad_y))

    return {
        'elevation': elevation,
        'roughness': roughness,
        'slope': slope,
        'counts': counts,
        'min_x': min_x,
        'min_y': min_y,
        'resolution': resolution,
        'nx': nx,
        'ny': ny,
    }


def main(argv=None):
    """Rasterise a mesh and write the ground-truth grid."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mesh')
    parser.add_argument('--resolution', type=float, default=0.05)
    parser.add_argument('--out', default='arena_truth.npz')
    args = parser.parse_args(argv)

    tris = read_binary_stl(args.mesh)
    print(f'{args.mesh}: {len(tris)} triangles')
    grid = rasterise(tris, args.resolution)

    filled = np.isfinite(grid['elevation'])
    print(f'grid {grid["nx"]} x {grid["ny"]} at {grid["resolution"]} m')
    print(f'  origin  ({grid["min_x"]:+.4f}, {grid["min_y"]:+.4f})')
    print(f'  extent  x {grid["min_x"]:+.3f} .. '
          f'{grid["min_x"] + grid["nx"] * grid["resolution"]:+.3f}   '
          f'y {grid["min_y"]:+.3f} .. '
          f'{grid["min_y"] + grid["ny"] * grid["resolution"]:+.3f}')
    print(f'  cells with surface {filled.sum()} / {filled.size} '
          f'({100.0 * filled.mean():.1f}%)')
    print(f'  elevation {np.nanmin(grid["elevation"]):+.4f} .. '
          f'{np.nanmax(grid["elevation"]):+.4f} m')
    print(f'  slope     {math.degrees(np.nanmin(grid["slope"])):.2f} .. '
          f'{math.degrees(np.nanmax(grid["slope"])):.2f} deg '
          f'(median {math.degrees(np.nanmedian(grid["slope"])):.2f})')
    print(f'  roughness {np.nanmin(grid["roughness"]):.5f} .. '
          f'{np.nanmax(grid["roughness"]):.5f} m '
          f'(median {np.nanmedian(grid["roughness"]):.5f})')

    np.savez_compressed(args.out, **grid)
    print(f'wrote {args.out}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
