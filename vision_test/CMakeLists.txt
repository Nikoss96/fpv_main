cmake_minimum_required(VERSION 3.0.2)
project(vision_test)

find_package(catkin REQUIRED COMPONENTS
  rospy
  std_msgs
  geometry_msgs
  nav_msgs
)

catkin_package()

# Установка Python-скриптов как исполняемых ROS-узлов
catkin_install_python(PROGRAMS
  src/autonomy_test.py
  src/waypoint_publisher.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)
