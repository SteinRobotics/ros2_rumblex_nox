# Nox sensors

Sensor composition is owned by `nox_bringup/launch/sensors_launch.py`.
The BNO055 mount and measurement frame are defined in the robot URDF and
`nox_bringup/config/nox/bno055_params.yaml`.

`nox_lidar_1d` drives the Garmin LIDAR-Lite and publishes `scan_1d`. `nox_perception_lidar` combines range readings and head position into `scan` for navigation. Enable head scanning only with movement and joint feedback. The Garmin library is a pinned submodule; see README.md for its publication prerequisite.

```bash
ros2 launch nox_bringup sensors_launch.py
ros2 launch nox_navigation navigation_launch.py
```

Navigation does not launch sensor drivers itself. Hardware bringup composes the
sensor pipeline and enables navigation only when requested. The offline map-wall
range simulator is a single-beam approximation, not a physical sensor validation.
