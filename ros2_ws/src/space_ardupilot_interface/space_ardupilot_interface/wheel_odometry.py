#!/usr/bin/env python3
"""
Turn wheel-encoder counts into the odometry ArduPilot's EKF will accept.

The rover's encoders are wired to the RoboClaws rather than to the Pixhawk, so
ArduPilot cannot read them itself. This computes the `odom` to `base_link`
transform from counts and publishes it on `/ap/tf`, which AP_DDS feeds to
`AP_VisualOdom` and from there to EKF3. That is what lets the vehicle arm and
navigate indoors with no GPS.

The maths lives in :class:`WheelOdometry`, which takes counts and returns a
pose, with no ROS and no serial port in sight, so the parts that are easy to
get subtly wrong are cheap to test.

Constraints the publisher has to respect, each measured rather than assumed;
see ``firmware/ardupilot/README.md``:

* Stamps must be in ArduPilot's own time base, which it publishes on
  ``/ap/time``. A wall-clock stamp is a different epoch and lands outside the
  EKF's fusion horizon.
* Consecutive stamps must differ by at least 20 ms or the EKF discards the
  sample.
* The feed must not stop. Aiding ends after roughly five seconds without a
  fused sample.
* The reported position must not jump. The DDS path hardcodes the reset
  counter to zero, so a discontinuity cannot be announced and simply looks
  like impossible movement.
"""

from dataclasses import dataclass
import math
from typing import Optional


# Encoder counters are signed 32-bit and wrap. Deltas are taken modulo this.
COUNTER_MODULUS = 1 << 32
COUNTER_HALF = COUNTER_MODULUS // 2

NANOSECONDS_PER_SECOND = 1_000_000_000


def _positive(name: str, value: float) -> float:
    """Validate a finite, strictly positive quantity."""
    if not math.isfinite(value) or value <= 0.0:
        raise ValueError(f'{name} must be finite and greater than zero')
    return value


def wrapped_delta(previous: int, current: int) -> int:
    """
    Return current minus previous across a 32-bit wrap.

    Encoder counters roll over, and a naive subtraction turns one count of
    real motion into four billion counts of nonsense. Interpreting the
    difference as the shorter way around is correct as long as the rover
    cannot travel half the counter's range between two samples, which at
    6400 counts per revolution is several hundred metres.
    """
    delta = (current - previous) % COUNTER_MODULUS
    if delta >= COUNTER_HALF:
        delta -= COUNTER_MODULUS
    return delta


@dataclass(frozen=True)
class OdometrySample:
    """One integrated pose, in the odom frame."""

    x: float
    y: float
    yaw: float
    linear_velocity: float
    angular_velocity: float
    left_velocity: float
    right_velocity: float


class WheelOdometry:
    """
    Integrate skid-steer wheel odometry from encoder counts.

    Both geometry values are measured from the built rover rather than taken
    from CAD, because the radius scales every distance and the track width
    scales every turn.
    """

    def __init__(
        self,
        *,
        wheel_radius_m: float,
        track_width_m: float,
        counts_per_revolution: float,
        max_wheel_speed_mps: float = 1.0,
    ):
        self.wheel_radius_m = _positive('wheel_radius_m', wheel_radius_m)
        self.track_width_m = _positive('track_width_m', track_width_m)
        self.counts_per_revolution = _positive(
            'counts_per_revolution', counts_per_revolution
        )
        self.max_wheel_speed_mps = _positive(
            'max_wheel_speed_mps', max_wheel_speed_mps
        )
        self.metres_per_count = (
            2.0 * math.pi * self.wheel_radius_m / self.counts_per_revolution
        )

        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0
        self._last_counts: Optional[tuple] = None
        self._last_time_ns: Optional[int] = None
        self.rejected_samples = 0

    def reset(self) -> None:
        """Forget the pose and the previous counts, keeping the geometry."""
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0
        self._last_counts = None
        self._last_time_ns = None

    def update(
        self, left_counts: int, right_counts: int, now_ns: int
    ) -> Optional[OdometrySample]:
        """
        Fold one encoder reading into the pose.

        Returns None for the first reading, which establishes a baseline, and
        for any reading that cannot be trusted. Rejecting a sample is safer
        than integrating a bad one: a rejected sample leaves the estimate
        briefly stale, while a bad one corrupts it permanently, and the DDS
        path has no way to announce a correction.
        """
        if self._last_counts is None or self._last_time_ns is None:
            self._last_counts = (left_counts, right_counts)
            self._last_time_ns = now_ns
            return None

        dt = (now_ns - self._last_time_ns) / NANOSECONDS_PER_SECOND
        if dt <= 0.0:
            # Time did not advance, or went backwards on a clock change.
            # Re-baseline rather than dividing by it.
            self._last_counts = (left_counts, right_counts)
            self._last_time_ns = now_ns
            self.rejected_samples += 1
            return None

        left_delta = wrapped_delta(self._last_counts[0], left_counts)
        right_delta = wrapped_delta(self._last_counts[1], right_counts)

        left_velocity = left_delta * self.metres_per_count / dt
        right_velocity = right_delta * self.metres_per_count / dt

        # A reading faster than the drivetrain can physically turn is a
        # dropped or corrupted packet, not motion. Integrating it would put
        # the rover somewhere it has never been.
        if (abs(left_velocity) > self.max_wheel_speed_mps
                or abs(right_velocity) > self.max_wheel_speed_mps):
            self._last_counts = (left_counts, right_counts)
            self._last_time_ns = now_ns
            self.rejected_samples += 1
            return None

        linear = 0.5 * (left_velocity + right_velocity)
        angular = (right_velocity - left_velocity) / self.track_width_m

        # Integrate over the midpoint heading. Straight integration at the
        # start heading walks the rover off the outside of every turn.
        mid_yaw = self.yaw + 0.5 * angular * dt
        self.x += linear * math.cos(mid_yaw) * dt
        self.y += linear * math.sin(mid_yaw) * dt
        self.yaw = _wrap_angle(self.yaw + angular * dt)

        self._last_counts = (left_counts, right_counts)
        self._last_time_ns = now_ns

        return OdometrySample(
            x=self.x,
            y=self.y,
            yaw=self.yaw,
            linear_velocity=linear,
            angular_velocity=angular,
            left_velocity=left_velocity,
            right_velocity=right_velocity,
        )


def _wrap_angle(angle: float) -> float:
    """Return the angle wrapped into [-pi, pi)."""
    return (angle + math.pi) % (2.0 * math.pi) - math.pi


def slip_ratio(wheel_velocity: float, body_velocity: float) -> Optional[float]:
    """
    Return the slip ratio for one side, or None when it is undefined.

    Slip is (wheel speed - true speed) / wheel speed. With the wheel stopped
    the ratio has no meaning rather than being zero, so this says so instead
    of returning a number that reads as "no slip".
    """
    if not math.isfinite(wheel_velocity) or not math.isfinite(body_velocity):
        return None
    if abs(wheel_velocity) < 1e-6:
        return None
    return (wheel_velocity - body_velocity) / wheel_velocity
