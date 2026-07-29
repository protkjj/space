#!/usr/bin/env python3
"""Resample the dense terrain STL into a coarse heightfield collision mesh.

The competition terrain (``arena_terrain_v04``) ships as a ~314k-triangle
surface mesh in metres.  Using it directly as a Gazebo collision would cripple
the physics engine, so we rasterise its top surface onto a regular XY grid and
emit a low-poly (~a few thousand triangle) heightfield mesh that is cheap to
collide against.  The full-resolution mesh is kept for the visual.

Only numpy/scipy are required (no trimesh/open3d), so this runs on a stock
ROS 2 Jazzy Python environment.
"""

from __future__ import annotations

import argparse
import struct
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree


def _read_binary_stl(path: Path) -> np.ndarray:
    """Return an (n, 3, 3) array of triangle vertices from a binary STL."""
    with path.open("rb") as fh:
        fh.read(80)  # header
        (count,) = struct.unpack("<I", fh.read(4))
        raw = np.frombuffer(fh.read(50 * count), dtype=np.uint8)
    raw = raw.reshape(count, 50)
    # 12 float32 per triangle: normal(3) + v1(3) + v2(3) + v3(3); trailing 2B attr
    floats = raw[:, :48].copy().view("<f4").reshape(count, 12)
    return floats[:, 3:12].reshape(count, 3, 3)


def _write_binary_stl(path: Path, triangles: np.ndarray) -> None:
    """Write an (n, 3, 3) triangle array as a binary STL (normals zeroed)."""
    count = triangles.shape[0]
    body = np.zeros((count, 50), dtype=np.uint8)
    payload = np.zeros((count, 12), dtype="<f4")
    payload[:, 3:12] = triangles.reshape(count, 9)
    body[:, :48] = payload.view(np.uint8).reshape(count, 48)
    with path.open("wb") as fh:
        fh.write(b"terrain collision heightfield".ljust(80, b"\0"))
        fh.write(struct.pack("<I", count))
        fh.write(body.tobytes())


def _build_heightfield(verts: np.ndarray, cell: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Grid the point cloud; each node takes the max Z of nearby samples.

    Max (rather than mean) keeps the collision surface at or above every real
    sample so the rover never clips through a bump.  Empty nodes are filled
    from the nearest populated node.
    """
    xmin, ymin = verts[:, 0].min(), verts[:, 1].min()
    xmax, ymax = verts[:, 0].max(), verts[:, 1].max()
    nx = int(np.ceil((xmax - xmin) / cell)) + 1
    ny = int(np.ceil((ymax - ymin) / cell)) + 1
    xs = xmin + cell * np.arange(nx)
    ys = ymin + cell * np.arange(ny)

    # snap each vertex to the nearest grid node and keep the running max Z
    ix = np.clip(np.round((verts[:, 0] - xmin) / cell).astype(int), 0, nx - 1)
    iy = np.clip(np.round((verts[:, 1] - ymin) / cell).astype(int), 0, ny - 1)
    flat = iy * nx + ix
    z = np.full(nx * ny, -np.inf)
    np.maximum.at(z, flat, verts[:, 2])
    z = z.reshape(ny, nx)

    filled = np.isfinite(z)
    if not filled.all():
        gy, gx = np.mgrid[0:ny, 0:nx]
        known = np.column_stack((gx[filled], gy[filled]))
        tree = cKDTree(known)
        miss = ~filled
        _, idx = tree.query(np.column_stack((gx[miss], gy[miss])))
        z[miss] = z[filled][idx]
    return xs, ys, z


def _grid_to_triangles(xs: np.ndarray, ys: np.ndarray, z: np.ndarray) -> np.ndarray:
    ny, nx = z.shape
    gx, gy = np.meshgrid(xs, ys)
    tris = []
    for j in range(ny - 1):
        for i in range(nx - 1):
            v00 = (gx[j, i], gy[j, i], z[j, i])
            v10 = (gx[j, i + 1], gy[j, i + 1], z[j, i + 1])
            v01 = (gx[j + 1, i], gy[j + 1, i], z[j + 1, i])
            v11 = (gx[j + 1, i + 1], gy[j + 1, i + 1], z[j + 1, i + 1])
            tris.append((v00, v10, v11))
            tris.append((v00, v11, v01))
    return np.asarray(tris, dtype="<f4")


def _sample_height(verts: np.ndarray, x: float, y: float, radius: float = 0.15) -> float:
    m = (np.abs(verts[:, 0] - x) < radius) & (np.abs(verts[:, 1] - y) < radius)
    return float(verts[m, 2].max()) if m.any() else float("nan")


def main() -> None:
    pkg = Path(__file__).resolve().parents[1]
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", type=Path,
                    default=pkg / "models/arena_terrain_v04/meshes/arena_visual.stl")
    ap.add_argument("--output", type=Path,
                    default=pkg / "models/arena_terrain_v04/meshes/arena_collision.stl")
    ap.add_argument("--cell", type=float, default=0.10, help="grid cell size (m)")
    args = ap.parse_args()

    tris = _read_binary_stl(args.source)
    verts = tris.reshape(-1, 3)
    print(f"source: {tris.shape[0]:,} triangles, {verts.shape[0]:,} vertices")
    print(f"bounds X[{verts[:,0].min():.2f},{verts[:,0].max():.2f}] "
          f"Y[{verts[:,1].min():.2f},{verts[:,1].max():.2f}] "
          f"Z[{verts[:,2].min():.2f},{verts[:,2].max():.2f}]")

    xs, ys, z = _build_heightfield(verts, args.cell)
    coll = _grid_to_triangles(xs, ys, z)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    _write_binary_stl(args.output, coll)
    print(f"collision: {coll.shape[0]:,} triangles @ {args.cell} m cell -> {args.output.name}")

    for sx, sy in ((-1.2, -1.6), (0.0, 0.0), (0.0, -2.0)):
        print(f"terrain top Z near ({sx:+.1f},{sy:+.1f}) = {_sample_height(verts, sx, sy):.3f} m")


if __name__ == "__main__":
    main()
