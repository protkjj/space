# Pending: values that need measurement, and known contamination not yet fixed

One place for everything that cannot be settled at a desk. Two reasons it exists:

1. **Measurement-pending constants.** Several thresholds are placeholders
   because deciding them from a desk would be guessing. Scattered across code
   comments they are invisible; collected here, the whole set can be filled in
   one session once the hardware and the arena are available.
2. **Known contamination, deliberately not fixed.** Found while working on
   something else and recorded rather than chased, so the current change stays
   scoped.

Every placeholder in the code links back here. If you add one, add a row.

---

## 1. Measurement-pending constants

Each row names the test that produces the value. Test IDs are introduced here;
there was no existing numbering.

| ID | Value | Where it lives | Current placeholder | What the test must produce |
|---|---|---|---|---|
| **V1** | `max_climb_angle_rad` | `space_mission/config/rover_spec_small.yaml` | 0.349 rad (20°), conservative | Ramp test: steepest grade the rover holds without runaway slip, on arena sand. Then decide separately what fraction of it becomes the hazard boundary — that is policy, not a copy. |
| **V2** | `safe_roughness_m` (σ₀) | `space_mission/verdict.py` | `None` — refuses to run | Arena roughness distribution. Pick σ₀ as a **percentile** of measured roughness, not an absolute figure. CLAUDE.md §1.4 writes "roughness < σ₀" without defining it; a desk number would be wrong by construction. |
| **V3** | `min_slip_quality`, `quality_variance_scale` | `traversability_transform.ObservationGate`, `space_mission/config/slip.yaml` | 0.3, 0.01 | VIO covariance scale on real terrain: what variance corresponds to a reading worth trusting. Cannot be set before a VIO node exists and has been run outdoors. |
| **V4** | `CONFIDENCE_HALF_SAMPLES`, and the whole soil proxy | `space_mission/soil_model.py` | 2.0 samples; `relative_difficulty_placeholder` v0.1.0 | Repeat-pass slip measurements on the same cells: how many crossings before λ stabilises. Also the data that lets the placeholder be replaced with a calibrated model. |
| **V5** | `assumed_sinkage`, hence `ground_pressure_kpa` | `space_description/config/rover_geometry.yaml` | 0.005 m assumed | Press the assembled rover into arena sand and measure the contact patch directly. |
| **V6** | `has_grousers` | `space_mission/config/rover_spec_small.yaml` | `false`, from the CAD reading smooth | Look at the physical Pololu 37D wheel. Any slip-to-soil interpretation that depends on tread is affected. |
| **V7** | `mass_total` | `space_description/config/rover_geometry.yaml` | 2.725 kg design estimate | Weigh the assembled rover, dispenser included. 3.0 kg is the competition **ceiling**, not a design value. |
| **V8** | Medium rover spec, all fields | `space_mission/config/rover_spec_medium.yaml` | Invented; `provenance: assumed` | Not a measurement — an external specification we have not been given. `min_passable_width_m` and `wheel_radius_m` dominate marker-site selection, so they matter most. Every `TraversabilityScore` whose `rover_spec.provenance` is `PROVENANCE_ASSUMED` must be recomputed once these land. |

### Why these stay placeholders

Setting them from a desk produces numbers that look authoritative and are
wrong — the same failure mode as the stale `step_max`, where a plausible value
survived because nothing downstream complained. A placeholder that refuses to
run (`safe_roughness_m = None`) is safer than a plausible guess.

---

## 2. Known contamination, recorded not fixed

| Item | Where | Why deferred |
|---|---|---|
| Arena-validation per-cell aggregates | `docs/traversability.md` "Arena validation", `docs/traversability_calibration.md` "Arena distributions" | Maximum step penalties were corrected exactly by inverting the monotonic smoothstep. The `traversability` percentile rows and limiting-factor counts are per-cell aggregates that inversion cannot recover — they need the arena sampling re-run. Partially patching them would produce an internally inconsistent table. |
| Wheel rotational inertia | `space_description/urdf/space_rover.urdf.xacro`, wheel `<inertial>` | Isotropic 0.00045 for all three axes. A cylinder of r=0.070, w=0.040, m=0.14 has spin inertia `m·r²/2 = 0.000343` and transverse `m(3r²+h²)/12 = 0.000190` — so the spin axis is ~31% too high and the transverse axes ~137% too high. Spin inertia governs wheel spin-up, which directly shapes slip transients. Not changed with the mass fix because it alters contact dynamics and needs its own before/after comparison. |
| Collision box cannot match the CAD exactly | `space_description/config/rover_geometry.yaml` | The mesh dips 8 mm below the contact plane at the wheel hubs, so an axis-aligned box spanning the full bbox would rest the rover on its chassis. The box now spans clearance→top, which covers the chassis laterally and longitudinally but under-covers vertically at the hubs. A convex hull or mesh collision would represent it properly. |
| `space_gazebo` lint | `space_gazebo` | 35 pre-existing failures: it uses `ament_lint_auto` (which pulls in `ament_copyright`) while shipping Python, and no Python file in the workspace carries a copyright header. `space_description` and `space_perception` use explicit `ament_flake8`/`ament_pep257` instead. |
| Slope arena produces no traversability cells | `arena_test_slope_v04` | The rover drives 4.3 m there, but `/terrain/elevation_points` stays empty while the same pipeline yields 51k cells on `arena_terrain_v04`. Likely the point-cloud crop bounds or the elevation grid extent do not match that world's geometry. Not chased -- the terrain arena is the demo world. |
| Rover high-centres at x ~= -0.07 on `arena_terrain_v04` | terrain vs 30 mm chassis clearance | Verified NOT a regression: with the old 0.084 m collision box the rover stops at the same place (1.116 m travelled vs 1.123 m). The difference is attitude -- the CAD-honest box levers it to +65 deg pitch where the old box left it at -20 deg. A grid sweep of the mesh underside shows P0-P75 between 0.030 and 0.048 m, so the low clearance is a broad feature, not one stray rail: the old box floated 39 mm above the real chassis. Left honest rather than relaxed, for the same reason the mass was corrected. |
| `space_controller` test collection fails | `space_controller/test/test_wheel_motor_driver.py` | An untracked work-in-progress test imports `space_controller.wheel_motor_driver`, which has never existed in this tree. |

---

## 3. Not started — mission-core work outside the current scope

Recorded so the gap is visible, not as a plan.

| Item | Status |
|---|---|
| VIO publishing node | Absent. Hardware `v_actual` has no source. **Simulation is unaffected**: `slip.yaml` points `actual_odom_topic` at Gazebo ground-truth `/odom`, which never reads the wheels, so CLAUDE.md §1.3 non-circularity holds and slip works today in sim. |
| `TerrainEstimate` producer | The `grid_map_msgs/GridMap` record is defined but nothing publishes it yet; `evaluate()` currently runs on plain arrays. |
| `mission_manager` state machine | Absent (CLAUDE.md §3.3). |
| `marker_dispenser` | Absent (§3.4). Must stay separable: a dispenser failure cannot stop map generation (§1.5). |
| `roboclaw_node` | Absent. No hardware motor drive, and no `/wheel_odom`. |
| ArduPilot interface | `space_ardupilot_interface` is an empty package. |
| `elevation_mapping` integration | External package wired in launch only. |
