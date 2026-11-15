cmake_minimum_required(VERSION 3.25)
project(nox_brain)

if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 23)
endif()
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic -Werror)
endif()

find_package(ament_cmake REQUIRED)
find_package(ament_index_cpp REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(std_srvs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nox_interfaces REQUIRED)
find_package(nox_utils REQUIRED)
find_package(yaml-cpp REQUIRED)
find_package(nlohmann_json REQUIRED) # nlohmann_json -> sudo apt install nlohmann-json3-dev

## set sources
set(SOURCES
src/gait/gait_continuous_pose.cpp
src/gait/gait_controller.cpp
src/gait/gait_leg_wave.cpp
src/gait/gait_move_combined.cpp
src/gait/gait_move_crawl.cpp
src/gait/gait_move_tripod.cpp
src/gait/gait_move_ripple.cpp
src/gait/gait_move_wave.cpp
src/gait/stride_planner.cpp
src/gait/gait_single_pose.cpp
src/gait/gait_test_legs.cpp
src/gait/gait_torso_roll.cpp
src/gait/gait_waiting.cpp
src/gait/gait_yaw_sequence.cpp
src/requester/coordinator.cpp
src/action/action_planner.cpp
src/requester/recognition.cpp
src/requester/error_management.cpp
src/requester/text_interpreter.cpp
src/handler/system.cpp
src/handler/communication.cpp
src/handler/movement.cpp
src/gait/hold_distance_control.cpp
src/gait/level_torso_control.cpp
src/gait/gait_hold_distance.cpp
src/gait/gait_level_torso.cpp
src/parser/sequence_parser.cpp
src/parser/sequence_loader.cpp
src/parser/action_decoder.cpp
)
add_library(nox_brain_lib ${SOURCES})
target_compile_features(nox_brain_lib PUBLIC cxx_std_23)
target_include_directories(nox_brain_lib PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)
target_link_libraries(nox_brain_lib PUBLIC
  ${std_srvs_TARGETS}
  nox_utils::nox_geometry
  ${sensor_msgs_TARGETS}
  tf2::tf2
  tf2_ros::tf2_ros
  rclcpp::rclcpp
  ament_index_cpp::ament_index_cpp
  ${nox_interfaces_TARGETS}
  ${nox_utils_TARGETS}
  nlohmann_json::nlohmann_json
  yaml-cpp::yaml-cpp
)

add_executable(node_brain
  src/node_brain.cpp
)
target_link_libraries(node_brain PRIVATE
  nox_brain_lib
  ${sensor_msgs_TARGETS}
  tf2::tf2
  tf2_ros::tf2_ros
  rclcpp::rclcpp
  ${std_msgs_TARGETS}
  ${geometry_msgs_TARGETS}
  ament_index_cpp::ament_index_cpp
  ${nox_interfaces_TARGETS}
  nlohmann_json::nlohmann_json
)
target_include_directories(node_brain PRIVATE include)

include_directories(
  include/nox_brain/
)

install(TARGETS nox_brain_lib
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib)
ament_export_libraries(nox_brain_lib)

install(TARGETS
  node_brain
  DESTINATION lib/${PROJECT_NAME})

install(DIRECTORY
  launch
  config
  DESTINATION share/${PROJECT_NAME}/
)

install(DIRECTORY tools
  DESTINATION share/${PROJECT_NAME}/
  PATTERN "__pycache__" EXCLUDE
  PATTERN "*.pyc" EXCLUDE)

# Unit tests
if(BUILD_TESTING)
  find_package(Python3 REQUIRED COMPONENTS Interpreter)
  add_test(NAME test_choreography
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/test/test_choreography.py)
  add_test(NAME test_sequence_generator
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/test/test_sequence_generator.py)
  find_package(ament_cmake_gtest REQUIRED)
  ament_add_gtest(test_sensor_gaits test/test_sensor_gaits.cpp)
  target_link_libraries(test_sensor_gaits nox_brain_lib)
  ament_add_gtest(test_leveling_movement_handler test/test_leveling_movement_handler.cpp)
  target_link_libraries(test_leveling_movement_handler nox_brain_lib)
  ament_add_gtest(test_feedback_movement_handler test/test_feedback_movement_handler.cpp)
  target_link_libraries(test_feedback_movement_handler nox_brain_lib)
  ament_add_gtest(test_hold_distance_control test/test_hold_distance_control.cpp)
  target_link_libraries(test_hold_distance_control nox_brain_lib)
  ament_add_gtest(test_level_torso_control test/test_level_torso_control.cpp)
  target_link_libraries(test_level_torso_control nox_brain_lib)
  ament_add_gtest(test_sequence_parser test/test_sequence_parser.cpp)
  target_link_libraries(test_sequence_parser nox_brain_lib)
  add_test(NAME test_section_parser
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/test/test_section_parser.py
      $<TARGET_FILE:test_sequence_parser>)
  target_compile_definitions(test_sequence_parser PRIVATE
    NOX_SEQUENCES_DIRECTORY="${CMAKE_CURRENT_SOURCE_DIR}/config/sequences")
  ament_add_gtest(test_orientation_timing test/test_orientation_timing.cpp)
  target_link_libraries(test_orientation_timing nox_brain_lib)

  ament_add_gtest(test_units test/test_units.cpp)
  target_link_libraries(test_units nox_brain_lib)

  ament_add_gtest(test_velocity test/test_velocity.cpp)
  target_link_libraries(test_velocity nox_brain_lib)

  ament_add_gtest(test_movement_types
    test/test_movement_types.cpp
    test/test_movement_types_other_translation_unit.cpp
  )
  target_link_libraries(test_movement_types nox_brain_lib)
  ament_add_gtest(test_coordinator test/test_coordinator.cpp)
  target_link_libraries(test_coordinator nox_brain_lib)
  ament_add_gtest(test_trajectory_transitions test/test_trajectory_transitions.cpp)
  target_link_libraries(test_trajectory_transitions nox_brain_lib)
  ament_add_gtest(test_locomotion_transitions test/test_locomotion_transitions.cpp)
  target_link_libraries(test_locomotion_transitions nox_brain_lib)
  ament_add_gtest(test_robot_configuration test/test_robot_configuration.cpp)
  target_link_libraries(test_robot_configuration nox_brain_lib)
  target_compile_definitions(test_robot_configuration PRIVATE NOX_SOURCE_DIR="${CMAKE_CURRENT_SOURCE_DIR}/..")
  ament_add_gtest(test_movement_handler test/test_movement_handler.cpp)
  target_link_libraries(test_movement_handler nox_brain_lib)
  target_compile_definitions(test_movement_handler PRIVATE
    NOX_SEQUENCES_DIRECTORY="${CMAKE_CURRENT_SOURCE_DIR}/config/sequences")
  ament_add_gtest(test_communication_handler test/test_communication_handler.cpp)
  target_link_libraries(test_communication_handler nox_brain_lib)
  ament_add_gtest(test_single_pose_target test/test_single_pose_target.cpp)
  target_link_libraries(test_single_pose_target nox_brain_lib)
  target_compile_definitions(test_single_pose_target PRIVATE
    NOX_SEQUENCES_DIRECTORY="${CMAKE_CURRENT_SOURCE_DIR}/config/sequences")
  ament_add_gtest(test_body_pose test/test_body_pose.cpp)
  target_link_libraries(test_body_pose nox_brain_lib)
  ament_add_gtest(test_gait_yaw_sequence test/test_gait_yaw_sequence.cpp)
  target_link_libraries(test_gait_yaw_sequence nox_brain_lib)
  ament_add_gtest(test_gait_controller test/test_gait_controller.cpp)
  target_link_libraries(test_gait_controller nox_brain_lib)
  ament_add_gtest(test_gait_lay_down test/test_gait_lay_down.cpp)
  target_link_libraries(test_gait_lay_down nox_brain_lib)
  ament_add_gtest(test_gait_leg_wave test/test_gait_leg_wave.cpp)
  target_link_libraries(test_gait_leg_wave nox_brain_lib)
  ament_add_gtest(test_gait_stand_up test/test_gait_stand_up.cpp)
  target_link_libraries(test_gait_stand_up nox_brain_lib)
  ament_add_gtest(test_gait_torso_roll test/test_gait_torso_roll.cpp)
  target_link_libraries(test_gait_torso_roll nox_brain_lib)
  ament_add_gtest(test_text_interpreter 
    test/test_text_interpreter.cpp
  )
  if(TARGET test_text_interpreter)
    target_include_directories(test_text_interpreter PRIVATE include)
    target_link_libraries(test_text_interpreter nox_brain_lib rclcpp::rclcpp ament_index_cpp::ament_index_cpp ${nox_interfaces_TARGETS} nlohmann_json::nlohmann_json)
  endif()

  ament_add_gtest(test_error_management
    test/test_error_management.cpp
  )
  if(TARGET test_error_management)
    target_include_directories(test_error_management PRIVATE include)
    target_link_libraries(test_error_management nox_brain_lib rclcpp::rclcpp ${nox_interfaces_TARGETS} ${nox_utils_TARGETS})
  endif()


endif()

ament_package()
