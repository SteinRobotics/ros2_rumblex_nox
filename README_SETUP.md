# Nox setup

Use Ubuntu 26.04 and ROS 2 Lyrical on the robot and developer machine.
The repository lives at `~/Workspace/colcon_nox/src/ros2_rumblex_nox`.
Install the ROS base distribution on a headless Raspberry Pi 5, or the desktop
distribution on a development PC. Use the system Python version for ROS extensions.

## Raspberry Pi 5

Review `scripts/setup_raspberry_pi.sh`, then run it as the regular login user
from a fresh shell, without a robot argument:

```bash
cd ~/Workspace/colcon_nox/src/ros2_rumblex_nox
git submodule update --init --recursive
bash scripts/setup_raspberry_pi.sh
```

The script installs system dependencies, a workspace virtual environment, runtime
packages, device rules and a lingering systemd user service. It changes the Pi and
requires sudo. It is not a desktop setup command. Follow the resource limits in
[nox_doc/BUILD_AND_TEST.md](nox_doc/BUILD_AND_TEST.md) when building manually.

Provide private wake-word models and online speech credentials separately.
Optional speech environment settings belong in `~/.config/nox/speech.env`.
After reboot inspect `systemctl --user status autostart_ros2.service` and
`journalctl --user -u autostart_ros2.service -b`. The launcher targets this robot directly.

## Developer machine

Install ROS Lyrical desktop, colcon, rosdep, a C++23 compiler, CMake >=3.25,
`libmagicenum-dev`, and Python development/virtual-environment support.
Run `bash scripts/setup_venv.sh` from this repository to create
`~/Workspace/colcon_nox/.venv` with the runtime and test dependencies in `requirements/`.
Use `--runtime-only` on the robot when development tests are not needed.
The environments are independent; CAD retains its dedicated environment.
Use rosdep against this repository for ROS dependencies and use the robot-owned requirements files for Python dependencies. Keep private models, caches and credentials
outside version control. See [BUILD.md](BUILD.md) for build commands and sourcing.

Follow [README_LAUNCH.md](README_LAUNCH.md) for desktop and hardware entry points;
[the BOM](BOM_NOX.md) and [SENSORS.md](SENSORS.md) describe the actual hardware.

Activate the workspace with `source scripts/environment.sh`; it clears inherited
sibling workspace overlays before selecting this robot and its `.venv`.
