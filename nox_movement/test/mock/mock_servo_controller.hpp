#pragma once

#include <vector>

#include "handler/i_servo_controller.hpp"

namespace nox_movement {

class CServoControllerMock : public IServoController {
   public:
    struct Request {
        std::map<uint32_t, double> target_angles;
        double duration_s;
    };

    void requestAngles(const std::map<uint32_t, double>& target_angles, double duration_s) override {
        requests.push_back({target_angles, duration_s});
    }

    void setInitialAnglesCallback(InitialAnglesCallback callback) override {
        callback(initial_leg_angles, initial_head_orientation);
    }

    std::vector<Request> requests;
    std::map<nox_geometry::ELegIndex, nox_geometry::CLegAngles> initial_leg_angles;
    nox_geometry::COrientation initial_head_orientation;
};

}  // namespace nox_movement
