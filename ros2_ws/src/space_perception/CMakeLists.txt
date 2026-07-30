cmake_minimum_required(VERSION 3.8)
project(space_perception)

if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(diagnostic_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav2_costmap_2d REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(pluginlib REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_lifecycle REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)
find_package(tf2_ros REQUIRED)

add_library(traversability_layer SHARED
  src/traversability_cost.cpp
  src/traversability_layer.cpp
)
target_compile_features(traversability_layer PUBLIC cxx_std_17)
target_include_directories(traversability_layer PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)
ament_target_dependencies(traversability_layer
  geometry_msgs
  diagnostic_msgs
  nav2_costmap_2d
  nav_msgs
  pluginlib
  rclcpp
  rclcpp_lifecycle
  sensor_msgs
  tf2
  tf2_geometry_msgs
  tf2_ros
)

pluginlib_export_plugin_description_file(
  nav2_costmap_2d traversability_layer.xml
)

ament_python_install_package(${PROJECT_NAME})
install(PROGRAMS
  scripts/depth_overlay_node
  scripts/local_elevation_map_node
  scripts/terrain_feature_node
  scripts/terrain_pointcloud_filter_node
  scripts/terrain_traversability_node
  scripts/traversability_calibration
  DESTINATION lib/${PROJECT_NAME}
)
install(TARGETS traversability_layer
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin
)
install(DIRECTORY include/ DESTINATION include)
install(FILES traversability_layer.xml DESTINATION share/${PROJECT_NAME})
install(DIRECTORY config launch DESTINATION share/${PROJECT_NAME})

if(BUILD_TESTING)
  find_package(ament_cmake_gtest REQUIRED)
  find_package(ament_cmake_pytest REQUIRED)
  find_package(ament_cmake_flake8 REQUIRED)
  find_package(ament_cmake_pep257 REQUIRED)

  ament_add_gtest(test_traversability_cost
    test/test_traversability_cost.cpp
    src/traversability_cost.cpp
  )
  target_include_directories(test_traversability_cost PRIVATE include)
  ament_target_dependencies(test_traversability_cost nav2_costmap_2d)

  ament_add_gtest(test_traversability_plugin
    test/test_traversability_plugin.cpp
  )
  ament_target_dependencies(
    test_traversability_plugin nav2_costmap_2d pluginlib rclcpp
  )

  ament_add_pytest_test(
    test_rover_derived_thresholds test/test_rover_derived_thresholds.py
  )
  ament_add_pytest_test(test_terrain_features test/test_terrain_features.py)
  ament_add_pytest_test(test_terrain_processing test/test_terrain_processing.py)
  ament_add_pytest_test(test_traversability test/test_traversability.py)
  ament_flake8()
  ament_pep257()
endif()

ament_export_include_directories(include)
ament_export_libraries(traversability_layer)
ament_export_dependencies(
  geometry_msgs nav2_costmap_2d nav_msgs pluginlib rclcpp
  rclcpp_lifecycle sensor_msgs tf2 tf2_geometry_msgs tf2_ros diagnostic_msgs
)
ament_package()
