#!/usr/bin/env python3
"""
waypoint_publisher.py
---------------------
Project 2176 — МИЭМ НИУ ВШЭ
Публикует одну целевую точку (x, y, z) из параметров ROS.
Удобен для проверки позиционного контроля по одной точке.

Использование:
  rosrun vision_test waypoint_publisher.py _x:=5.0 _y:=0.0 _z:=2.0
  rosrun vision_test waypoint_publisher.py _x:=5.0 _y:=0.0 _z:=2.0 _rate:=10
"""

import rospy
from geometry_msgs.msg import PoseStamped


def main():
    rospy.init_node("waypoint_publisher", anonymous=False)

    x = rospy.get_param("~x", 0.0)
    y = rospy.get_param("~y", 0.0)
    z = rospy.get_param("~z", 2.0)
    rate_hz = rospy.get_param("~rate", 20)

    pub = rospy.Publisher("/p2176/quadcopter/setpoint_pose", PoseStamped, queue_size=1)
    rate = rospy.Rate(rate_hz)

    rospy.loginfo(f"[waypoint_publisher] Publishing setpoint: ({x}, {y}, {z}) at {rate_hz} Hz")

    msg = PoseStamped()
    msg.header.frame_id = "world"
    msg.pose.position.x = x
    msg.pose.position.y = y
    msg.pose.position.z = z
    msg.pose.orientation.w = 1.0

    while not rospy.is_shutdown():
        msg.header.stamp = rospy.Time.now()
        pub.publish(msg)
        rate.sleep()


if __name__ == "__main__":
    try:
        main()
    except rospy.ROSInterruptException:
        pass
