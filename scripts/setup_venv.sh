#!/usr/bin/env bash
# Create this workspace's own ROS-compatible Python environment.
set -eo pipefail
unset PYTHONPATH AMENT_PREFIX_PATH CMAKE_PREFIX_PATH COLCON_PREFIX_PATH LD_LIBRARY_PATH ROS_PACKAGE_PATH
export PYTHONNOUSERSITE=1
mode=${1:---development}
case "$mode" in
    --development) requirements=test.txt ;;
    --runtime-only) requirements=runtime.txt ;;
    *) echo "Usage: $0 [--development|--runtime-only]" >&2; exit 2 ;;
esac
[[ $# -le 1 ]] || { echo "Too many arguments" >&2; exit 2; }
repo=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)
workspace=$(cd "$repo/../.." && pwd -P)
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
export MAKEFLAGS="-j$workers -l$workers" CMAKE_BUILD_PARALLEL_LEVEL="$workers"
flock --nonblock "/tmp/rumblex-heavy-$(id -u).lock" \
  systemd-run --user --scope -p "MemoryHigh=$memory_high" -p "MemoryMax=$memory_max" \
    -p "MemorySwapMax=$memory_swap" \
  timeout --kill-after=10s 300s bash -c '
    set -eo pipefail
    cg=$(sed -n "s/^0:://p" /proc/self/cgroup)
    for key in memory.high memory.max memory.swap.max; do
      value=$(cat "/sys/fs/cgroup$cg/$key") || exit 1
      [[ $value =~ ^[0-9]+$ ]] || exit 1
    done
    workspace=$1
    repo=$2
    requirements=$3
    /usr/bin/python3 -m venv --system-site-packages "$workspace/.venv"
    touch "$workspace/.venv/COLCON_IGNORE"
    "$workspace/.venv/bin/python" -m pip install --disable-pip-version-check \
      --prefer-binary -r "$repo/requirements/$requirements"
    "$workspace/.venv/bin/python" -m pip install --disable-pip-version-check \
      --no-deps "openwakeword==0.6.0"
  ' bash "$workspace" "$repo" "$requirements"
echo "Environment ready: $workspace/.venv"
echo "Activate it after sourcing /opt/ros/lyrical/setup.bash. CAD remains separate."
