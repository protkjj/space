cmake_minimum_required(VERSION 3.8)
project(space_msgs)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(builtin_interfaces REQUIRED)
find_package(grid_map_msgs REQUIRED)
find_package(std_msgs REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  msg/RoverSpec.msg
  msg/SlipEstimate.msg
  msg/TerrainEstimate.msg
  msg/TraversabilityScore.msg
  DEPENDENCIES builtin_interfaces grid_map_msgs std_msgs
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
