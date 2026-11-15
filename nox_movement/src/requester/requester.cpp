/*******************************************************************************
 * Copyright (c) 2021 Christian Stein
 ******************************************************************************/

#include "requester/requester.hpp"

#include <cmath>

#include "handler/leg_servo_conversion.hpp"
#include "handler/servo_controller.hpp"
#include "nox_utils/units.hpp"

using namespace nox_interfaces::msg;
using std::placeholders::_1;

namespace nox_movement {

CRequester::CRequester(std::shared_ptr<rclcpp::Node> node, std::shared_ptr<IServoController> servo_controller)
    : node_(node) {
    kinematics_ = std::make_shared<nox_geometry::CBodyModel>(node);
    if (servo_controller) {
        servo_controller_ = std::move(servo_controller);
    } else {
        servo_controller_ = std::make_shared<CServoController>(node);
    }

    servo_controller_->setInitialAnglesCallback(
        [this](const std::map<nox_geometry::ELegIndex, nox_geometry::CLegAngles>& initial_angles,
               const nox_geometry::COrientation& head) {
            RCLCPP_INFO_STREAM(node_->get_logger(),
                               "on Callback: initial servo angles received, setting kinematics.");
            kinematics_->setHeadOrientation(head);
            for (const auto& [leg_index, leg_angles] : initial_angles) {
                kinematics_->setLegAngles(leg_index, leg_angles);
            }
        });

    sub_body_pose_ = node_->create_subscription<BodyPose>("cmd_movement", rclcpp::QoS(1),
                                                          std::bind(&CRequester::onBodyPose, this, _1));
    pub_body_pose_ = node_->create_publisher<BodyPose>("body_pose_actual", rclcpp::QoS(1).transient_local());
    pub_body_pose_->publish(nox_geometry::bodyPose(*kinematics_));

    pub_joint_states_ = node_->create_publisher<sensor_msgs::msg::JointState>("joint_states", 10);
}

void CRequester::sendServoRequest(const double duration_s) {
    auto head = kinematics_->getHeadOrientation();
    auto legs = kinematics_->getLegAngles();
    servo_controller_->requestAngles(leg_servo_conversion::buildServoTargets(head, legs), duration_s);
}

void CRequester::publishJointStates(
    const std::map<nox_geometry::ELegIndex, nox_geometry::CLegAngles>& legs,
    const nox_geometry::COrientation& head) {
    sensor_msgs::msg::JointState msg;
    msg.header.stamp = node_->get_clock()->now();

    // Joint names must match the URDF joint names in nox_description
    static const std::vector<std::pair<nox_geometry::ELegIndex, std::string>> leg_order = {
        {nox_geometry::ELegIndex::RightFront, "right_front"},
        {nox_geometry::ELegIndex::RightMid, "right_mid"},
        {nox_geometry::ELegIndex::RightBack, "right_back"},
        {nox_geometry::ELegIndex::LeftFront, "left_front"},
        {nox_geometry::ELegIndex::LeftMid, "left_mid"},
        {nox_geometry::ELegIndex::LeftBack, "left_back"},
    };

    for (const auto& [leg_idx, prefix] : leg_order) {
        auto it = legs.find(leg_idx);
        if (it == legs.end()) continue;
        const auto& a = it->second;
        msg.name.push_back(prefix + "_coxa_joint");
        msg.position.push_back(a.torso_coxa.numerical_value_in(nox_geometry::units::rad));
        msg.name.push_back(prefix + "_femur_joint");
        msg.position.push_back(a.coxa_femur.numerical_value_in(nox_geometry::units::rad));
        msg.name.push_back(prefix + "_tibia_joint");
        msg.position.push_back(a.femur_tibia.numerical_value_in(nox_geometry::units::rad));
    }

    msg.name.push_back("head_yaw_joint");
    msg.position.push_back(head.yaw.numerical_value_in(nox_geometry::units::rad));
    msg.name.push_back("head_pitch_joint");
    msg.position.push_back(head.pitch.numerical_value_in(nox_geometry::units::rad));

    pub_joint_states_->publish(msg);
}

void CRequester::onBodyPose(const BodyPose& msg) {
    if (!nox_geometry::hasBodyPose(msg) || !nox_geometry::validBodyPose(msg)) {
        RCLCPP_WARN(node_->get_logger(), "Ignoring empty or non-finite body pose");
        return;
    }
    const auto resolved = nox_geometry::resolveBodyPose(nox_geometry::bodyPose(*kinematics_), msg);
    kinematics_->moveTorso(nox_geometry::toeTargets(resolved),
                           nox_geometry::CPose(resolved.torso_pose));
    kinematics_->setHeadOrientation(nox_geometry::COrientation(resolved.head_orientation));
    const auto now = std::chrono::steady_clock::now();
    pending_duration_s_.reset();
    if (last_pose_received_) {
        const double dt = std::chrono::duration<double>(now - *last_pose_received_).count();
        if (dt >= 0.01 && dt <= 0.5) pending_duration_s_ = dt;
    }
    last_pose_received_ = now;
    pending_pose_ = true;
}

void CRequester::update(std::chrono::milliseconds timeslice) {
    if (pending_pose_) {
        pending_pose_ = false;
        double duration_s = pending_duration_s_.value_or(double(timeslice.count() / 1000.0));
        sendServoRequest(duration_s);
    }
    pub_body_pose_->publish(nox_geometry::bodyPose(*kinematics_));
    publishJointStates(kinematics_->getLegAngles(), kinematics_->getHeadOrientation());
}

}  // namespace nox_movement
