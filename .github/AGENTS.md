# Agents

## Context

- This is a **ROS 2** (Robot Operating System 2) C++ project for a hexapod robot.

## Code Guidelines

- Use **references** (`&` / `const&`) over raw pointers. When pointers are necessary, use smart pointers (`std::shared_ptr`, `std::unique_ptr`).
- Prefer **C++23** features where useful (e.g., `std::format`, concepts, ranges, designated initializers, `std::span`).

## Build Instructions

Follow [the resource-limited build guide](../nox_doc/BUILD_AND_TEST.md).
Run heavy workloads sequentially; use the verified memory and time limits and worker limits there.
