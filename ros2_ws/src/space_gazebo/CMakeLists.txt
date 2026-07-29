cmake_minimum_required(VERSION 3.8)
project(space_gazebo)

find_package(ament_cmake REQUIRED)
find_package(gz-gui8 REQUIRED)
find_package(gz-msgs10 REQUIRED)
find_package(gz-transport13 REQUIRED)
find_package(Qt5 REQUIRED COMPONENTS Core Qml Quick)

set(CMAKE_AUTOMOC ON)
qt5_add_resources(
  ROVER_KEY_TELEOP_RESOURCES
  src/RoverKeyTeleop.qrc
)

add_library(
  RoverKeyTeleop SHARED
  include/space_gazebo/rover_key_teleop.hpp
  src/rover_key_teleop.cpp
  ${ROVER_KEY_TELEOP_RESOURCES}
)
target_include_directories(
  RoverKeyTeleop PRIVATE
  include
)
target_link_libraries(
  RoverKeyTeleop PRIVATE
  gz-gui8::gz-gui8
  gz-msgs10::gz-msgs10
  gz-transport13::gz-transport13
  Qt5::Core
  Qt5::Qml
  Qt5::Quick
)

install(
  DIRECTORY assets config launch models urdf worlds
  DESTINATION share/${PROJECT_NAME}
)

install(
  TARGETS RoverKeyTeleop
  LIBRARY DESTINATION lib
)

install(
  PROGRAMS scripts/arena_marker_publisher.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME arena_marker_publisher
)

install(
  PROGRAMS tools/convert_arena_step.py
  DESTINATION share/${PROJECT_NAME}/tools
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # The project has not established a copyright holder; do not invent one.
  set(ament_cmake_copyright_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
