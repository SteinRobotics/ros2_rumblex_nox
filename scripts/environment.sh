# Source this file to select only this robot's ROS overlay and Python environment.
robot_env_repo=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)
robot_env_workspace=$(cd "$robot_env_repo/../.." && pwd -P)
robot_env_parent=$(dirname "$robot_env_workspace")
if declare -F deactivate >/dev/null; then deactivate; fi
unset AMENT_PREFIX_PATH CMAKE_PREFIX_PATH COLCON_PREFIX_PATH PYTHONPATH LD_LIBRARY_PATH ROS_PACKAGE_PATH
unset VIRTUAL_ENV VIRTUAL_ENV_PROMPT
export PYTHONNOUSERSITE=1
# Remove inherited executable paths from sibling colcon workspaces too.
robot_env_clean_path=()
IFS=: read -r -a robot_env_paths <<< "$PATH"
for robot_env_path in "${robot_env_paths[@]}"; do
    case "$robot_env_path" in "$robot_env_parent"/colcon_*/*) ;; *) robot_env_clean_path+=("$robot_env_path") ;; esac
done
PATH=$(IFS=:; echo "${robot_env_clean_path[*]}")
export PATH
source /opt/ros/lyrical/setup.bash
if [[ -f "$robot_env_workspace/.venv/bin/activate" ]]; then
    source "$robot_env_workspace/.venv/bin/activate"
fi
if [[ -f "$robot_env_workspace/install/local_setup.bash" ]]; then
    source "$robot_env_workspace/install/local_setup.bash"
fi
if [[ -d "$robot_env_workspace/vendor/install" ]]; then
    export CMAKE_PREFIX_PATH="$robot_env_workspace/vendor/install:${CMAKE_PREFIX_PATH:-}"
fi
unset robot_env_repo robot_env_workspace robot_env_parent robot_env_clean_path robot_env_paths robot_env_path
