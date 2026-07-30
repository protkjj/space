# Dual-rover traversability transform layer

Interface contract only. No evaluation logic is implemented yet; every function
named here raises `NotImplementedError`.

## Why two maps

The rover produces two products, and treating them as one was a mistake.

- **`S_small`** — our own rover's movement decisions. Its objective is not
  "easy to traverse" but "easy to traverse *and* informative", so an
  exploration term belongs in it.
- **`S_medium`** — whether the follow-on medium rover can actually pass.
  Marker placement is judged by this map, because the marker's consumer is the
  medium rover. A marker in a gap only our 3 kg rover fits through is
  worthless.

## Why `S_medium` is not `S_small` scaled

λ is not a terrain constant. It is the result of a **terrain × rover**
interaction. Sand that slips our rover 15% will slip a medium rover
differently: contact pressure, wheel diameter, mass, and grouser shape all
differ. Scaling one score into the other is physically wrong, not merely
imprecise.

```
observation   terrain geometry (θ, σ, step)  +  λ our rover actually felt
                                 |
estimation    soil_model: λ + our spec -> soil difficulty RANK
                                 |
                   +-------------+-------------+
evaluation      [small spec]             [medium spec]
                 S_small                   S_medium
```

Only **observation and estimation are canonical**. Both scores are derived by
substituting a `RoverSpec` into the same `evaluate()`. When the real medium
specification arrives, the stored record is replayed and only the score is
recomputed — no re-survey.

## Message contract

| Type | Role |
|---|---|
| `space_msgs/TerrainEstimate` | Canonical record. `grid_map_msgs/GridMap` + layer-name constants + soil-model provenance. |
| `space_msgs/RoverSpec` | One rover's physical spec, with `provenance` marking measured vs assumed. |
| `space_msgs/TraversabilityScore` | Derived map. Carries the `RoverSpec` it was computed under, inline. |
| `space_msgs/SlipEstimate` | Per-sample λ feeding the observation layer. |

Grid layers are addressed by the `LAYER_*` constants, never by index — layer
order is not guaranteed. Unobserved cells are **NaN in every layer**, which is
distinct from a measured zero. A planner reading zero as "traversable but bad"
where we meant "unknown" is the failure this rule prevents.

### Topics

| Topic | Type |
|---|---|
| `/slip` | `space_msgs/SlipEstimate` |
| `/terrain/estimate` | `space_msgs/TerrainEstimate` |
| `/traversability/small` | `space_msgs/TraversabilityScore` |
| `/traversability/medium` | `space_msgs/TraversabilityScore` |

## Where the soil proxy lives

`space_mission/soil_model.py`, isolated behind two functions, and it is a
**placeholder**. Per CLAUDE.md §4 there is no terramechanics model before field
data. Its output supports exactly one claim: *this cell is harder than that
cell*. It is not an absolute soil property and must never be thresholded
against a physical constant.

`SOIL_MODEL_ID` / `SOIL_MODEL_VERSION` are stamped into every
`TerrainEstimate`, so records made under the placeholder can be re-derived once
a calibrated model replaces it.

### Confidence must accumulate

`soil_confidence` is a function of **sample count** and sample quality. A cell
crossed once and a cell crossed three times are not equally trustworthy — the
whole value of a rover that drives on the terrain is that confidence rises as
it works. Hence the `slip_samples` layer.

### The quality gate runs before estimation

`min_slip_quality` is applied in `soil_model.accepts_sample()`, **upstream** of
scoring. A low-confidence λ that reaches the soil proxy corrupts the estimation
layer, and because both maps derive from that layer, one bad sample breaks
`S_small` and `S_medium` at once. Gating at the score stage would be too late.

## Config split

The three kinds of value that `space_perception.TraversabilityConfig`
currently mixes:

| Kind | Home | Examples |
|---|---|---|
| Rover limits | `RoverSpec` | `max_climb_angle_rad`, `max_step_height_m` (derived), `ground_clearance_m` |
| Observation gates | `ObservationGate` | `min_slip_quality`, `coverage_min`, `confidence_min` |
| Scoring weights | `ScoringConfig` | `weight_slope`, `weight_soil`, `composition_mode` |

**If a value can be derived from the rover, it does not belong in a config.**
This is not a style preference. `TraversabilityConfig.step_max = 0.056` is
recorded in `docs/traversability.md` as "half the current 0.112 m wheel
radius" — a rover property written down as a threshold. The CAD import moved
the wheel to 0.070 m and nothing recomputed it, so traversability has been
judging steps against a rover 1.6× more capable than the one we own, silently.
`RoverSpec.max_step_height_m` is a derived property precisely so that cannot
recur.

Hard limits from the spec **veto** a cell rather than adding a weighted
penalty. A step taller than the wheel can climb is not "somewhat worse", it is
impassable, and no weighting of other terms should outvote that.

## One slope limit was three quantities

The tree held 20° and 30° under names close enough to be mistaken for one
parameter. They are now separated, and **none is derived from another** —
they are related by policy, not arithmetic:

| Quantity | Home | Value | Status |
|---|---|---|---|
| Mechanical climbing capability | `RoverSpec.max_climb_angle_rad` | 20° | **Conservative placeholder**, no ramp test run |
| Mission hazard boundary | `VerdictThresholds.hazard_slope_rad` | 20° | CLAUDE.md §1.4 |
| Penalty curve saturation | `ScoringConfig.slope_penalty_saturation_rad` | 30° | Evaluation tuning |

Deriving one from another is the reflex that is *correct* for `step_max` — that
really is half a wheel radius — and *wrong* here. A mission may cap itself well
below what the vehicle can do, and a penalty curve may saturate above the
hazard line so scores keep discriminating past it. When a ramp test yields the
mechanical limit, "what fraction of it is the hazard boundary" becomes an
explicit decision rather than an accident of naming.

Two properties of §1.4 that are easy to misread from its prose:

- `safe_slope_rad` and `hazard_slope_rad` are the **same** boundary (SAFE needs
  < 20°, HAZARD triggers at ≥ 20°), so **slope is binary** and can never by
  itself produce a MARGINAL verdict. MARGINAL comes only from the slip band
  (15–40%) or from roughness.
- §1.4 writes "roughness < σ₀" and **never defines σ₀**. `safe_roughness_m` is
  therefore `None` and `validate()` refuses to run without it. A threshold that
  defaulted to infinity would mark every cell SAFE on the roughness axis — the
  same silent-pass failure `step_max` produced.

Step height is *not* in the threshold table: how tall a step is impassable is a
wheel property, so `classify()` takes it from `RoverSpec.max_step_height_m`.
Putting it in a mission config is how these values went stale to begin with.

## Verdicts do not choose marker sites

CLAUDE.md §1.5 calls this the recurring mistake, so it is worth restating at
interface level. A verdict describes terrain **as our rover found it**. Marker
sites are chosen on `S_medium`, because the marker's only consumer is the
medium rover — a site our 3 kg rover calls SAFE may sit in a gap the medium
rover cannot enter, which makes the marker worthless.

## Resolved

1. **Exploration term → its own topic, `/exploration/objective`.** Terrain
   measurements are a permanent asset the medium rover will still be using
   later; an exploration objective is volatile and changes whenever the rover
   moves. Sharing a topic would drag the canonical record's lifetime down to
   that of the volatile term, and would force the whole grid to republish at
   the faster rate. It carries a bare `grid_map_msgs/GridMap` rather than a
   `space_msgs` wrapper: provenance metadata exists so a canonical record can
   be re-derived, and this product is explicitly *not* canonical. The absence
   of that metadata is the type-level statement that it is disposable.
2. **Per-field provenance → prose, but enumerated.** A per-field enum would
   double the schema to serve a human judgement call. Instead
   `provenance_note` lists unconfirmed fields **by name**. The medium spec is
   wholly `ASSUMED` so it needs no enumeration; only the small spec mixes, and
   its note names all three weak fields (`max_climb_angle_rad`,
   `has_grousers`, `ground_pressure_kpa`) with why each is distrusted.

## Still open

- **`step_max` in `space_perception` and the nav2 footprints are stale.** Being
  fixed as part of the single-source-of-truth wiring, not left to this layer:
  patching the numbers without wiring the source would guarantee a fourth
  round of the same bug on the next CAD change.
