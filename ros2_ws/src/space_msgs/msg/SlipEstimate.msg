# Wheel slip -- the rover's signature measurement (mission doc section 1.2).
#
#   lambda = (v_wheel - v_actual) / v_wheel
#
# Depth gives geometry only; it cannot tell a safe 15 deg slope from a sinking
# one. Only the slip a rover actually experiences can. Treat this as a RELATIVE
# indicator ("this patch slips more than that one"), never as a calibrated
# absolute -- section 1.3 holds even with VIO error, but only relatively.

std_msgs/Header header

# lambda, dimensionless. Meaningless unless `valid` is true; publishers set it
# to NaN in that case so a consumer that ignores `valid` fails loudly.
float32 slip_ratio

# Encoder-implied forward speed, m/s. Contaminated by slip on purpose: a
# spinning wheel still reports motion. This is the numerator's inflated term.
float32 v_wheel

# Wheel-INDEPENDENT forward speed, m/s. Must not fuse wheel encoders, or the
# ratio becomes circular (section 1.3). See `source`.
float32 v_actual

# False -> discard slip_ratio entirely. Set when wheel speed is below the
# estimator's floor (a stationary rover has no defined slip) or when an input
# is stale. Independent of `quality`: this is "was lambda computable at all".
bool valid

# Confidence in v_actual, 0.0 (useless) .. 1.0 (fully trusted). Derived from
# the actual-velocity source's covariance, overridden by a VIO status topic
# when one is available. Independent of `valid`: a low-quality reading is
# still usable for the relative comparison of section 1.3, so the CONSUMER
# picks the threshold rather than the estimator silently dropping data.
float32 quality

# Which producer supplied v_actual. Published so a consumer can enforce
# section 1.3 itself: SOURCE_EKF fuses wheel encoders, which makes the slip
# ratio circular. That failure is invisible at runtime -- the arithmetic still
# succeeds and the value still looks plausible -- so it has to be typed.
uint8 source

uint8 SOURCE_UNKNOWN=0
uint8 SOURCE_SIM_GROUND_TRUTH=1
uint8 SOURCE_VIO=2
uint8 SOURCE_EKF=3
