#!/usr/bin/env python3
"""
Accumulate the canonical terrain record on a fixed world-frame grid.

Why this node exists
--------------------
Until now there was no map. ``local_elevation_map_node`` keeps a 4 x 4 m grid
around the rover and drops cells after ``cell_timeout`` = 2 s, so
``/terrain/traversability`` is an instantaneous overlay: cells appear as the
camera sweeps over them and vanish two seconds later. Every arena map figure so
far was accumulated OFFLINE by a capture script; nothing in the running system
held it.

That matters beyond presentation. CLAUDE.md's dual-rover transform layer makes
the observation and estimation layers the CANONICAL record -- the thing stored
and handed to the follow-on medium rover, from which S_small and S_medium are
re-derived. A record with a two-second memory cannot serve that purpose, and
``slip_samples``/``soil_confidence`` are meaningless without it: "this cell was
crossed three times" needs somewhere to remember the first two.

What it publishes
-----------------
``space_msgs/TerrainEstimate`` on ``/terrain/estimate``: a
``grid_map_msgs/GridMap`` carrying the layer contract those message constants
define. Unobserved cells are NaN, which is distinct from a measured zero -- a
planner reads 0.0 as "passable, costly" and NaN as "unknown", and collapsing
them would route the rover cheaply into unsurveyed ground.

The grid extent is plain parameters, NOT read from arena CAD. Deriving it from a
mesh would work in this arena and nowhere else, and the mission environment has
no CAD at all.

Slip attribution
----------------
Slip arrives as one scalar for the whole rover, so it is credited to the cell the
rover is standing on, and only when ``SlipEstimate.valid`` is true and its
``quality`` clears ``min_slip_quality``. That gate runs HERE, before the soil
proxy, because a low-confidence lambda that reaches the estimation layer corrupts
it -- and both derived maps come from that layer, so one bad sample would break
S_small and S_medium together.

``source`` is checked too: ``SOURCE_EKF`` means the producer fused wheel
encoders, which makes the slip ratio circular (CLAUDE.md 1.3). Such samples are
counted and refused rather than silently averaged in.
"""

import math
import struct

from geometry_msgs.msg import Pose
from grid_map_msgs.msg import GridMap, GridMapInfo
from nav_msgs.msg import Odometry
import numpy as np
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import PointCloud2
from space_mission import soil_model
from space_msgs.msg import SlipEstimate, TerrainEstimate
from std_msgs.msg import Float32MultiArray, MultiArrayDimension


#: Feature-cloud fields consumed from ``/terrain/features``. Read by name from
#: the message's own field table rather than by fixed offset, so a producer that
#: adds a field does not silently shift what we read.
FEATURE_KEYS = ('x', 'y', 'slope', 'roughness', 'step_height', 'confidence')


class TerrainMapNode(Node):
    """Fold per-frame terrain features into a persistent world-frame grid."""

    def __init__(self):
        super().__init__('terrain_map')
        defaults = {
            'features_topic': '/terrain/features',
            'slip_topic': '/slip',
            'odom_topic': '/odom',
            'output_topic': '/terrain/estimate',
            'frame_id': 'odom',
            # Arena-sized default; override per world. Not taken from CAD --
            # see the module docstring.
            'min_x': -2.5,
            'max_x': 2.5,
            'min_y': -3.0,
            'max_y': 3.0,
            'resolution': 0.05,
            'publish_rate': 2.0,
            # Applied before the soil proxy, not after.
            'min_slip_quality': 0.3,
            'min_feature_confidence': 0.10,
        }
        for name, value in defaults.items():
            self.declare_parameter(name, value)

        self._frame = str(self.get_parameter('frame_id').value)
        self._res = float(self.get_parameter('resolution').value)
        self._min_x = float(self.get_parameter('min_x').value)
        self._min_y = float(self.get_parameter('min_y').value)
        span_x = float(self.get_parameter('max_x').value) - self._min_x
        span_y = float(self.get_parameter('max_y').value) - self._min_y
        if self._res <= 0.0 or span_x <= 0.0 or span_y <= 0.0:
            raise ValueError('resolution and extent must be positive')
        self._nx = int(round(span_x / self._res))
        self._ny = int(round(span_y / self._res))
        self._min_quality = float(self.get_parameter('min_slip_quality').value)
        self._min_confidence = float(
            self.get_parameter('min_feature_confidence').value
        )

        shape = (self._ny, self._nx)
        # Observation layers. NaN until observed.
        self._slope = np.full(shape, np.nan)
        self._roughness = np.full(shape, np.nan)
        self._step = np.full(shape, np.nan)
        # Running mean of geometry, so repeat views average instead of the last
        # frame overwriting everything before it.
        self._geometry_count = np.zeros(shape)
        # Slip layers, accumulated per cell as the rover drives over them.
        self._slip_sum = np.zeros(shape)
        self._slip_quality_sum = np.zeros(shape)
        self._slip_count = np.zeros(shape)

        self._pose = None
        self._refused_circular = 0
        self._warned_circular = False

        sensor_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST, depth=5,
        )
        self._pub = self.create_publisher(
            TerrainEstimate, self.get_parameter('output_topic').value, 1
        )
        self.create_subscription(
            PointCloud2, self.get_parameter('features_topic').value,
            self._on_features, sensor_qos,
        )
        self.create_subscription(
            SlipEstimate, self.get_parameter('slip_topic').value,
            self._on_slip, 10,
        )
        self.create_subscription(
            Odometry, self.get_parameter('odom_topic').value,
            self._on_odom, sensor_qos,
        )
        rate = float(self.get_parameter('publish_rate').value)
        if rate <= 0.0:
            raise ValueError('publish_rate must be positive')
        self.create_timer(1.0 / rate, self._publish)
        self.get_logger().info(
            f'Terrain map {self._nx}x{self._ny} at {self._res} m in '
            f'"{self._frame}", origin ({self._min_x:+.2f}, {self._min_y:+.2f}) '
            f'-> {self.get_parameter("output_topic").value}'
        )

    # --- inputs ----------------------------------------------------------
    def _on_odom(self, message: Odometry) -> None:
        p = message.pose.pose.position
        self._pose = (float(p.x), float(p.y))

    def _cell(self, x, y):
        """Return the grid index for a world point, or None if outside."""
        ix = int(math.floor((x - self._min_x) / self._res))
        iy = int(math.floor((y - self._min_y) / self._res))
        if 0 <= ix < self._nx and 0 <= iy < self._ny:
            return iy, ix
        return None

    def _on_features(self, message: PointCloud2) -> None:
        offsets = {field.name: field.offset for field in message.fields}
        missing = [key for key in FEATURE_KEYS if key not in offsets]
        if missing:
            self.get_logger().warn(
                f'feature cloud lacks {sorted(missing)}; ignoring frame'
            )
            return
        count = message.width * message.height
        if not count:
            return

        step = message.point_step
        data = message.data
        for index in range(count):
            base = index * step
            confidence = struct.unpack_from(
                '<f', data, base + offsets['confidence'])[0]
            if not math.isfinite(confidence) or confidence < self._min_confidence:
                continue
            x = struct.unpack_from('<f', data, base + offsets['x'])[0]
            y = struct.unpack_from('<f', data, base + offsets['y'])[0]
            cell = self._cell(x, y)
            if cell is None:
                continue
            slope = struct.unpack_from('<f', data, base + offsets['slope'])[0]
            rough = struct.unpack_from(
                '<f', data, base + offsets['roughness'])[0]
            stepv = struct.unpack_from(
                '<f', data, base + offsets['step_height'])[0]
            if not (math.isfinite(slope) and math.isfinite(rough)
                    and math.isfinite(stepv)):
                continue
            self._merge_geometry(cell, slope, rough, stepv)

    def _merge_geometry(self, cell, slope, roughness, step_height):
        """
        Fold one observation into a cell's running mean.

        A running mean rather than last-writer-wins: adjacent frames see the same
        surface through different noise, so averaging recovers signal. It also
        means a single bad frame cannot erase a well-observed cell.
        """
        n = self._geometry_count[cell]
        if n == 0:
            self._slope[cell] = slope
            self._roughness[cell] = roughness
            self._step[cell] = step_height
        else:
            weight = 1.0 / (n + 1.0)
            self._slope[cell] += (slope - self._slope[cell]) * weight
            self._roughness[cell] += (roughness - self._roughness[cell]) * weight
            # Step height is a MAXIMUM, not an average: a step seen once is a
            # step. Averaging it away would report a hazard as milder each time
            # the rover looked at flat ground beside it.
            self._step[cell] = max(self._step[cell], step_height)
        self._geometry_count[cell] = n + 1.0

    def _on_slip(self, message: SlipEstimate) -> None:
        if message.source == SlipEstimate.SOURCE_EKF:
            self._refused_circular += 1
            if not self._warned_circular:
                self._warned_circular = True
                self.get_logger().error(
                    'refusing slip with source=EKF: robot_localization fuses '
                    'wheel encoders, so the ratio is circular (CLAUDE.md 1.3)'
                )
            return
        if not message.valid or not math.isfinite(message.slip_ratio):
            return
        if not soil_model.accepts_sample(message.quality, self._min_quality):
            return
        if self._pose is None:
            return
        cell = self._cell(*self._pose)
        if cell is None:
            return
        self._slip_sum[cell] += float(message.slip_ratio)
        self._slip_quality_sum[cell] += float(message.quality)
        self._slip_count[cell] += 1.0

    # --- output ----------------------------------------------------------
    def _estimation_layers(self):
        """Return (soil_difficulty, soil_confidence) from the slip layers."""
        difficulty = np.full(self._slope.shape, np.nan)
        confidence = np.full(self._slope.shape, np.nan)
        observed = self._slip_count > 0
        if not observed.any():
            return difficulty, confidence

        mean_slip = np.divide(
            self._slip_sum, np.maximum(self._slip_count, 1.0),
            out=np.zeros_like(self._slip_sum), where=observed,
        )
        mean_quality = np.divide(
            self._slip_quality_sum, np.maximum(self._slip_count, 1.0),
            out=np.zeros_like(self._slip_quality_sum), where=observed,
        )
        # The soil proxy is scalar and cheap; only crossed cells need it, and
        # there are far fewer of those than grid cells.
        for iy, ix in zip(*np.nonzero(observed)):
            slope = self._slope[iy, ix]
            if not math.isfinite(slope):
                continue
            value = soil_model.estimate_soil_difficulty(
                float(mean_slip[iy, ix]), float(slope), self._spec()
            )
            if value is None:
                continue
            difficulty[iy, ix] = value
            confidence[iy, ix] = soil_model.estimate_soil_confidence(
                float(self._slip_count[iy, ix]),
                float(mean_quality[iy, ix]),
            )
        return difficulty, confidence

    def _spec(self):
        """
        Return the spec of the rover that DID the measuring.

        Loaded lazily and cached: the estimation layer removes our own rover's
        contribution from lambda, which is what makes the residue reusable for
        scoring a different rover.
        """
        if getattr(self, '_cached_spec', None) is None:
            from space_description.rover_geometry import load_geometry
            from space_mission.rover_spec import (
                PROVENANCE_MEASURED, RoverSpec,
            )
            geom = load_geometry()
            self._cached_spec = RoverSpec(
                rover_id='small',
                mass_kg=float(geom['mass_total']),
                wheel_radius_m=float(geom['wheel_radius']),
                wheel_width_m=float(geom['wheel_width']),
                ground_pressure_kpa=1.0,
                max_climb_angle_rad=0.349,
                min_passable_width_m=1.0,
                ground_clearance_m=float(geom['chassis_ground_clearance']),
                has_grousers=False,
                provenance=PROVENANCE_MEASURED,
            )
        return self._cached_spec

    def _layer(self, values):
        """Wrap a 2-D array as the row-major Float32MultiArray GridMap wants."""
        message = Float32MultiArray()
        message.layout.dim = [
            MultiArrayDimension(label='column_index', size=self._nx,
                                stride=self._nx * self._ny),
            MultiArrayDimension(label='row_index', size=self._ny,
                                stride=self._ny),
        ]
        # GridMap indexes from the top-left corner with x along rows, so the
        # array is transposed and flipped relative to the (y, x) grid held here.
        message.data = np.asarray(
            values[::-1, ::-1].T, dtype=np.float32
        ).ravel().tolist()
        return message

    def _publish(self) -> None:
        difficulty, confidence = self._estimation_layers()
        mean_slip = np.where(
            self._slip_count > 0,
            np.divide(self._slip_sum, np.maximum(self._slip_count, 1.0)),
            np.nan,
        )
        mean_quality = np.where(
            self._slip_count > 0,
            np.divide(self._slip_quality_sum, np.maximum(self._slip_count, 1.0)),
            np.nan,
        )
        samples = np.where(self._slip_count > 0, self._slip_count, np.nan)

        layers = {
            TerrainEstimate.LAYER_SLOPE: self._slope,
            TerrainEstimate.LAYER_ROUGHNESS: self._roughness,
            TerrainEstimate.LAYER_STEP: self._step,
            TerrainEstimate.LAYER_SLIP_SMALL: mean_slip,
            TerrainEstimate.LAYER_SLIP_QUALITY: mean_quality,
            TerrainEstimate.LAYER_SLIP_SAMPLES: samples,
            TerrainEstimate.LAYER_SOIL_DIFFICULTY: difficulty,
            TerrainEstimate.LAYER_SOIL_CONFIDENCE: confidence,
        }

        estimate = TerrainEstimate()
        estimate.header.stamp = self.get_clock().now().to_msg()
        estimate.header.frame_id = self._frame
        estimate.soil_model_id = soil_model.SOIL_MODEL_ID
        estimate.soil_model_version = soil_model.SOIL_MODEL_VERSION

        grid = GridMap()
        grid.header = estimate.header
        info = GridMapInfo()
        info.resolution = self._res
        info.length_x = self._nx * self._res
        info.length_y = self._ny * self._res
        pose = Pose()
        # GridMap's pose is the CENTRE of the grid.
        pose.position.x = self._min_x + info.length_x / 2.0
        pose.position.y = self._min_y + info.length_y / 2.0
        pose.orientation.w = 1.0
        info.pose = pose
        grid.info = info
        grid.layers = list(layers)
        grid.basic_layers = [TerrainEstimate.LAYER_SLOPE]
        grid.data = [self._layer(values) for values in layers.values()]
        estimate.grid = grid
        self._pub.publish(estimate)

    def observed_cells(self):
        """Return how many cells carry geometry, for diagnostics and tests."""
        return int((self._geometry_count > 0).sum())


def main(args=None):
    """Run the terrain map node."""
    rclpy.init(args=args)
    node = TerrainMapNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
