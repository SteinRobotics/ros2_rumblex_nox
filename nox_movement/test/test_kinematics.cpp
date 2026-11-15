#include <gtest/gtest.h>

#include "rclcpp/rclcpp.hpp"
#include "nox_utils/body_model.hpp"
#include "test_helpers.hpp"

using namespace std;

class KinematicsTest : public ::testing::Test {
   protected:
    void SetUp() override {
        if (!rclcpp::ok()) {
            rclcpp::init(0, nullptr);
        }
        rclcpp::NodeOptions options;
        auto overrides = nox_movement::test_helpers::defaultRobotParameters();
        options.parameter_overrides(overrides);
        node_ = std::make_shared<rclcpp::Node>("test_kinematics_node", options);
        kin_ = std::make_unique<nox_geometry::CBodyModel>(node_);
        cout << "KinematicsTest SetUp complete" << endl;
    }

    void TearDown() override {
        kin_.reset();
        if (rclcpp::ok()) {
            rclcpp::shutdown();
        }
    }

    std::shared_ptr<rclcpp::Node> node_;
    std::unique_ptr<nox_geometry::CBodyModel> kin_;
};

// Standing position
// RightFront: 	ag: 0.000°, 2.276°, 7.704°	| x: 0.201, y: -0.160, z: -0.050

// Laydown position
// RightFront: 	ag: 0.000°, 70.723°, -53.320°	| x: 0.180, y: -0.139, z: 0.010

TEST_F(KinematicsTest, setLegAngles) {
    // create target angles
    nox_geometry::CLegAngles angles;
    angles.torso_coxa = 0.0 * nox_geometry::units::deg;
    angles.coxa_femur = 2.276 * nox_geometry::units::deg;
    angles.femur_tibia = 7.704 * nox_geometry::units::deg;

    kin_->setLegAngles(nox_geometry::ELegIndex::RightFront, angles);

    nox_geometry::CPosition toe_pos_expected;
    toe_pos_expected.x = 0.201 * nox_geometry::units::m;   // 0.092 + 0.109
    toe_pos_expected.y = -0.160 * nox_geometry::units::m;  // -0.092 - 0.068
    toe_pos_expected.z = -0.050 * nox_geometry::units::m;  // 0.045 - 0.095

    auto& leg = kin_->getLegs().at(nox_geometry::ELegIndex::RightFront);

    expectPositionNear(toe_pos_expected, leg.toe_position, "setLegAngles position mismatch");
    expectAnglesNear(angles, leg.angles, "setLegAngles angles mismatch");
}

TEST_F(KinematicsTest, check_standing_position) {
    kin_->moveTorso(kin_->getStandingToePositions());
    auto& leg = kin_->getLegs().at(nox_geometry::ELegIndex::RightFront);

    nox_geometry::CPosition toe_pos_expected;
    toe_pos_expected.x = 0.201 * nox_geometry::units::m;   // 0.092 + 0.109
    toe_pos_expected.y = -0.160 * nox_geometry::units::m;  // -0.092 - 0.068
    toe_pos_expected.z = -0.050 * nox_geometry::units::m;  // 0.045 - 0.095

    nox_geometry::CLegAngles angles_expected;
    angles_expected.torso_coxa = 0.0 * nox_geometry::units::deg;
    angles_expected.coxa_femur = 2.276 * nox_geometry::units::deg;
    angles_expected.femur_tibia = 7.704 * nox_geometry::units::deg;

    expectPositionNear(toe_pos_expected, leg.toe_position, "standing position mismatch");
    expectAnglesNear(angles_expected, leg.angles, "standing angles mismatch");
}

TEST_F(KinematicsTest, check_laydown_position) {
    kin_->moveTorso(kin_->getLaydownToePositions());
    auto& leg = kin_->getLegs().at(nox_geometry::ELegIndex::RightFront);

    nox_geometry::CPosition toe_pos_expected;
    toe_pos_expected.x = 0.180 * nox_geometry::units::m;   // 0.071 + 0.109
    toe_pos_expected.y = -0.139 * nox_geometry::units::m;  // -0.071 - 0.068
    toe_pos_expected.z = 0.010 * nox_geometry::units::m;   // 0.045 - 0.035

    nox_geometry::CLegAngles angles_expected;
    angles_expected.torso_coxa = 0.0 * nox_geometry::units::deg;
    angles_expected.coxa_femur = 70.723 * nox_geometry::units::deg;
    angles_expected.femur_tibia = -53.320 * nox_geometry::units::deg;

    expectPositionNear(toe_pos_expected, leg.toe_position, "laydown position mismatch");
    expectAnglesNear(angles_expected, leg.angles, "laydown angles mismatch");
}

TEST_F(KinematicsTest, check_set_toe) {
    nox_geometry::CPosition target_pos;
    target_pos.x = 0.201 * nox_geometry::units::m;   // 0.092 + 0.109
    target_pos.y = -0.160 * nox_geometry::units::m;  // -0.092 - 0.068
    target_pos.z = -0.050 * nox_geometry::units::m;  // 0.045 - 0.095

    kin_->setToePosition(nox_geometry::ELegIndex::RightFront, target_pos);
    auto& leg = kin_->getLegs().at(nox_geometry::ELegIndex::RightFront);

    nox_geometry::CLegAngles angles_expected;
    angles_expected.torso_coxa = 0.0 * nox_geometry::units::deg;
    angles_expected.coxa_femur = 2.276 * nox_geometry::units::deg;
    angles_expected.femur_tibia = 7.704 * nox_geometry::units::deg;

    expectPositionNear(target_pos, leg.toe_position, "setToe position mismatch");
    expectAnglesNear(angles_expected, leg.angles, "setToe angles mismatch");
}

TEST_F(KinematicsTest, TorsoRotationPreservesLegLocalTarget) {
    kin_->moveTorso(kin_->getStandingToePositions());
    const auto standing_angles = kin_->getLegAngles(nox_geometry::ELegIndex::RightFront);

    // Rotate the entire standing toe (201, -160, -50) mm with the torso.
    // The joint angles must remain unchanged, including the leg vector rotation.
    const std::array<std::pair<nox_geometry::COrientation, nox_geometry::CPosition>, 3> cases = {{
        {nox_geometry::COrientation(90.0 * nox_geometry::units::deg,
                                        0.0 * nox_geometry::units::rad,
                                        0.0 * nox_geometry::units::rad),
         nox_geometry::CPosition(201.0 * nox_geometry::units::mm, 50.0 * nox_geometry::units::mm,
                                     -160.0 * nox_geometry::units::mm)},
        {nox_geometry::COrientation(0.0 * nox_geometry::units::rad,
                                        90.0 * nox_geometry::units::deg,
                                        0.0 * nox_geometry::units::rad),
         nox_geometry::CPosition(-50.0 * nox_geometry::units::mm,
                                     -160.0 * nox_geometry::units::mm,
                                     -201.0 * nox_geometry::units::mm)},
        {nox_geometry::COrientation(0.0 * nox_geometry::units::rad,
                                        0.0 * nox_geometry::units::rad,
                                        90.0 * nox_geometry::units::deg),
         nox_geometry::CPosition(160.0 * nox_geometry::units::mm, 201.0 * nox_geometry::units::mm,
                                     -50.0 * nox_geometry::units::mm)},
    }};

    for (const auto& [orientation, target] : cases) {
        kin_->moveTorso({{nox_geometry::ELegIndex::RightFront, target}},
                        nox_geometry::CPose(nox_geometry::CPosition(), orientation));
        expectAnglesNear(standing_angles, kin_->getLegAngles(nox_geometry::ELegIndex::RightFront),
                         "rotated mount changed the leg-local target");
    }
}
