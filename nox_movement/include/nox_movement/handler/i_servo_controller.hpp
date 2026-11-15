#pragma once

#include <cstdint>
#include <functional>
#include <map>

#include "nox_utils/body_types.hpp"

namespace nox_movement {

// The controller operations needed by the movement requester. Implementations can
// be substituted without constructing ROS subscriptions or opening a servo bus.
class IServoController {
   public:
    using InitialAnglesCallback =
        std::function<void(const std::map<nox_geometry::ELegIndex, nox_geometry::CLegAngles>&,
                           const nox_geometry::COrientation&)>;

    virtual ~IServoController() = default;

    virtual void requestAngles(const std::map<uint32_t, double>& target_angles, double duration_s) = 0;
    // Registers the callback and starts initialization; the callback may run before this returns.
    virtual void setInitialAnglesCallback(InitialAnglesCallback callback) = 0;
};

}  // namespace nox_movement
