# Nox launch commands

Source ROS and this workspace as described in [BUILD.md](BUILD.md).
All commands select Nox automatically. Run only one complete stack at a time.
Use verified resource limits for simulation and tests.

```bash
# Hardware (navigation is opt-in)
ros2 launch nox_bringup target_launch.py
ros2 launch nox_bringup target_launch.py enable_navigation:=true
# Offline desktop stack; no servo connection
ros2 launch nox_bringup test_launch.py
# Gazebo mesh stack
ros2 launch nox_bringup test_gazebo_launch.py
# Model inspection
ros2 launch nox_description display.launch.py
ros2 launch nox_description display_mesh.launch.py
# Individual components
ros2 launch nox_movement movement_offline_launch.py
ros2 launch nox_communication communication_launch.py
```

Use `--show-args` on an entry point for its supported options. Hardware launches leave
speech listening disabled unless `autostart_listening:=true` is requested.

Head sweeping is enabled with navigation. Use `sensors_launch.py enable_head_scan:=true` only with the movement stack and head feedback available.
