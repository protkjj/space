#!/usr/bin/env python3
"""
Publish S_small and S_medium from one terrain record.

Subscribes ``/terrain/estimate`` and publishes
``space_msgs/TraversabilityScore`` on ``/traversability/small`` and
``/traversability/medium``. Both come from the same
:func:`space_mission.traversability_transform.evaluate` call with a different
``RoverSpec`` -- never from scaling one into the other, which would be physically
wrong: lambda is a terrain x rover interaction, so the sand that slips our 2.7 kg
rover behaves differently under a medium rover's contact pressure, wheel
diameter, mass, and grousers.

Each published score carries the spec it was computed under, inline. When
``rover_spec.provenance`` is ``PROVENANCE_ASSUMED`` -- which it always is for the
medium rover, whose numbers are invented -- every cell is provisional, and that
field is how a consumer finds which maps to recompute once real numbers arrive.

The node deliberately does no accumulation. ``terrain_map_node`` owns the
canonical record; this one is a pure function of it, so restarting it loses
nothing and changing the scoring weights costs one republish rather than a
re-survey.
"""

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from space_mission import traversability_transform as transform
from space_mission.rover_spec import load_rover_spec, spec_to_msg
from space_msgs.msg import TerrainEstimate, TraversabilityScore


ROVERS = ('small', 'medium')


class TraversabilityTransformNode(Node):
    """Derive one traversability map per rover from the terrain record."""

    def __init__(self):
        super().__init__('traversability_transform')
        self.declare_parameter('terrain_topic', '/terrain/estimate')
        self.declare_parameter('output_prefix', '/traversability')
        for name, value in (
            ('composition_mode', 'weighted_sum'),
            ('weight_slope', 0.30),
            ('weight_roughness', 0.15),
            ('weight_step', 0.25),
            ('weight_soil', 0.30),
            ('min_slip_quality', 0.3),
            ('min_soil_confidence', 0.0),
        ):
            self.declare_parameter(name, value)

        self._config = transform.ScoringConfig(
            composition_mode=str(self.get_parameter('composition_mode').value),
            weight_slope=float(self.get_parameter('weight_slope').value),
            weight_roughness=float(
                self.get_parameter('weight_roughness').value),
            weight_step=float(self.get_parameter('weight_step').value),
            weight_soil=float(self.get_parameter('weight_soil').value),
        )
        self._gate = transform.ObservationGate(
            min_slip_quality=float(self.get_parameter('min_slip_quality').value),
            min_soil_confidence=float(
                self.get_parameter('min_soil_confidence').value),
        )
        self._specs = self._load_specs()

        prefix = str(self.get_parameter('output_prefix').value)
        self._pubs = {
            rover: self.create_publisher(
                TraversabilityScore, f'{prefix}/{rover}', 1)
            for rover in ROVERS
        }
        self.create_subscription(
            TerrainEstimate, str(self.get_parameter('terrain_topic').value),
            self._on_terrain,
            QoSProfile(reliability=ReliabilityPolicy.BEST_EFFORT,
                       history=HistoryPolicy.KEEP_LAST, depth=1),
        )
        assumed = [r for r, s in self._specs.items()
                   if s.provenance == 'assumed']
        self.get_logger().info(
            f'Traversability transform ready for {list(self._specs)} '
            f'-> {prefix}/{{{",".join(ROVERS)}}}'
        )
        if assumed:
            self.get_logger().warn(
                f'specs for {assumed} are ASSUMED, not measured; every score '
                'derived from them is provisional and must be recomputed when '
                'real numbers land (docs/pending.md V8)'
            )

    def _load_specs(self):
        """
        Load one spec per rover from this node's own parameters.

        Declared per rover under ``rover_specs.<id>.<field>`` so the YAML files
        stay separate: the two rovers' parameters must not be editable into each
        other by accident.
        """
        specs = {}
        for rover in ROVERS:
            params = {}
            for field in (
                'rover_id', 'mass_kg', 'wheel_radius_m', 'wheel_width_m',
                'ground_pressure_kpa', 'max_climb_angle_rad',
                'min_passable_width_m', 'ground_clearance_m', 'has_grousers',
                'provenance', 'provenance_note',
            ):
                name = f'rover_specs.{rover}.{field}'
                if not self.has_parameter(name):
                    self.declare_parameter(name, _placeholder(field))
                value = self.get_parameter(name).value
                if value is not None and value != '':
                    params[field] = value
            try:
                specs[rover] = load_rover_spec(params)
            except (KeyError, ValueError) as error:
                raise RuntimeError(
                    f'rover spec "{rover}" is unusable: {error}. Load '
                    'space_mission/config/rover_spec_{small,medium}.yaml.'
                ) from error
        return specs

    def _on_terrain(self, message: TerrainEstimate) -> None:
        try:
            terrain = _to_terrain_grid(message)
        except ValueError as error:
            self.get_logger().warn(f'unusable terrain record: {error}')
            return

        for rover, spec in self._specs.items():
            result = transform.evaluate(terrain, spec, self._config, self._gate)
            score = TraversabilityScore()
            score.header = message.header
            score.rover_id = rover
            score.rover_spec = spec_to_msg(spec)
            score.terrain_stamp = message.header.stamp
            score.soil_model_id = message.soil_model_id
            score.soil_model_version = message.soil_model_version
            score.evaluator_version = transform.EVALUATOR_VERSION
            score.grid = _score_grid(message.grid, result)
            self._pubs[rover].publish(score)


def _placeholder(field):
    """Return a typed placeholder so declare_parameter knows the type."""
    if field in ('rover_id', 'provenance', 'provenance_note'):
        return ''
    if field == 'has_grousers':
        return False
    return 0.0


def _layer_array(grid, name):
    """Return a layer as a 2-D (y, x) array, undoing the GridMap ordering."""
    import numpy as np

    try:
        index = list(grid.layers).index(name)
    except ValueError as error:
        raise ValueError(f'layer "{name}" missing') from error
    raw = np.asarray(grid.data[index].data, dtype=float)
    nx = int(round(grid.info.length_x / grid.info.resolution))
    ny = int(round(grid.info.length_y / grid.info.resolution))
    if raw.size != nx * ny:
        raise ValueError(
            f'layer "{name}" has {raw.size} values, expected {nx * ny}')
    return raw.reshape(nx, ny).T[::-1, ::-1]


def _to_terrain_grid(message):
    """Convert TerrainEstimate into the ROS-free view evaluate() takes."""
    grid = message.grid
    return transform.TerrainGrid(
        resolution_m=float(grid.info.resolution),
        slope_rad=_layer_array(grid, TerrainEstimate.LAYER_SLOPE),
        roughness_m=_layer_array(grid, TerrainEstimate.LAYER_ROUGHNESS),
        step_height_m=_layer_array(grid, TerrainEstimate.LAYER_STEP),
        slip_small=_layer_array(grid, TerrainEstimate.LAYER_SLIP_SMALL),
        slip_quality=_layer_array(grid, TerrainEstimate.LAYER_SLIP_QUALITY),
        slip_samples=_layer_array(grid, TerrainEstimate.LAYER_SLIP_SAMPLES),
        soil_difficulty=_layer_array(
            grid, TerrainEstimate.LAYER_SOIL_DIFFICULTY),
        soil_confidence=_layer_array(
            grid, TerrainEstimate.LAYER_SOIL_CONFIDENCE),
    )


def _score_grid(source, result):
    """Build the output GridMap, reusing the input's geometry exactly."""
    import numpy as np
    from grid_map_msgs.msg import GridMap
    from std_msgs.msg import Float32MultiArray, MultiArrayDimension

    grid = GridMap()
    grid.header = source.header
    grid.info = source.info
    grid.layers = [TraversabilityScore.LAYER_SCORE,
                   TraversabilityScore.LAYER_LIMITING_FACTOR]
    grid.basic_layers = [TraversabilityScore.LAYER_SCORE]

    nx = int(round(source.info.length_x / source.info.resolution))
    ny = int(round(source.info.length_y / source.info.resolution))
    for values in (result.score, result.limiting_factor):
        message = Float32MultiArray()
        message.layout.dim = [
            MultiArrayDimension(label='column_index', size=nx, stride=nx * ny),
            MultiArrayDimension(label='row_index', size=ny, stride=ny),
        ]
        message.data = np.asarray(
            np.asarray(values, dtype=float)[::-1, ::-1].T, dtype=np.float32
        ).ravel().tolist()
        grid.data.append(message)
    return grid


def main(args=None):
    """Run the traversability transform node."""
    rclpy.init(args=args)
    node = TraversabilityTransformNode()
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
