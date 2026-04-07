import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    namespace = LaunchConfiguration("namespace", default="cv")
    input_image_topic = LaunchConfiguration(
        "input_image_topic", default="/camera/color/image_raw"
    )
    model = LaunchConfiguration("model", default="yolov8n.pt")
    device = LaunchConfiguration("device", default="cpu")
    threshold = LaunchConfiguration("threshold", default="0.4")
    image_reliability = LaunchConfiguration("image_reliability", default="1")

    yolo_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory("yolo_bringup"),
                "launch",
                "yolo.launch.py",
            )
        ),
        launch_arguments={
            "model": model,
            "device": device,
            "threshold": threshold,
            "input_image_topic": input_image_topic,
            "image_reliability": image_reliability,
            "namespace": namespace,
            "use_tracking": "False",
            "use_debug": "False",
            "use_3d": "False",
        }.items(),
    )

    labels_node = Node(
        package="yolo_ros",
        executable="detection_labels_node",
        name="detection_labels_node",
        namespace=namespace,
        parameters=[
            {
                "input_topic": "detections",
                "output_topic": "detection_labels",
                "deduplicate": True,
            }
        ],
    )

    return LaunchDescription([yolo_launch, labels_node])
