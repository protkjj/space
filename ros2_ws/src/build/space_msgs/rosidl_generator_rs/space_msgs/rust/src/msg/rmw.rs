#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};


#[link(name = "space_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__space_msgs__msg__RoverSpec() -> *const std::ffi::c_void;
}

#[link(name = "space_msgs__rosidl_generator_c")]
extern "C" {
    fn space_msgs__msg__RoverSpec__init(msg: *mut RoverSpec) -> bool;
    fn space_msgs__msg__RoverSpec__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<RoverSpec>, size: usize) -> bool;
    fn space_msgs__msg__RoverSpec__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<RoverSpec>);
    fn space_msgs__msg__RoverSpec__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<RoverSpec>, out_seq: *mut rosidl_runtime_rs::Sequence<RoverSpec>) -> bool;
}

// Corresponds to space_msgs__msg__RoverSpec
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Physical specification of ONE rover -- the evaluation layer's only
/// rover-dependent input (CLAUDE.md: dual-rover transform layer).
///
/// This type exists because rover limits kept leaking into "tuning" configs.
/// space_perception's TraversabilityConfig carried step_max = 0.056 m, which
/// docs/traversability.md records as "half the current 0.112 m wheel radius" --
/// a rover property disguised as a threshold. When the CAD import changed the
/// wheel to 0.070 m, that value silently became 1.6x too permissive. Rover
/// limits belong here and are derived, never hand-copied.
///
/// Embedded in TraversabilityScore so a derived map always travels with the
/// assumptions it was computed under.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct RoverSpec {
    /// 'small' | 'medium' | ...
    pub rover_id: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub mass_kg: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub wheel_radius_m: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub wheel_width_m: f32,

    /// static, mass / total contact patch
    pub ground_pressure_kpa: f32,

    /// MECHANICAL limit only: the steepest grade this vehicle can physically climb.
    /// Deliberately NOT the mission's hazard boundary and NOT a scoring saturation
    /// point. Those are different physical quantities that happened to share this
    /// name, which is why the codebase held three different numbers (20 deg, 30 deg,
    /// and an untested one) for what looked like one parameter. They are now split:
    ///   this field                       -> mechanical capability (ramp test)
    ///   VerdictThresholds.hazard_slope   -> CLAUDE.md 1.4 verdict boundary
    ///   ScoringConfig.slope_penalty_saturation_rad -> evaluation tuning
    /// They are related by policy, not by derivation, so none is computed from
    /// another.
    pub max_climb_angle_rad: f32,

    /// widest footprint + clearance margin
    pub min_passable_width_m: f32,

    /// lowest chassis point to ground
    pub ground_clearance_m: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub has_grousers: bool,

    /// Where these numbers came from. MEASURED means our own CAD or scale; ASSUMED
    /// means a rover we do not possess, so every score derived from it is
    /// provisional. Consumers use this to decide what needs recomputing when the
    /// real medium-rover numbers arrive -- that is the whole point of keeping the
    /// observation and estimation layers as the canonical record.
    pub provenance: u8,

    /// Free text: which drawing, datasheet, or guess each number traces back to.
    pub provenance_note: rosidl_runtime_rs::String,

}

impl RoverSpec {

    // This constant is not documented.
    #[allow(missing_docs)]
    pub const PROVENANCE_UNKNOWN: u8 = 0;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const PROVENANCE_MEASURED: u8 = 1;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const PROVENANCE_ASSUMED: u8 = 2;

}


impl Default for RoverSpec {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !space_msgs__msg__RoverSpec__init(&mut msg as *mut _) {
        panic!("Call to space_msgs__msg__RoverSpec__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for RoverSpec {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { space_msgs__msg__RoverSpec__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { space_msgs__msg__RoverSpec__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { space_msgs__msg__RoverSpec__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for RoverSpec {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for RoverSpec where Self: Sized {
  const TYPE_NAME: &'static str = "space_msgs/msg/RoverSpec";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__space_msgs__msg__RoverSpec() }
  }
}


#[link(name = "space_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__space_msgs__msg__SlipEstimate() -> *const std::ffi::c_void;
}

#[link(name = "space_msgs__rosidl_generator_c")]
extern "C" {
    fn space_msgs__msg__SlipEstimate__init(msg: *mut SlipEstimate) -> bool;
    fn space_msgs__msg__SlipEstimate__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<SlipEstimate>, size: usize) -> bool;
    fn space_msgs__msg__SlipEstimate__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<SlipEstimate>);
    fn space_msgs__msg__SlipEstimate__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<SlipEstimate>, out_seq: *mut rosidl_runtime_rs::Sequence<SlipEstimate>) -> bool;
}

// Corresponds to space_msgs__msg__SlipEstimate
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Wheel slip -- the rover's signature measurement (mission doc section 1.2).
///
///   lambda = (v_wheel - v_actual) / v_wheel
///
/// Depth gives geometry only; it cannot tell a safe 15 deg slope from a sinking
/// one. Only the slip a rover actually experiences can. Treat this as a RELATIVE
/// indicator ("this patch slips more than that one"), never as a calibrated
/// absolute -- section 1.3 holds even with VIO error, but only relatively.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct SlipEstimate {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::rmw::Header,

    /// lambda, dimensionless. Meaningless unless `valid` is true; publishers set it
    /// to NaN in that case so a consumer that ignores `valid` fails loudly.
    pub slip_ratio: f32,

    /// Encoder-implied forward speed, m/s. Contaminated by slip on purpose: a
    /// spinning wheel still reports motion. This is the numerator's inflated term.
    pub v_wheel: f32,

    /// Wheel-INDEPENDENT forward speed, m/s. Must not fuse wheel encoders, or the
    /// ratio becomes circular (section 1.3). See `source`.
    pub v_actual: f32,

    /// False -> discard slip_ratio entirely. Set when wheel speed is below the
    /// estimator's floor (a stationary rover has no defined slip) or when an input
    /// is stale. Independent of `quality`: this is "was lambda computable at all".
    pub valid: bool,

    /// Confidence in v_actual, 0.0 (useless) .. 1.0 (fully trusted). Derived from
    /// the actual-velocity source's covariance, overridden by a VIO status topic
    /// when one is available. Independent of `valid`: a low-quality reading is
    /// still usable for the relative comparison of section 1.3, so the CONSUMER
    /// picks the threshold rather than the estimator silently dropping data.
    pub quality: f32,

    /// Which producer supplied v_actual. Published so a consumer can enforce
    /// section 1.3 itself: SOURCE_EKF fuses wheel encoders, which makes the slip
    /// ratio circular. That failure is invisible at runtime -- the arithmetic still
    /// succeeds and the value still looks plausible -- so it has to be typed.
    pub source: u8,

}

impl SlipEstimate {

    // This constant is not documented.
    #[allow(missing_docs)]
    pub const SOURCE_UNKNOWN: u8 = 0;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const SOURCE_SIM_GROUND_TRUTH: u8 = 1;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const SOURCE_VIO: u8 = 2;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const SOURCE_EKF: u8 = 3;

}


impl Default for SlipEstimate {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !space_msgs__msg__SlipEstimate__init(&mut msg as *mut _) {
        panic!("Call to space_msgs__msg__SlipEstimate__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for SlipEstimate {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { space_msgs__msg__SlipEstimate__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { space_msgs__msg__SlipEstimate__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { space_msgs__msg__SlipEstimate__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for SlipEstimate {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for SlipEstimate where Self: Sized {
  const TYPE_NAME: &'static str = "space_msgs/msg/SlipEstimate";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__space_msgs__msg__SlipEstimate() }
  }
}


#[link(name = "space_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__space_msgs__msg__TerrainEstimate() -> *const std::ffi::c_void;
}

#[link(name = "space_msgs__rosidl_generator_c")]
extern "C" {
    fn space_msgs__msg__TerrainEstimate__init(msg: *mut TerrainEstimate) -> bool;
    fn space_msgs__msg__TerrainEstimate__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<TerrainEstimate>, size: usize) -> bool;
    fn space_msgs__msg__TerrainEstimate__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<TerrainEstimate>);
    fn space_msgs__msg__TerrainEstimate__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<TerrainEstimate>, out_seq: *mut rosidl_runtime_rs::Sequence<TerrainEstimate>) -> bool;
}

// Corresponds to space_msgs__msg__TerrainEstimate
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// The CANONICAL terrain record: observation layer + estimation layer.
///
/// CLAUDE.md's dual-rover transform layer makes this the thing we store and
/// transfer. S_small and S_medium are DERIVED from it by substituting a
/// RoverSpec, so they are never the record of truth. When the real medium-rover
/// specification arrives, this message is replayed and only the score is
/// recomputed -- no re-survey.
///
/// Nothing rover-specific may be added here. Slip is the one apparent
/// exception: lambda is a terrain x rover interaction, not a terrain constant,
/// so it is named LAYER_SLIP_SMALL to keep that explicit. It is an OBSERVATION
/// made by our small rover, never a property the medium rover would reproduce.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct TerrainEstimate {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::rmw::Header,

    /// Multi-layer grid. Layer names are contractual -- look layers up by the
    /// constants below, never by index, because layer order is not guaranteed.
    pub grid: grid_map_msgs::msg::rmw::GridMap,

    /// Unobserved cells carry NaN in every layer. Consumers must treat NaN as
    /// "no data", distinct from a measured zero.
    /// --- Estimation provenance ------------------------------------------------
    /// Which soil proxy produced the estimation layers. The first implementation is
    /// a deliberate placeholder (CLAUDE.md 4: no terramechanics before field data),
    /// so its output is only meaningful for RANKING cells against each other, never
    /// as an absolute soil property. Recording the model identity here is what lets
    /// a later, calibrated model be swapped in and old records re-derived.
    pub soil_model_id: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub soil_model_version: rosidl_runtime_rs::String,

}

impl TerrainEstimate {
    /// --- Observation layer: terrain-intrinsic geometry -------------------------
    pub const LAYER_SLOPE: &'static str = "slope_rad";


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const LAYER_ROUGHNESS: &'static str = "roughness_m";


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const LAYER_STEP: &'static str = "step_height_m";

    /// --- Observation layer: what our small rover actually felt ----------------
    pub const LAYER_SLIP_SMALL: &'static str = "slip_small";


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const LAYER_SLIP_QUALITY: &'static str = "slip_quality";

    /// Number of independent lambda measurements accumulated in each cell. A cell
    /// crossed once and a cell crossed three times must be distinguishable, so that
    /// confidence rises as field data accumulates instead of being a fixed guess.
    pub const LAYER_SLIP_SAMPLES: &'static str = "slip_samples";

    /// --- Estimation layer: soil proxy ----------------------------------------
    /// A RANK, not a measurement. See soil_model_id below.
    pub const LAYER_SOIL_DIFFICULTY: &'static str = "soil_difficulty";


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const LAYER_SOIL_CONFIDENCE: &'static str = "soil_confidence";

}


impl Default for TerrainEstimate {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !space_msgs__msg__TerrainEstimate__init(&mut msg as *mut _) {
        panic!("Call to space_msgs__msg__TerrainEstimate__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for TerrainEstimate {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { space_msgs__msg__TerrainEstimate__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { space_msgs__msg__TerrainEstimate__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { space_msgs__msg__TerrainEstimate__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for TerrainEstimate {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for TerrainEstimate where Self: Sized {
  const TYPE_NAME: &'static str = "space_msgs/msg/TerrainEstimate";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__space_msgs__msg__TerrainEstimate() }
  }
}


#[link(name = "space_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__space_msgs__msg__TraversabilityScore() -> *const std::ffi::c_void;
}

#[link(name = "space_msgs__rosidl_generator_c")]
extern "C" {
    fn space_msgs__msg__TraversabilityScore__init(msg: *mut TraversabilityScore) -> bool;
    fn space_msgs__msg__TraversabilityScore__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<TraversabilityScore>, size: usize) -> bool;
    fn space_msgs__msg__TraversabilityScore__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<TraversabilityScore>);
    fn space_msgs__msg__TraversabilityScore__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<TraversabilityScore>, out_seq: *mut rosidl_runtime_rs::Sequence<TraversabilityScore>) -> bool;
}

// Corresponds to space_msgs__msg__TraversabilityScore
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// A DERIVED traversability map for one specific rover.
///
/// Published on /traversability/small and /traversability/medium. Both come from
/// the same evaluate() call with a different RoverSpec -- never from scaling one
/// into the other. CLAUDE.md is explicit that lambda is a terrain x rover
/// interaction: the same sand that slips our 3 kg rover 15% will slip a medium
/// rover differently because contact pressure, wheel diameter, mass, and grouser
/// shape all differ. Scaling S_small into S_medium is physically wrong.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct TraversabilityScore {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::rmw::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub rover_id: rosidl_runtime_rs::String,

    /// The exact specification this score was computed under, carried inline rather
    /// than referenced. If rover_spec.provenance is PROVENANCE_ASSUMED, every cell
    /// here is provisional and must be recomputed when real numbers land -- and this
    /// field is how you find out which maps those are.
    pub rover_spec: super::super::msg::rmw::RoverSpec,

    /// Layers keyed by the constants below.
    pub grid: grid_map_msgs::msg::rmw::GridMap,

    /// --- Provenance, so a recompute can be targeted instead of global ---------
    /// Stamp of the TerrainEstimate this was derived from.
    pub terrain_stamp: builtin_interfaces::msg::rmw::Time,

    /// Copied from the source TerrainEstimate: a score is only as valid as the soil
    /// model behind it.
    pub soil_model_id: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub soil_model_version: rosidl_runtime_rs::String,

    /// Version of the evaluation function itself, separate from the soil model,
    /// because scoring weights and the soil proxy change independently.
    pub evaluator_version: rosidl_runtime_rs::String,

}

impl TraversabilityScore {
    /// Traversability score, higher is better. NaN where the terrain record had no
    /// data or the observation-quality gate rejected the cell.
    pub const LAYER_SCORE: &'static str = "score";

    /// Which term dominated the score, so a low value is explainable rather than an
    /// opaque number. Values are LIMIT_* below.
    pub const LAYER_LIMITING_FACTOR: &'static str = "limiting_factor";


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const LIMIT_NONE: u8 = 0;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const LIMIT_SLOPE: u8 = 1;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const LIMIT_ROUGHNESS: u8 = 2;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const LIMIT_STEP: u8 = 3;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const LIMIT_SOIL: u8 = 4;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const LIMIT_CLEARANCE: u8 = 5;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const LIMIT_WIDTH: u8 = 6;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const LIMIT_NO_DATA: u8 = 7;

}


impl Default for TraversabilityScore {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !space_msgs__msg__TraversabilityScore__init(&mut msg as *mut _) {
        panic!("Call to space_msgs__msg__TraversabilityScore__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for TraversabilityScore {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { space_msgs__msg__TraversabilityScore__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { space_msgs__msg__TraversabilityScore__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { space_msgs__msg__TraversabilityScore__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for TraversabilityScore {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for TraversabilityScore where Self: Sized {
  const TYPE_NAME: &'static str = "space_msgs/msg/TraversabilityScore";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__space_msgs__msg__TraversabilityScore() }
  }
}


