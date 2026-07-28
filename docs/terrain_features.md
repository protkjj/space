# Geometric terrain features

## Pipeline and interfaces

The feature layer consumes sensor-derived elevation cells only:

```text
/terrain/elevation_points (odom)
  → terrain_feature_node
  ├── /terrain/features
  ├── /terrain/slope_markers
  ├── /terrain/roughness_markers
  ├── /terrain/step_markers
  └── /terrain/feature_diagnostics
  → terrain_traversability_node
  └── /terrain/traversability
```

Runtime code does not read the arena CAD or STL. It does not publish a
traversability score, safety class, hazard decision, or marker recommendation.
The input header timestamp and frame are preserved. Inputs outside the
configured `odom` frame, malformed fields, invalid cells, and invalid feature
fits are omitted rather than fabricated.

The input fields are `x`, `y`, `z`, and `variance` as FLOAT32 and
`point_count` as UINT32. `/terrain/features` has this 44-byte layout:

| Field | Type | Units | Offset |
| --- | --- | --- | ---: |
| `x`, `y`, `z` | FLOAT32 | m | 0, 4, 8 |
| `slope` | FLOAT32 | rad | 12 |
| `roughness` | FLOAT32 | m | 16 |
| `step_height` | FLOAT32 | m | 20 |
| `elevation_variance` | FLOAT32 | m² | 24 |
| `point_count` | UINT32 | samples | 28 |
| `neighbor_count` | UINT32 | cells | 32 |
| `neighborhood_coverage` | FLOAT32 | ratio | 36 |
| `confidence` | FLOAT32 | ratio | 40 |

## Indexing and neighbourhood

For grid resolution `r`, the integer cell index is reconstructed from a
float32 centre using `round(x/r - 0.5)`. This avoids treating float32 rounding
near a cell centre as a different cell. Duplicate indices are counted and the
measurement with greatest point support is retained; lower variance and then
lower elevation are deterministic tie breakers.

The feature neighbourhood contains cell-centre offsets within the configured
Euclidean `feature_radius`. The centre is excluded from `neighbor_count` and
from the expected-neighbour total, but is included in the plane fit. Neighbours
are ordered by distance and integer offset, and `maximum_neighbors` bounds
work. Thus:

```text
coverage = available neighbours / expected neighbours
```

No missing neighbour is interpolated.

## Feature definitions

The configured `svd` fit solves the centred least-squares plane
`z = a·dx + b·dy + c`. Rank-deficient fits, fits above
`maximum_condition_number`, and fits whose RMS vertical residual exceeds
`maximum_fit_residual` are invalid.

Slope is:

```text
slope = atan(sqrt(a² + b²))
```

Roughness is the median absolute vertical residual of the centre and selected
neighbours about that plane. It is robust to an isolated large residual and
remains a geometric measurement, not a risk score.

Step height is the maximum absolute plane-removed elevation difference between
the centre and available cells within `step_neighborhood_cells`:

```text
max |(z_neighbor - z_center) - a·dx - b·dy|
```

Subtracting the fitted plane distinguishes a gradual ramp from an abrupt local
discontinuity. A cell without the configured minimum adjacent support is
invalid.

Confidence measures observation quality only:

```text
support = clamp((point_count - min_count) / (target_count - min_count), 0, 1)
variance_quality = exp(-variance / variance_scale²)
residual_quality = exp(-fit_RMS / residual_scale)
confidence = clamp(coverage × support × variance_quality × residual_quality,
                   0, 1)
```

It does not itself indicate safety or traversability. The downstream
prototype described in [`traversability.md`](traversability.md) consumes it as
one explicit measurement-quality term.

## Visualisation and diagnostics

Each feature marker topic publishes a `DELETEALL` followed by one `CUBE_LIST`
with one point and colour per valid feature. Blue-to-green-to-red colours map
zero to a configurable visual maximum. Visual maxima clamp colours only; they
never alter PointCloud2 values. Marker alpha and cell scale are configurable,
unknown/invalid cells are absent, and fixed IDs prevent accumulation.

`/terrain/feature_diagnostics` reports input age, input and valid cell counts,
neighbour and plane-fit rejection counts, median neighbour count, coverage and
plane residual, processing time/rate, output status, and marker construction
times. It contains no safety classification.

## Performance

On the development host, a repeatable synthetic 500-cell, 100-iteration
construction benchmark measured the original elevation markers at 15.35 ms
per update and the compact `CUBE_LIST` at 3.11 ms per update, an approximately
80% reduction.

The full Gazebo/RViz pipeline sustained approximately 2.7–2.9 Hz for feature
publication, above the 2 Hz prototype target. Feature processing was
118–150 ms for 445–483 valid cells. Individual feature marker construction
was approximately 3.8–5.0 ms. Diagnostic elevation-input age was
0.42–0.66 seconds under the combined simulation, visualization, and sampling
load; it is an observed load-dependent age, not a latency guarantee. Each
marker array remains exactly two markers (`DELETEALL` and one `CUBE_LIST`).

Arena observations were:

| Location | Rover XYZ (m) | R/P/Y (rad) | Elevation / feature cells | Slope median / max (rad) | Roughness median / max (m) | Step median / max (m) | Confidence median |
| --- | --- | --- | --- | --- | --- | --- | ---: |
| Lower section | −1.200, −1.600, 0.105 | 0.000 / 0.000 / 0.000 | 484 / 483 | 0.082 / 0.351 | 0.00031 / 0.00952 | 0.00078 / 0.01860 | 0.141 |
| Slope beginning and visible transition | −0.787, −1.600, 0.112 | 0.000 / −0.047 / 0.000 | 455 / 445 | 0.083 / 0.783 | 0.00045 / 0.03541 | 0.00112 / 0.11166 | 0.00020 |
| Higher smooth slope | −0.272, −1.600, 0.151 | 0.000 / −0.087 / 0.000 | 455 / 455 | 0.066 / 0.166 | 0.00033 / 0.00565 | 0.00076 / 0.02140 | 0.141 |

The low median residual features on the higher slope and localized maximum
step at the transition match the intended qualitative behavior. These
sensor-derived observations do not claim exact arena-angle accuracy.

## Limitations

- Local plane estimates depend on RGB-D density, elevation aggregation,
  occlusion, TF timing, and configured neighbourhood size.
- Step height is a local plane-removed discontinuity statistic, not a physical
  obstacle label.
- Confidence is not a calibrated probability.
- A provisional continuous traversability score is implemented downstream.
  No guaranteed safe/unsafe classification, hazard topic, marker
  recommendation, Nav2 terrain-cost integration, wheel-slip input, ArduPilot
  integration, or RoboClaw integration is implemented.
