# cv_module in fpv_main

## Purpose

This module is a camera-in / detections-out CV block for the current project.

## Input

Default input image topic:

- `/camera/color/image_raw`

This matches the existing simulator/PX4 setup in `fpv_main`.

## Output

Structured detections from YOLO:

- `/cv/detections` (`yolo_msgs/DetectionArray`, ROS 2)

Compact detection labels for easy consumption:

- `/cv/detection_labels` (`std_msgs/String`, ROS 2/ROS 1 bridge friendly)

The string payload is JSON and contains:

- `count`
- `labels`
- `detections` with `label`, `score`, and `track_id`

## Recommended Run Order

1. Start your current camera source in `fpv_main`.
2. If needed across ROS 1 and ROS 2, start:
   `./compat/fpv_main_bridge.bash`
3. Start detector:
   `./launch_cv_detector.bash`

## Notes

- The default model is `yolov8n.pt` for lighter inference.
- Override compute device if GPU is available:
  `DEVICE=cuda:0 ./launch_cv_detector.bash`
