#!/bin/bash

set -euo pipefail

echo "Starting fpv_main camera/detection bridge"
echo "ROS1 -> ROS2: /camera/color/image_raw"
echo "ROS2 -> ROS1: /cv/detection_labels"

exec ros2 run ros1_bridge parameter_bridge \
  /camera/color/image_raw@sensor_msgs/msg/Image[sensor_msgs/Image \
  /cv/detection_labels@std_msgs/msg/String]std_msgs/String
