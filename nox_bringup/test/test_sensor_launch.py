"""Check robot pipeline selection without starting hardware or the vendor driver."""

import importlib.util
from pathlib import Path
from unittest.mock import patch
import xml.etree.ElementTree as ET

import pytest
import yaml
from launch import LaunchContext
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.utilities import normalize_to_list_of_substitutions, perform_substitutions
from launch_ros.actions import Node
from launch_ros.utilities import evaluate_parameters

ROOT = Path(__file__).resolve().parents[2]


def evaluate(ctx, value):
    return perform_substitutions(ctx, normalize_to_list_of_substitutions(value))


def load(package, name):
    spec = importlib.util.spec_from_file_location(
        name, ROOT / package / "launch" / f"{name}.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def context(robot, driver="true", sweep="true", camera="false"):
    result = LaunchContext()
    result.launch_configurations.update(
        robot=robot,
        enable_driver=driver,
        enable_head_scan=sweep,
        enable_camera=camera,
        camera_device="/dev/v4l/by-id/test-meet-se",
        camera_params_file="",
        camera_info_url="",
    )
    return result


@pytest.mark.parametrize("robot,package,count", [("nox", "nox_lidar_1d", 2)])
def test_selected_pipeline(robot, package, count):
    module = load("nox_bringup", "sensors_launch")
    with patch.object(
        module, "get_package_share_directory", side_effect=lambda name: str(ROOT / name)
    ):
        ctx = context(robot)
        actions = module._launch_sensors(ctx)
        assert len(actions) == count
        assert all(isinstance(action, IncludeLaunchDescription) for action in actions)
        actions[0].launch_description_source.get_launch_description(ctx)
        assert package in actions[0].launch_description_source.location
        assert actions[0].condition.evaluate(ctx)
        assert not actions[0].condition.evaluate(context(robot, driver="false"))
        if robot == "nox":
            actions[1].launch_description_source.get_launch_description(ctx)
            assert (
                "nox_perception_lidar" in actions[1].launch_description_source.location
            )
            assert actions[1].condition.evaluate(ctx)
            assert not actions[1].condition.evaluate(context(robot, sweep="false"))


@pytest.mark.parametrize("robot", ["nox"])
def test_hardware_bringup_publishes_imu_mount_without_navigation(robot):
    description = load("nox_bringup", "target_launch").generate_launch_description()
    ctx = context(robot)
    ctx.launch_configurations["enable_navigation"] = "false"
    publishers = [
        action
        for action in description.entities
        if isinstance(action, Node)
        and evaluate(ctx, action.node_package) == "robot_state_publisher"
    ]
    assert len(publishers) == 1
    publisher = publishers[0]
    assert publisher.condition is None
    parameters = evaluate_parameters(ctx, publisher._Node__parameters)
    model = ET.fromstring(parameters[0]["robot_description"])
    assert model.get("name") == robot
    joint = model.find("joint[@name='imu_joint']")
    assert joint is not None
    assert joint.get("type") == "fixed"
    assert joint.find("parent").get("link") == "base_link"
    assert joint.find("child").get("link") == "imu_link"
    assert model.find("ros2_control") is None


def test_navigation_has_no_sensor_or_head_controller():
    module = load("nox_navigation", "navigation_launch")
    with patch.object(
        module, "get_package_share_directory", side_effect=lambda name: str(ROOT / name)
    ):
        nodes = [
            action
            for action in module.generate_launch_description().entities
            if isinstance(action, Node)
        ]
        assert all("head_scan" not in str(node.node_executable) for node in nodes)
        assert all("lidar" not in str(node.node_package) for node in nodes)
    for robot in ["nox"]:
        config = yaml.safe_load(
            (ROOT / "nox_navigation" / "config" / robot / "navigation.yaml").read_text()
        )
        assert set(config) == {"node_navigation"}
