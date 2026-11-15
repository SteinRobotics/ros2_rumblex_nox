from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node


def generate_launch_description():
    robot = "nox"
    config_dir = [get_package_share_directory("nox_movement"), "config", robot]
    anatomy = PathJoinSubstitution(
        [
            get_package_share_directory("nox_description"),
            "config",
            robot,
            "anatomy.yaml",
        ]
    )
    servo_description = PathJoinSubstitution(config_dir + ["servo_description.yaml"])
    node = Node(
        package="nox_movement",
        name="node_movement",
        executable="node_movement",
        output="screen",
        parameters=[anatomy, servo_description],
    )
    return LaunchDescription([node])
