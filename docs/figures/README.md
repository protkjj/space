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

## Reading the map figures

Each map figure is two panels: **CAD ground truth on the left** (what the arena
IS, known before driving) and **rover-measured traversability on the right**.
Comparing them is the point — every bright crater rim in the CAD slope panel has
a red arc against it in the measured panel, which is the +0.707 correlation made
visible.

Two presentation choices, both constrained so they cannot overstate the result:

**The ramp is centred on 0.60**, so scores below it read red and above it read
green, and the boundary is drawn as a contour. This is a **presentation** choice:
it changes no score, and it is *not* the CLAUDE.md §1.4 verdict boundary — that
one depends on σ₀ and the ramp test, both still pending (`docs/pending.md`).
Centred this way the survey splits 47.4% below / 52.6% above, so the eye sees the
spread instead of a wall of red. Pass `--threshold` to move it or omit it for a
plain linear ramp.

**Colour scale follows the data.** The first version of these figures fixed the
ramp at 0.60–1.00, which clipped **47.4% of cells to the bottom red** and left
the top tenth of the ramp for 0.7% of cells — the map looked uniformly hostile
while the data actually spread from 0.03 to 0.94 with a median of 0.62. The scale
now runs from the 2nd to the 98th percentile (`--vmin`/`--vmax` to override).

**3×3 neighbour smoothing**, because adjacent 5 cm cells are not independent
samples — they are the same surface seen through sensor noise. It is masked back
to the originally measured cells on every iteration, so it can never bleed colour
into ground the rover has not observed, and the scripts assert the coverage count
is unchanged (`coverage change +0 cells`). A blur that widened coverage would
inflate the one number these figures exist to report.

## What each one shows

**`arena_map_full_survey.png`** — the whole arena at **75.0% coverage**
(6000 of 8000 cells, 1144 frames, median 29 visits per cell). Crater floors read
green and the rims read dark red, which is the structure the hillshade shows
independently.

Produced by `survey_arena.py`, which PLACES the rover at 96 poses (4x6 grid, 4
yaws each) rather than driving it, because this rover cannot traverse the whole
arena: it high-centres on the rims, and a driven run reaches 1.1 m and 8.7%
coverage. Placement heights come from the CAD grid so the rover settles onto the
surface instead of being dropped inside it; 21 of 96 poses still ended tilted
beyond 25 deg, which is reported rather than hidden.

Perception is fully exercised — every cell comes from a real rendered depth image
through the unchanged pipeline. Only locomotion is skipped, and the figure title
says so. Use this figure for "what the map looks like with coverage" and
`arena_map_accumulated.png` for "how far the rover actually gets".

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
arena's true slope over the full survey, **157,378 cells**. Correlation
**+0.707**, error sd 6.78°, |error| P90 11.08°, median **−2.76°**.

Cells whose slope penalty saturates carry no slope information, so they are
excluded and counted rather than folded in at the boundary: 26,475 below 5° and
21,819 above 30°. The earlier short traverse gave +0.766 / −2.42° over 9189
cells — the full survey covers harder terrain, so the correlation is slightly
lower and the bias slightly larger.

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
