"""Launch Gazebo Harmonic simulation of a RumbleX robot with ros2_control."""

import os
import re
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    OpaqueFunction,
    RegisterEventHandler,
    TimerAction,
)
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
import xacro
import yaml


def _launch_robot(context):
    robot = "nox"
    pkg_description = get_package_share_directory("nox_description")
    pkg_gazebo = get_package_share_directory("nox_gazebo")
    xacro_file = os.path.join(pkg_description, "urdf", f"{robot}.urdf.xacro")
    if not os.path.isfile(xacro_file):
        raise RuntimeError(f"Robot profile {robot!r} has no model: {xacro_file}")
    robot_description = xacro.process_file(
        xacro_file, mappings={"use_sim": "true"}
    ).toxml()
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("ros_gz_sim"), "launch", "gz_sim.launch.py"]
            )
        ),
        launch_arguments={"gz_args": ["-r ", LaunchConfiguration("world")]}.items(),
    )
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description": robot_description, "use_sim_time": True}],
    )
    spawn_entity = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-topic",
            "robot_description",
            "-name",
            robot,
            "-x",
            LaunchConfiguration("spawn_x"),
            "-y",
            LaunchConfiguration("spawn_y"),
            "-Y",
            LaunchConfiguration("spawn_yaw"),
            "-z",
            "0.07",
        ],
        output="screen",
    )
    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"],
    )
    forward_position_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "forward_position_controller",
            "--param-file",
            os.path.join(pkg_gazebo, "config", robot, "joint_controllers.yaml"),
        ],
    )
    activate_joint_state_broadcaster = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawn_entity, on_exit=[joint_state_broadcaster_spawner]
        )
    )
    activate_position_controller = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[forward_position_controller_spawner],
        )
    )
    gz_ros_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
            "/lidar_scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan",
            "/imu/data@sensor_msgs/msg/Imu[gz.msgs.IMU",
        ],
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
            {"servo.offline": True, "use_sim_time": True},
        ],
        remappings=[("joint_states", "target_joint_states")],
    )
    controllers_yaml = os.path.join(
        pkg_gazebo, "config", robot, "joint_controllers.yaml"
    )
    with open(controllers_yaml) as f:
        controllers_config = yaml.safe_load(f)
    joint_names = controllers_config["forward_position_controller"]["ros__parameters"][
        "joints"
    ]
    joint_state_bridge = Node(
        package="nox_gazebo",
        executable="joint_state_bridge.py",
        name="joint_state_bridge",
        output="screen",
        parameters=[{"joint_names": joint_names, "use_sim_time": True}],
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
            {"use_sim_time": True},
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
    delayed_nodes = TimerAction(
        period=3.0, actions=[movement_node, joint_state_bridge, brain_node]
    )
    perception_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare("nox_perception_lidar"),
                    "launch",
                    "perception_launch.py",
                ]
            )
        ),
        launch_arguments={}.items(),
        condition=IfCondition(LaunchConfiguration("enable_navigation")),
    )
    navigation_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("nox_navigation"), "launch", "navigation_launch.py"]
            )
        ),
        launch_arguments={"enable_map": "true"}.items(),
        condition=IfCondition(LaunchConfiguration("enable_navigation")),
    )
    return [
        gazebo,
        robot_state_publisher,
        spawn_entity,
        activate_joint_state_broadcaster,
        activate_position_controller,
        gz_ros_bridge,
        communication_launch,
        delayed_nodes,
        *[perception_launch],
        navigation_launch,
    ]


def generate_launch_description():
    world_file = os.path.join(
        get_package_share_directory("nox_gazebo"), "worlds", "empty.sdf"
    )
    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "world",
                default_value=world_file,
                description="Full path to the Gazebo world SDF file",
            ),
            DeclareLaunchArgument(
                "enable_navigation",
                default_value="false",
                description="Launch nox_navigation (robot-specific perception + reactive nav)",
            ),
            DeclareLaunchArgument("spawn_x", default_value="-2.26"),
            DeclareLaunchArgument("spawn_y", default_value="-2.13"),
            DeclareLaunchArgument("spawn_yaw", default_value="0.0"),
            OpaqueFunction(function=_launch_robot),
        ]
    )
