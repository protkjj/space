cmake_minimum_required(VERSION 3.8)
project(space_gazebo)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY assets config launch models urdf worlds
  DESTINATION share/${PROJECT_NAME}
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
