# space_mission

Mission-level ownership boundary for rover traversability products.

Current data flow:

```text
space_perception
  /terrain/elevation_points
  /terrain/features
  /terrain/traversability
           |
           v
space_mission/traversability_fusion_node
  /mission/traversability
           |
           v
space_navigation (Nav2 costmap)
```

The initial fusion stage forwards visual traversability while monitoring all
three perception inputs. Future stages add IMU/odometry state, measured
small-rover slip, and predicted medium-rover slip inside this package without
changing the Navigation interface.

The default `space_bringup` RViz view colors the `traversability` field from
red (`0.0`, difficult to traverse) to green (`1.0`, easy to traverse).
