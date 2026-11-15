# RumbleX Nox

Independent ROS 2 repository for the Nox hexapod. This repository contains
only Nox's hardware configuration, software, robot models and CAD.
Shared algorithms are maintained here independently. See [source provenance](PROVENANCE.md).

## Getting started

Use Ubuntu 26.04 with ROS 2 Lyrical, C++23 and CMake 3.25 or newer.
Clone into `~/Workspace/colcon_nox/src/ros2_rumblex_nox`.

```bash
git clone --recurse-submodules https://github.com/SteinRobotics/ros2_rumblex_nox.git
```

Follow [setup](README_SETUP.md), [build and test](BUILD.md), and
[launch commands](README_LAUNCH.md). [Resource limits](nox_doc/BUILD_AND_TEST.md)
apply to builds, tests, simulation and CAD jobs.

## Packages and hardware

Core packages are `nox_brain`, `nox_movement`, `nox_interfaces`,
`nox_utils`, `nox_communication`, `nox_hmi` and `nox_teleop`.
`nox_bringup` assembles the hardware stack; `nox_description`,
`nox_gazebo` and `nox_navigation` supply models, simulation and navigation.

Nox uses Hiwonder servos, Garmin 1D lidar and head-scan perception.
See [sensors](SENSORS.md), [bill of materials](BOM_NOX.md), and
[CAD](nox_description/cad/README.md).

## Interfaces and configuration

All owned packages and custom message types use the `nox_` prefix.
Node names, topic names, message fields and existing hardware calibration are preserved.
Old `rumblex_*` launch commands and message package names must be updated by clients.

Launch files target Nox directly and have no `robot` selection argument.
Package-owned settings remain in `config/nox/`. Private speech models and credentials
are not committed; supply `nox_communication/models/nox.onnx` locally.

The Garmin submodule retains commit `7951ea641d1443e378af4e26878d07af219a403e`. That commit is available in this local checkout but was not reachable from the configured GitHub remote during the split. Publish it to the dependency remote before relying on a fresh recursive clone.

## Raspberry Pi 5 Pin Layout
The Raspberry Pi 5 inside Nox hosts most of the human-machine interface hardware that lives in `rumblex_hmi/`. The table follows the standard 40-pin header (odd numbers on the left when the USB ports face you). Pins with descriptions are currently wired up; empty cells are free for experiments.

| Pin   | Signal        | Usage                  | Pin    | Signal        | Usage               |
| ----- | ------------- | ---------------------- | ------ | ------------- | ------------------- |
| **1** | 3V3           | supply for I2C modules | 2      | 5V            | —                   |
| **3** | GPIO2 (SDA1)  | I2C bus                | **4**  | 5V            | Servo Power Relay   |
| **5** | GPIO3 (SCL1)  | I2C bus                | **6**  | GND           | GND for I2C modules |
| 7     | GPIO4         | —                      | 8      | GPIO14 (TXD)  | —                   |
| 9     | GND           | —                      | 10     | GPIO15 (RXD)  | —                   |
| 11    | GPIO17        | —                      | 12     | GPIO18        | —                   |
| 13    | GPIO27        | —                      | **14** | GND           | Servo Power Relay   |
| 15    | GPIO22        | —                      | 16     | GPIO23        |                     |
| 17    | 3V3           | —                      | 18     | GPIO24        | —                   |
| 19    | GPIO10 (MOSI) | —                      | 20     | GND           | —                   |
| 21    | GPIO9 (MISO)  | —                      | 22     | GPIO25        | —                   |
| 23    | GPIO11 (SCLK) | —                      | 24     | GPIO8 (CE0)   | —                   |
| 25    | GND           | —                      | 26     | GPIO7 (CE1)   | —                   |
| 27    | GPIO0 (ID_SD) | —                      | 28     | GPIO1 (ID_SC) | —                   |
| 29    | GPIO5         | —                      | 30     | GND           | —                   |
| 31    | GPIO6         | —                      | 32     | GPIO12        | —                   |
| 33    | GPIO13        | —                      | **34** | GND           | BNO055 I2C switch   |
| 35    | GPIO19        | —                      | **36** | GPIO16        | Servo Power Relay   |
| 37    | GPIO26        | —                      | 38     | GPIO20        | —                   |
| 39    | GND           | —                      | 40     | GPIO21        | —                   |


### I2C Device Addresses
| Device               | Address |
| -------------------- | ------- |
| BNO055 IMU           | 0x29    |
| SSD1306 OLED Display | 0x3C    |
| INA228 Power Monitor | 0x40    |
| Garmin Lidar Lite    | 0x62    |




See [split validation](VALIDATION.md) for build results and existing test mismatches.

The workspace has its own [Python dependency manifest](requirements/README.md);
activate it with `source scripts/environment.sh`. CAD remains separate.
