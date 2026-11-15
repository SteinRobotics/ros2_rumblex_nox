"""Launch RViz visualization with movement pipeline and teleop_twist_keyboard for cmd_vel input."""

import os
import re
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    OpaqueFunction,
    TimerAction,
)
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
import xacro

_SNAP_GUI_OVERRIDES = {
    k: ""
    for k in (
        "GTK_PATH",
        "GTK_EXE_PREFIX",
        "GTK_IM_MODULE_FILE",
        "GIO_MODULE_DIR",
        "GSETTINGS_SCHEMA_DIR",
    )
    if k in os.environ
}


def _launch_robot(context):
    robot = "nox"
    pkg_description = get_package_share_directory("nox_description")
    xacro_file = os.path.join(pkg_description, "urdf", f"{robot}.urdf.xacro")
    if not os.path.isfile(xacro_file):
        raise RuntimeError(f"Robot profile {robot!r} has no model: {xacro_file}")
    robot_description = xacro.process_file(
        xacro_file, mappings={"use_sim": "false"}
    ).toxml()
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description": robot_description}],
    )
    joint_state_publisher = Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
        parameters=[{"source_list": ["target_joint_states"]}],
    )
    pkg_movement = get_package_share_directory("nox_movement")
    movement_config_dir = os.path.join(pkg_movement, "config", robot)
    movement_node = Node(
        package="nox_movement",
        name="node_movement",
        executable="node_movement",
        output="screen",
        parameters=[
            os.path.join(
                get_package_share_directory("nox_description"),
                "config",
                robot,
                "anatomy.yaml",
            ),
            os.path.join(movement_config_dir, "servo_description.yaml"),
            {"servo.offline": True},
        ],
        remappings=[("joint_states", "target_joint_states")],
    )
    pkg_brain = get_package_share_directory("nox_brain")
    brain_config = os.path.join(pkg_brain, "config", robot, "parameter.yaml")
    brain_node = Node(
        package="nox_brain",
        name="node_brain",
        executable="node_brain",
        output="screen",
        parameters=[
            os.path.join(
                get_package_share_directory("nox_description"),
                "config",
                robot,
                "anatomy.yaml",
            ),
            os.path.join(pkg_brain, "config", robot, "gait.yaml"),
            brain_config,
        ],
    )
    communication_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare("nox_communication"),
                    "launch",
                    "communication_launch.py",
                ]
            )
        ),
        launch_arguments={}.items(),
    )
    enable_lidar = LaunchConfiguration("enable_lidar")
    lidar_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("nox_lidar_1d"), "launch", "lidar_launch.py"]
            )
        ),
        launch_arguments={}.items(),
        condition=IfCondition(enable_lidar),
    )
    rviz_config = os.path.join(pkg_description, "rviz", "model.rviz")
    rviz = Node(
        package="rviz2",
        executable="rviz2",
        arguments=["-d", rviz_config],
        additional_env={
            **_SNAP_GUI_OVERRIDES,
            "QT_QPA_PLATFORM": "xcb",
            "QT_ENABLE_HIGHDPI_SCALING": "0",
            "QT_AUTO_SCREEN_SCALE_FACTOR": "0",
            "QT_SCALE_FACTOR": "1",
            "QT_SCREEN_SCALE_FACTORS": "1",
        },
    )
    teleop = Node(
        package="teleop_twist_keyboard",
        executable="teleop_twist_keyboard",
        prefix="xterm -e",
        output="screen",
    )
    delayed_nodes = TimerAction(period=1.0, actions=[movement_node, brain_node, teleop])
    return [
        robot_state_publisher,
        joint_state_publisher,
        communication_launch,
        lidar_launch,
        rviz,
        delayed_nodes,
    ]


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "enable_lidar",
                default_value="false",
                description="Start the selected robot lidar driver for RViz.",
            ),
            OpaqueFunction(function=_launch_robot),
        ]
    )
