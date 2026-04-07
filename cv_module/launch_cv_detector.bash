#!/bin/bash

set -euo pipefail

IMAGE_TOPIC=${1:-/camera/color/image_raw}
MODEL=${MODEL:-yolov8n.pt}
DEVICE=${DEVICE:-cpu}
THRESHOLD=${THRESHOLD:-0.4}

exec ros2 launch yolo_bringup fpv_cv.launch.py \
  input_image_topic:=${IMAGE_TOPIC} \
  model:=${MODEL} \
  device:=${DEVICE} \
  threshold:=${THRESHOLD}
