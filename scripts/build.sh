#!/usr/bin/env bash
# Build from the robot's colcon workspace, with a shared resource budget.
set -eo pipefail
repo=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)
workspace=$(cd "$repo/../.." && pwd -P)
packages=()
for package in "$@"; do
    [[ $package =~ ^[a-z][a-z0-9_]*$ && -f "$repo/$package/package.xml" ]] || {
        echo "Unknown local package: $package" >&2; exit 2;
    }
    packages+=("$package")
done
selection=()
if (( ${#packages[@]} )); then selection=(--packages-up-to "${packages[@]}"); fi
source "$repo/scripts/environment.sh"
cd "$workspace"
workers=2
memory_high=6G
memory_max=8G
memory_swap=1G
if [[ $(uname -m) == aarch64 ]]; then
    workers=1
    memory_high=40%
    memory_max=50%
    memory_swap=512M
fi
if pgrep -x 'cc1plus|colcon|ninja|ctest|pytest|FreeCAD|gz' >/dev/null; then
    echo 'Another build/test/simulation process is active. Inspect it before starting this build.' >&2
    exit 1
fi
export MAKEFLAGS="-j$workers -l$workers" CMAKE_BUILD_PARALLEL_LEVEL="$workers" CTEST_PARALLEL_LEVEL=1
flock --nonblock "/tmp/rumblex-heavy-$(id -u).lock" \
  systemd-run --user --scope -p "MemoryHigh=$memory_high" -p "MemoryMax=$memory_max" \
    -p "MemorySwapMax=$memory_swap" \
  timeout --kill-after=10s 300s bash -c '
    cg=$(sed -n "s/^0:://p" /proc/self/cgroup)
    for key in memory.high memory.max memory.swap.max; do
      value=$(cat "/sys/fs/cgroup$cg/$key") || exit 1
      [[ $value =~ ^[0-9]+$ ]] || exit 1
    done
    exec "$@"
  ' bash python -m colcon build --symlink-install --executor sequential "${selection[@]}" \
    --cmake-args -DPython3_EXECUTABLE="$(command -v python)" -DPYTHON_EXECUTABLE="$(command -v python)"
