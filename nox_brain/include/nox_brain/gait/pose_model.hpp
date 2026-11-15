#pragma once
#include "nox_utils/body_model.hpp"
namespace brain {
using namespace nox_geometry;
class CPoseModel : public nox_geometry::CBodyModel {
   public:
    using CBodyModel::CBodyModel;
};
}  // namespace brain
