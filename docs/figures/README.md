# Figures

Regenerated from a live simulation run, not hand-drawn. Every step is a script in
`tools/`.

## How to regenerate

```bash
# 1. Rasterise the arena CAD into a ground-truth grid
tools/rasterize_arena.py \
  ros2_ws/src/space_gazebo/models/arena_terrain_v04/meshes/arena_visual.stl \
  --resolution 0.05 --out arena_truth.npz

# 2. Launch (headless works with no GL context) and drive while capturing
ros2 launch space_bringup simulation.launch.py world:=arena_terrain_v04 \
  spawn_z:=0.32 headless:=true use_rviz:=false
tools/capture_cells.py /terrain/traversability 46 measured_cells.npz
tools/capture_slip.py 24 slip_trace.png

# 3. Render
tools/render_arena_map.py --truth arena_truth.npz --measured measured_cells.npz \
  --out arena_map_accumulated.png
tools/compare_to_cad.py --truth arena_truth.npz --measured measured_cells.npz \
  --out slope_validation_vs_cad.png
```

## What each one shows

**`arena_map_accumulated.png`** — traversability accumulated onto the arena's
fixed grid. 693 of 8000 cells measured (8.7% coverage) over 219 frames, median
15 visits per measured cell. Grey is *not yet visited*, which is a different
statement from *measured and bad* — the distinction the raw pipeline output
cannot make, because it emits only the cells currently in view.

The hillshade is CAD, for context. **Every colour is measured by the rover.**
Colouring from CAD would turn the map into a restatement of what we already knew,
and the mission's claim (CLAUDE.md §1.1) is that a rover on the terrain learns
what geometry cannot tell you.

**`slope_validation_vs_cad.png`** — the rover's measured slope against the
arena's true slope, 9189 cells. Correlation **+0.766**, error sd 6.28°,
|error| P90 9.25°, median **−2.42°**.

The bias sign matters. The pipeline *under*-reports slope, because the 5 cm
elevation grid median-filters the surface and flattens it. Under-reporting is the
optimistic direction: the geometric map makes terrain look gentler than it is.
That is the quantified case for measuring slip on top of geometry rather than
trusting geometry alone.

**`slip_trace_arena_terrain_v04.png`** — `V_wheel` and `V_actual` track each
other for 7.5 s at 1–2% slip inside the SAFE band, then `V_actual` collapses to
zero while `V_wheel` holds 0.10 m/s, and slip crosses the 40% HAZARD boundary to
saturate at 100%. Nothing about the geometry changed at that instant; only the
rover's ability to move did.

**`traversability_map_arena_terrain_v04.png`** — the earlier scatter of measured
cells without the arena canvas. Superseded by `arena_map_accumulated.png`; kept
because it shows what the pipeline emits before the canvas is applied.

## Caveat

Accumulation in these figures happens **offline, in `capture_cells.py`**. The
running system does not hold a map: `local_elevation_map_node` keeps a 4×4 m
window around the rover and drops cells after `cell_timeout` = 2 s. The
persistent `TerrainEstimate` producer is still to be written — see
`docs/pending.md`.
