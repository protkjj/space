cmake_minimum_required(VERSION 3.8)
project(space_description)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)

# rover_geometry.py derives every rover-dependent threshold from
# config/rover_geometry.yaml. It ships here, with the geometry it reads, because
# this package owns the rover's physical description and depends on nothing --
# so perception, bringup, and mission can all import it without inverting the
# dependency graph.
ament_python_install_package(${PROJECT_NAME})

install(
  DIRECTORY
    config
    meshes
    urdf
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  # Explicit linters rather than ament_lint_auto, matching space_perception --
  # the other ament_cmake package that ships Python. lint_auto pulls in
  # ament_copyright, and no Python file anywhere in this workspace carries a
  # copyright header, so it would fail on arrival. space_gazebo shows what
  # happens otherwise: it uses lint_auto with Python and sits at 35 failures.
  find_package(ament_cmake_flake8 REQUIRED)
  find_package(ament_cmake_pep257 REQUIRED)
  ament_flake8()
  ament_pep257()

  # Guards the single source of truth: if a CAD dimension moves and a derived
  # value does not follow, this fails instead of shipping a plausible number for
  # a rover that no longer exists.
  find_package(ament_cmake_pytest REQUIRED)
  ament_add_pytest_test(test_rover_geometry test/test_rover_geometry.py)
endif()

ament_package()
