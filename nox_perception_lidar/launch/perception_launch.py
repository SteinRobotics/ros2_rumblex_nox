"""Launch the nox head-sweep processing using its robot-specific configuration."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "params_file",
                default_value=PathJoinSubstitution(
                    [
                        FindPackageShare("nox_perception_lidar"),
                        "config",
                        "nox",
                        "perception.yaml",
                    ]
                ),
            ),
            Node(
                package="nox_perception_lidar",
                executable="node_head_scan",
                name="node_head_scan",
                output="screen",
                parameters=[LaunchConfiguration("params_file")],
            ),
        ]
    )
