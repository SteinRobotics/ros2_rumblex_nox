"""Launch sensor-independent reactive navigation for a RumbleX hexapod."""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node


def generate_launch_description():
    pkg_nav = get_package_share_directory("nox_navigation")
    robot = "nox"
    config = PathJoinSubstitution([pkg_nav, "config", robot, "navigation.yaml"])
    anatomy = PathJoinSubstitution(
        [
            get_package_share_directory("nox_description"),
            "config",
            robot,
            "anatomy.yaml",
        ]
    )
    map_file = os.path.join(pkg_nav, "maps", "simple_room.yaml")
    enable_map_arg = DeclareLaunchArgument(
        "enable_map",
        default_value="false",
        description="Start map_server to publish the static occupancy grid",
    )
    navigation = Node(
        package="nox_navigation",
        executable="node_navigation",
        name="node_navigation",
        output="screen",
        parameters=[config],
    )
    map_server = Node(
        package="nav2_map_server",
        executable="map_server",
        name="map_server",
        output="screen",
        parameters=[{"yaml_filename": map_file, "use_sim_time": True}],
        condition=IfCondition(LaunchConfiguration("enable_map")),
    )
    lifecycle_manager = Node(
        package="nav2_lifecycle_manager",
        executable="lifecycle_manager",
        name="lifecycle_manager_map",
        output="screen",
        parameters=[
            {"autostart": True, "node_names": ["map_server"], "use_sim_time": True}
        ],
        condition=IfCondition(LaunchConfiguration("enable_map")),
    )
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "use_external_odometry",
                default_value="false",
                description="Use an existing odom publisher instead of the supporting-foot estimator",
            ),
            enable_map_arg,
            Node(
                package="nox_navigation",
                executable="offline_odometry.py",
                output="screen",
                parameters=[anatomy],
                condition=UnlessCondition(LaunchConfiguration("use_external_odometry")),
            ),
            navigation,
            map_server,
            lifecycle_manager,
        ]
    )
