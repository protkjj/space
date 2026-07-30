# Traversability calibration and latency benchmark

## Scope and reproducibility

This calibration uses the production functions in `traversability.py`; it
does not reimplement the equations. Generate the deterministic artifacts with:

```bash
ros2 run space_perception traversability_calibration \
  --output-directory docs/calibration
```

Machine-readable results are in
[`calibration/traversability_response.csv`](calibration/traversability_response.csv)
and the generated table is in
[`calibration/traversability_response.md`](calibration/traversability_response.md).
All sweep and runtime values are simulation calibration, not physical safety
limits.

## Synthetic response

All controlled sweeps were monotonic and bounded. Selected results under the
default weighted-sum composition are:

| Input | Free reference | Intermediate response | Maximum response |
| --- | --- | --- | --- |
| Slope | 0–5°: score 1.000 | 15°: 0.877; 25°: 0.686 | ≥30°: 0.650 |
| Roughness | 0–2 mm: 1.000 | 10 mm: 0.944; 15 mm: 0.881 | ≥25 mm: 0.800 |
| Step height | 0–5 mm: 1.000 | 20 mm: 0.850; 30 mm: 0.722 | ≥35 mm: 0.700 |

Coverage, confidence, and variance affect only `uncertainty_penalty`. Coverage
below 0.60 and confidence below 0.10 also make the row invalid, producing a
NaN score rather than favourable unknown terrain. Tests verify smoothstep
continuity at both references and monotonic score response for all six inputs.

`step_max` changed. Everything else is unchanged:

| Parameter | Old | Current |
| --- | ---: | ---: |
| slope free / max | 0.0873 / 0.5236 rad | unchanged |
| roughness free / max | 0.002 / 0.025 m | unchanged |
| step free / max | 0.005 / 0.056 m | **0.005 / 0.035 m**, derived as half the 0.070 m wheel |
| variance free / max | 0.000025 / 0.0004 m² | unchanged |
| coverage / confidence minimum | 0.60 / 0.10 | unchanged |
| slope / roughness / step / quality weights | .35 / .20 / .30 / .15 | unchanged |

This table previously reported `step_max` as `unchanged`, which is how the drift
survived: the one table whose job is to record scoring-parameter change told
anyone auditing the CAD import that nothing needed doing. `step_max` is no longer
a configured value at all — `terrain_traversability_node` derives it from
`space_description/config/rover_geometry.yaml`, so it cannot be reported as
unchanged while the wheel changes underneath it.

Future hardware-derived limits remain unresolved. They require verified mass,
centre of gravity, traction, drivetrain, clearances, terrain mechanics, and
physical testing; the 0.070 m simulated wheel radius alone is insufficient.

## Arena distributions

Percentile columns are P10 / P25 / P50 / P75 / P90 / P95 / maximum.

> **Logged under `step_max = 0.056 m`, which was wrong** — it was half the
> pre-CAD 0.112 m wheel and was never recomputed when the wheel became 0.070 m.
> Maximum step penalties are shown as `logged → corrected`.
>
> The corrected values are exact rather than estimates. The penalty is a
> monotonic smoothstep, so a logged penalty inverts uniquely to the step height
> that produced it — 8.75 mm, 35.26 mm, and 20.07 mm for the three regions —
> which is then re-evaluated at the real 0.035 m limit. The middle inversion is
> independently confirmed: 35.26 mm is exactly the step height recorded for the
> transition region's step-dominant cell in the worked example below.
>
> The transition region therefore **saturates** on step height, where the log
> shows 0.638. Its `traversability` row and the limiting counts understate step
> severity for the same reason, but those are per-cell aggregates that inversion
> cannot recover — restating them honestly needs a re-run of the arena sampling,
> so they are left as logged rather than partially patched. Percentiles below the
> maximum are all zero and unaffected: those step heights sit under
> `step_free = 0.005 m`, so they scored zero under either limit.

### Lower section

Valid/invalid cells: 194 / 289.

| Metric | Percentiles |
| --- | --- |
| slope (rad) | 0.000004 / 0.07779 / 0.08226 / 0.08675 / 0.08801 / 0.09002 / 0.35116 |
| roughness (m) | 0.00000008 / 0.000227 / 0.000314 / 0.000495 / 0.001029 / 0.001273 / 0.009523 |
| step height (m) | 0.00000015 / 0.000501 / 0.000784 / 0.001197 / 0.001989 / 0.002843 / 0.018604 |
| confidence | 0 / 0 / 0.14091 / 0.27061 / 0.28125 / 0.29906 / 0.55961 |
| coverage | 0.507 / 0.607 / 0.857 / 0.893 / 0.929 / 0.929 / 1.0 |
| slope penalty | 0 / 0 / 0 / 0 / 0.0000002 / 0.0000088 / 0.24760 |
| roughness penalty | 0 / 0 / 0 / 0 / 0 / 0 / 0.21226 |
| step penalty | 0 / 0 / 0 / 0 / 0 / 0 / 0.01539 → **0.042874** |
| quality penalty | 0.8723 / 0.8947 / 0.8979 / 0.9347 / 0.9680 / 0.9952 / 0.9999 |
| traversability | 0.8548 / 0.8598 / 0.8653 / 0.8658 / 0.8692 / 0.8909 / 0.9274 |

Limiting counts: uncertainty 12, low confidence 182, invalid 289.

### Transition

Valid/invalid cells: 161 / 303.

| Metric | Percentiles |
| --- | --- |
| slope (rad) | 0.00268 / 0.07238 / 0.08235 / 0.08670 / 0.09340 / 0.30024 / 0.78563 |
| roughness (m) | 0.000153 / 0.000299 / 0.000435 / 0.000838 / 0.001721 / 0.010339 / 0.036060 |
| step height (m) | 0.000148 / 0.000673 / 0.001014 / 0.001795 / 0.003255 / 0.019596 / 0.091426 |
| confidence | 0 / 0 / 0 / 0.23928 / 0.27921 / 0.29159 / 0.55919 |
| coverage | 0.500 / 0.607 / 0.786 / 0.893 / 0.929 / 0.929 / 1.0 |
| slope penalty | 0 / 0 / 0 / 0 / 0.000034 / 0.000653 / 0.59338 |
| roughness penalty | 0 / 0 / 0 / 0 / 0 / 0.000061 / 0.57809 |
| step penalty | 0 / 0 / 0 / 0 / 0 / 0 / 0.63834 → **1.000000** (saturated) |
| quality penalty | 0.8246 / 0.8967 / 0.9034 / 0.9414 / 0.9913 / 0.9961 / 0.9992 |
| traversability | 0.8511 / 0.8588 / 0.8640 / 0.8655 / 0.8763 / 0.9266 / 0.9273 |

Limiting counts: slope 1, step 1, uncertainty 8, low confidence 151,
invalid 303.

### Higher slope

Valid/invalid cells: 201 / 244.

| Metric | Percentiles |
| --- | --- |
| slope (rad) | 0.000007 / 0.000013 / 0.05425 / 0.08260 / 0.08826 / 0.08994 / 0.13289 |
| roughness (m) | 0.00000009 / 0.00000024 / 0.000329 / 0.000664 / 0.001372 / 0.001639 / 0.002503 |
| step height (m) | 0.00000016 / 0.00000046 / 0.000753 / 0.001378 / 0.002280 / 0.002576 / 0.020836 |
| confidence | 0 / 0 / 0.14542 / 0.27381 / 0.28571 / 0.29167 / 0.54800 |
| coverage | 0.536 / 0.679 / 0.857 / 0.893 / 0.929 / 0.929 / 0.964 |
| slope penalty | 0 / 0 / 0 / 0 / 0.000016 / 0.000112 / 0.008336 |
| roughness penalty | 0 / 0 / 0 / 0 / 0 / 0 / 0.001416 |
| step penalty | 0 / 0 / 0 / 0 / 0 / 0 / 0.21032 → **0.503455** |
| quality penalty | 0.8863 / 0.8898 / 0.9004 / 0.9322 / 0.9945 / 0.9990 / 1.0000 |
| traversability | 0.8506 / 0.8596 / 0.8649 / 0.8665 / 0.8671 / 0.8797 / 0.9245 |

Limiting counts: uncertainty 15, low confidence 186, invalid 244.

### Weak edge observations

The lower tails reached coverage 0.18–0.29 and confidence zero in dedicated
edge samples. Cells below coverage 0.60 or confidence 0.10 remain in the cloud
with `valid=0`, score NaN, and limiting code 255. They are never assigned
favourable geometry or displayed as favourable markers.

## Why regional medians are similar

The similarity is explained by measured distributions:

1. At least half of valid cells in all regions are below the geometric free
   references, so median slope, roughness, and step penalties are zero.
2. The local camera view contains mixed terrain; rover pitch does not imply
   every visible cell has that slope.
3. Median quality penalty is consistently about 0.90. Its 0.15 weight
   contributes about 0.135 to all three regional median scores.
4. Invalid filtering removes many low-confidence transition cells from score
   percentiles.
5. Geometry differences occur mainly in the upper tail and minimum score, not
   the median.

The separately normalized geometry median is near zero while quality median is
about 0.90. No parameter was changed merely to force regional medians apart.

## Transition examples and LOW_CONFIDENCE semantics

A valid step-dominant cell at `(0.875, -1.075)` measured:

- slope 0.2065 rad, roughness 0.00823 m, step height 0.03526 m;
- confidence 0.1260, coverage 0.75, 21 neighbours;
- slope/roughness/step/quality penalties
  0.1832 / 0.1802 / **1.0000** / 0.9975 (step penalty logged as 0.6383);
- score **0.4502**, valid 1, limiting factor STEP_HEIGHT (score logged as
  0.5587).

This cell is the clearest case for why the stale `step_max` mattered. Its
0.03526 m step is 0.7 mm **above** what the 0.070 m wheel can climb, so the
correct penalty is fully saturated, not 0.64. Recomputed exactly from the four
penalties above and the published weights (.35/.20/.30/.15):
`1 − (0.35·0.1832 + 0.20·0.1802 + 0.30·1.0 + 0.15·0.9975) = 0.450215`. The same
arithmetic reproduces the logged 0.5587 from the logged 0.6383, confirming the
weights and formula rather than assuming them.

The 0.109 difference is not cosmetic. This is the worked example a reader uses to
validate the scorer, and it published a cell the rover cannot traverse as
mid-range rather than impassable.

By contrast, the largest transition step (0.09143 m) had confidence 0.0211,
coverage 0.607, and saturated geometric/quality penalties. It was invalid,
received code 255, and had a NaN score. This explains the earlier absence of a
step-dominant valid cell; sampling and observation support changed slightly,
and the strongest step cells remain invalid.

`LOW_CONFIDENCE` means confidence is still at or above the validity threshold
but its contribution is the dominant quality limitation. Confidence below
0.10 produces `INVALID`, never `LOW_CONFIDENCE`. Confidence is included once
inside uncertainty; it is not a second geometric penalty.

## Queue and latency benchmark

All sensor-derived streams use BEST_EFFORT, KEEP_LAST, depth 1. The filter
retains its 5 Hz latest-input timer to bound CPU. Elevation now processes on
arrival and retains its timer only to retry temporary TF misses. Features and
scores process on arrival. Duplicate stamps are skipped and inputs older than
the configurable 1.0 seconds are dropped. Diagnostics report duplicate and
stale drop counts.

| Stage | Median / P90 / maximum age after change | Matched median stage delay |
| --- | --- | ---: |
| raw camera | 0.012 / 0.016 / 0.032 s | — |
| filtered | 0.124 / 0.192 / 0.232 s | 0.081 s |
| elevation | 0.176 / 0.246 / 0.300 s | 0.052 s |
| features | 0.276 / 0.374 / 0.394 s | 0.114 s |
| traversability | 0.276 / 0.375 / 0.398 s | 0.0015 s |

Matched camera-to-score delay is 0.244 s median, 0.366 s P90, and 0.374 s
maximum, compared with the previous observed 0.69–1.27 s age. Output remained
2.8 Hz. The target below 0.5 seconds is met. The residual delay is processing
and filter scheduling, not queued backlog.

## Stationary stability and motion

During a 20-second stationary run, 194 persistent valid cells each had 44
observations. Their score standard deviation and range were zero at the
recorded precision; the simulator produced deterministic stationary geometry.
No smoothing was added.

During conservative 0.08 m/s motion, timestamps advanced, the grid followed
the rover in `odom`, score age remained bounded, and old samples did not
accumulate. Command safety reported fresh-command recovery and returned to
STALE after its 0.5-second timeout. RViz stayed alive with compatible QoS;
final colour appearance remains a human visual check.

## Local Nav2 use

The calibrated score now feeds a bounded, non-lethal local-costmap layer.
This integration does not upgrade provisional simulation parameters into
physical limits and does not imply safe/unsafe classification or guaranteed
avoidance. See
[`nav2_traversability_layer.md`](nav2_traversability_layer.md).
