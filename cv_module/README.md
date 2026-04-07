# cv_module

Local CV module for `fpv_main`, based on `yolo_ros`.

It is configured as a simple detector block:

- image from camera comes in on `/camera/color/image_raw`,
- YOLO detections are published on `/cv/detections`,
- compact detection labels are published on `/cv/detection_labels`.

## Quick Start

```bash
cd /home/andrey/projects/fpv_main/cv_module
pip3 install -r requirements.txt
./launch_cv_detector.bash
```

If your camera source is in ROS 1 and the detector runs in ROS 2, use:

```bash
./compat/fpv_main_bridge.bash
```

More integration notes: `FPV_MAIN_INTEGRATION.md`
