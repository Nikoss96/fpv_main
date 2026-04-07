import json

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from yolo_msgs.msg import DetectionArray


class DetectionLabelsNode(Node):
    def __init__(self) -> None:
        super().__init__("detection_labels_node")

        self.declare_parameter("input_topic", "detections")
        self.declare_parameter("output_topic", "detection_labels")
        self.declare_parameter("deduplicate", True)

        input_topic = self.get_parameter("input_topic").value
        output_topic = self.get_parameter("output_topic").value
        self.deduplicate = bool(self.get_parameter("deduplicate").value)

        self.publisher = self.create_publisher(String, output_topic, 10)
        self.subscription = self.create_subscription(
            DetectionArray, input_topic, self.detections_callback, 10
        )

    def detections_callback(self, msg: DetectionArray) -> None:
        detections = []
        labels = []

        for detection in msg.detections:
            label = detection.class_name or str(detection.class_id)
            labels.append(label)
            detections.append(
                {
                    "label": label,
                    "score": round(float(detection.score), 4),
                    "track_id": detection.id,
                }
            )

        if self.deduplicate:
            ordered_labels = list(dict.fromkeys(labels))
        else:
            ordered_labels = labels

        payload = {
            "frame_id": msg.header.frame_id,
            "stamp": {
                "sec": int(msg.header.stamp.sec),
                "nanosec": int(msg.header.stamp.nanosec),
            },
            "count": len(detections),
            "labels": ordered_labels,
            "detections": detections,
        }

        self.publisher.publish(String(data=json.dumps(payload, ensure_ascii=True)))


def main(args=None) -> None:
    rclpy.init(args=args)
    node = DetectionLabelsNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
