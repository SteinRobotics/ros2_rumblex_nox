# Repository Guidelines

## Project Structure & Module Organization

This repository contains only Nox. ROS packages use the `nox_` prefix.
Keep package-owned parameters under `config/nox/`; launch files target this robot directly.
Core code, hardware drivers, simulation, CAD, documentation and tests are maintained independently.

## Build, Test, and Development Commands

Follow [resource-limited builds and tests](nox_doc/BUILD_AND_TEST.md) before
running builds, tests, simulations, or CAD workloads. It documents separate amd64
and Raspberry Pi 5 budgets, user-systemd access from Codex, and recovery after
interruptions. Run heavy jobs sequentially across sessions and verify limits.

For the approximately 30 GiB amd64 host, start with MemoryHigh=6G, MemoryMax=8G,
MemorySwapMax=1G and a five-minute timeout. On Pi 5, use the guide's RAM-relative
budget and one compiler worker. Keep memory-pressure protection enabled.

Use `--executor sequential` with colcon and set **both** `MAKEFLAGS="-j2 -l2"`
and `CMAKE_BUILD_PARALLEL_LEVEL=2` (use 1 for both on Pi or recovery batches).
This colcon version otherwise adds CPU-count-based Make parallelism, overriding
the intended CMake worker limit. Run tests with one worker as well.

If the sandbox cannot connect to the systemd user bus, request tool escalation
for the bounded `systemd-run --user --scope ...` command; do not silently run
without limits. If access is rejected or limits cannot be verified, report the
blocker. Inspect surviving processes and logs before retrying interrupted jobs;
never automatically restart the full workload or raise limits after an OOM/timeout.

Use package launch files for local checks, for example `ros2 launch nox_movement movement_launch.py` or `ros2 launch nox_gazebo simulation_gazebo.launch.py`.

## Coding Style & Naming Conventions

C++ uses the repository `.clang-format` (Google-derived, four-space indentation, 110-column limit); format changed C++ files before submitting. Prefer references over raw pointers and use `std::unique_ptr` or `std::shared_ptr` when ownership requires pointers. Follow existing C++23 conventions. Python uses four spaces, `snake_case` modules/functions, and ROS node names consistent with their package. Keep ROS package and interface names lowercase with underscores.

## Testing Guidelines

C++ tests use `ament_cmake_gtest`/GMock and live in each package's `test/` directory, typically named `test_<component>.cpp`. Add or update focused tests with behavior changes; no repository-wide coverage threshold is currently documented.

## Commit & Pull Request Guidelines

Recent commits use short, imperative, lowercase summaries such as `add servo interface board` and `move cad files to nox_description`. Keep commits focused and use the same style. Pull requests should explain the behavior or hardware change, identify affected packages, include test/build commands and results, and attach screenshots or logs for visualization, UI, or hardware-facing changes. Call out required ROS dependencies and configuration changes explicitly.
