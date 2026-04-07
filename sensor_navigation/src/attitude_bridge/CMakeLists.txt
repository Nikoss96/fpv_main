cmake_minimum_required(VERSION 3.0.2)
project(attitude_bridge)

find_package(catkin REQUIRED COMPONENTS
  rospy
  geometry_msgs
  nav_msgs
  std_msgs
  mavros_msgs
)

catkin_package()

catkin_install_python(PROGRAMS
  scripts/attitude_bridge.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
