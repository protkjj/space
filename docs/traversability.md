# Continuous terrain traversability prototype

## Scope and interfaces

The prototype scores measured terrain features:

```text
/terrain/features (odom)
  → terrain_traversability_node
  ├── /terrain/traversability
  ├── /terrain/traversability_markers
  └── /terrain/traversability_diagnostics
```

A score of 1 is favourable and 0 is highly unfavourable under this provisional
model. It is not a guaranteed safe/unsafe classification or certification.
Runtime code does not read the arena CAD or STL.

`/terrain/traversability` preserves the input timestamp and frame and contains:

| Field | Type | Units | Offset |
| --- | --- | --- | ---: |
| `x`, `y`, `z` | FLOAT32 | m | 0, 4, 8 |
| `traversability` | FLOAT32 | ratio | 12 |
| `slope_penalty` | FLOAT32 | ratio | 16 |
| `roughness_penalty` | FLOAT32 | ratio | 20 |
| `step_penalty` | FLOAT32 | ratio | 24 |
| `uncertainty_penalty` | FLOAT32 | ratio | 28 |
| `confidence` | FLOAT32 | ratio | 32 |
| `valid` | UINT8 | boolean | 36 |
| `limiting_factor` | UINT8 | code | 37 |

Rows are sorted by X and then Y. One row remains for each input feature cell.
Invalid rows have `valid=0`, `limiting_factor=255`, and a NaN score. This
retains observability without presenting unknown support as favourable.

## Continuous penalties

For a measured feature `f`, lower reference `free`, and upper reference `max`:

```text
t = clamp((f - free) / (max - free), 0, 1)
penalty = t²(3 - 2t)
```

This cubic smoothstep is zero at or below `free`, continuous between
references, and one at or above `max`. Slope, roughness, and step height use
their corresponding references.

Measurement uncertainty remains separate from geometry:

```text
variance_penalty = smoothstep(variance, variance_free, variance_max)
coverage_penalty = smoothstep(1 - coverage, 0, 1 - coverage_min)
confidence_penalty = smoothstep(1 - confidence, 0, 1 - confidence_min)
uncertainty_penalty =
    max(variance_penalty, coverage_penalty, confidence_penalty)
```

Lower coverage, lower feature confidence, or greater elevation variance
therefore increases uncertainty deterministically.

## Composition and validity

The optional strict `conservative_max` mode is:

```text
combined_penalty =
    max(slope_penalty, roughness_penalty, step_penalty, uncertainty_penalty)
traversability = 1 - combined_penalty
```

The default `weighted_sum` mode normalizes the configured nonnegative weights:

```text
combined_penalty = Σ(normalized_weight_i × penalty_i)
traversability = 1 - combined_penalty
```

Every score and penalty is clamped to `[0, 1]`. A cell is valid only when all
input fields are finite, `neighbor_count >= minimum_neighbors`,
`neighborhood_coverage >= coverage_min`, and
`confidence >= confidence_min`.

Dominant limiting-factor codes are:

| Code | Meaning |
| ---: | --- |
| 0 | NONE |
| 1 | SLOPE |
| 2 | ROUGHNESS |
| 3 | STEP_HEIGHT |
| 4 | UNCERTAINTY (variance or coverage component) |
| 5 | LOW_CONFIDENCE |
| 255 | INVALID |

The largest active weighted contribution wins in `weighted_sum` mode; the
largest raw penalty wins in `conservative_max` mode. Within uncertainty, the
code distinguishes confidence from variance/coverage. Exact ties use the
smaller listed code, making results deterministic.

## Provisional simulation parameters

These values tune the first Gazebo prototype; they are not final mechanical
limits:

| Parameter | Value | Basis |
| --- | ---: | --- |
| `slope_free` | 0.0873 rad (5°) | near-flat allowance |
| `slope_max` | 0.5236 rad (30°) | conservative simulation upper reference |
| `roughness_free` | 0.002 m | measured smooth-surface residuals |
| `roughness_max` | 0.025 m | simulation discrimination range |
| `step_free` | 0.005 m | small residual allowance |
| `step_max` | 0.056 m | half the current 0.112 m wheel radius |
| `variance_free` | 0.000025 m² | 5 mm standard-deviation equivalent |
| `variance_max` | 0.0004 m² | 20 mm standard-deviation equivalent |
| `coverage_min` | 0.60 | local-neighbour support |
| `confidence_min` | 0.10 | existing feature-quality distribution |
| `minimum_neighbors` | 8 | plane-neighbour support |

The wheel radius is defined in
`space_description/urdf/space_rover.urdf.xacro`. Hardware limits must later be
derived from verified mass, centre of gravity, traction, suspension,
clearances, drivetrain capability, operating environment, and test evidence.

The weighted-mode defaults are slope 0.35, roughness 0.20, step 0.30, and
uncertainty 0.15. This keeps the deliberately conservative feature-confidence
term visible without allowing it to hide every geometric distinction observed
in the arena. The unweighted `conservative_max` mode remains selectable for
stricter analysis.

## Visualization and diagnostics

Valid cells are published as a fixed-ID `CUBE_LIST`, green at high score,
yellow at intermediate score, and red at low score. Invalid cells are omitted.
Each update starts with `DELETEALL`, so markers cannot accumulate. Colours are
display mappings only and do not alter output values or constitute a safety
class.

Diagnostics report input age and counts, valid/invalid counts, score range,
median individual penalties, limiting-factor distribution, processing and
marker duration, effective rate, publication status, and composition mode.
They intentionally report no safe/unsafe counts.

## Arena validation

The complete Gazebo/RViz pipeline was sampled with conservative 0.08 m/s
commands. Values are sensor-derived and load-dependent:

| Region | Rover XYZ / pitch | Feature / valid cells | Median / minimum score | Median slope / roughness / step / uncertainty penalties | Maximum slope / roughness / step / uncertainty penalties | Processing / marker time |
| --- | --- | --- | --- | --- | --- | --- |
| Lower section | −1.200, −1.600, 0.105 m / 0.000 rad | 483 / 194 | 0.865 / 0.716 | 0 / 0 / 0 / 0.898 | 0.248 / 0.212 / 0.015 / 1.000 | 4–11 / 4–6 ms |
| Slope transition | −0.818, −1.600, 0.111 m / −0.039 rad | 462 / 166 | 0.864 / 0.508 | 0 / 0 / 0 / 0.902 | 0.569 / 0.590 / 0.614 / 1.000 | 4.4 / 1.1 ms |
| Higher smooth slope | −0.325, −1.600, 0.147 m / −0.087 rad | 480 / 232 | 0.865 / 0.493 | 0 / 0 / 0 / 0.901 | 0.255 / 0.195 / 0.780 / 1.000 | 6.0 / 4.2 ms |

The configured slope-free reference exceeds the median observed local slope,
so median slope penalty remained zero even on the higher section. Local cells
still showed geometric penalties and reduced minimum scores. This is reported
as observed rather than retuning solely to force an expected median.

After limiting factors were defined as weighted score contributions, a
transition sample contained 2 slope-limited, 5 uncertainty-limited, 155
low-confidence-limited, and 301 invalid cells. No valid cell was step-dominant:
the strongest step observations coincided mostly with weak support or were
outweighed by slope. The lower section contained 12 uncertainty-limited, 182
low-confidence-limited, and 289 invalid cells.

Weak edge-of-view observations had coverage as low as 0.18–0.29 and confidence
of zero. They became invalid; they were retained with NaN scores and omitted
from markers. Output remained in `odom`, marker arrays stayed fixed at two
markers, and the traversability output sustained approximately 2.1–2.7 Hz.
Feature-to-output age observed in diagnostics was about 0.69–1.27 seconds
under combined Gazebo, RViz, and sampling load. This preserved input stamp is
also the practical point-cloud-to-score age for the current pipeline.

The command watchdog reported recovery when commands began and returned to
STALE after 0.5 seconds without input. Scoring and markers continued while the
rover moved, without blocking that stop behavior. RViz loaded the score cloud
with BEST_EFFORT QoS and the compact marker display without QoS warnings.
Colour appearance still requires human visual confirmation.

## Limitations

- Parameters are arena-oriented simulation tuning, not certified rover limits.
- Confidence and uncertainty are quality heuristics, not probabilities.
- Scores inherit RGB-D, TF, elevation-grid, and feature-estimation limitations.
- No guaranteed safe/unsafe classification, global terrain planning,
  guaranteed terrain avoidance, marker-drop recommendation, dispenser control,
  wheel-slip integration, ArduPilot integration, or RoboClaw integration is
  implemented.

Calibration curves, regional distributions, latency, and stability are
documented in
[`traversability_calibration.md`](traversability_calibration.md). The
provisional local Nav2 soft-cost integration is documented in
[`nav2_traversability_layer.md`](nav2_traversability_layer.md).
