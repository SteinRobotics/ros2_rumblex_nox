# Build and test Nox

## Terminal environment

From the repository, activate its environment without inheriting another workspace:

```bash
source scripts/environment.sh
cd ~/Workspace/colcon_nox
```

This selects `/opt/ros/lyrical`, this workspace's `.venv`, and its own installed
overlay. It removes inherited sibling workspace paths and disables user-site Python
packages. System packages remain visible for ROS ABI compatibility. Run
`bash scripts/setup_venv.sh` from the repository first to create the environment;
CAD dependencies stay in the dedicated CAD environment.

Do not reuse build/install directories from the original repository: package names changed.

## Resource limits

Follow [nox_doc/BUILD_AND_TEST.md](nox_doc/BUILD_AND_TEST.md) to define and verify
`nox_limited`. Check existing jobs first. On this amd64 host use MemoryHigh=6G,
MemoryMax=8G, MemorySwapMax=1G and a five-minute timeout, two compiler workers,
sequential packages and one test worker. On Pi use the guide's RAM-relative limits
and one worker. Run the two workspaces sequentially. After a timeout or memory failure,
inspect logs and resume only a smaller focused batch; never rerun the full workload automatically.

## Build

The editor tasks use `scripts/build.sh`, which applies the resource limits automatically.
Run `bash scripts/build.sh nox_movement` from this repository for a focused build
and its dependencies, or omit the package to build the workspace.

Install dependencies using rosdep and the setup/package documentation first.

```bash
export MAKEFLAGS='-j2 -l2'
export CMAKE_BUILD_PARALLEL_LEVEL=2
export CTEST_PARALLEL_LEVEL=1
nox_limited colcon build --symlink-install --executor sequential \
  --cmake-args -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
source install/local_setup.bash
```

For a focused build add `--packages-up-to nox_movement` (or another target).
Private speech resources and external hardware drivers require the setup described
in [README_SETUP.md](README_SETUP.md). Do not disable resource controls to complete a build.

## Tests

```bash
nox_limited colcon test --executor sequential --packages-select nox_movement \
  --event-handlers console_direct+ --ctest-args --output-on-failure -j1
colcon test-result --verbose
```

Run package tests appropriate to the change. CAD tests use a separate CAD environment
and bounded processes; they are not part of the ordinary software test run.
The section-parser Python script is a CTest harness requiring a compiled executable,
not a pytest collection target. See package CMakeLists.txt for its invocation.
