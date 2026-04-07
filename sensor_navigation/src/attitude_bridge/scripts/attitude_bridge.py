#!/usr/bin/env python3
"""
attitude_bridge.py
------------------
Project 2176 — МИЭМ НИУ ВШЭ

Bridges sensor_navigation pathFollower → base_simulator quadcopterPlugin.

pathFollower publishes /attitude_control (geometry_msgs/TwistStamped):
  linear.x  → desired roll  [rad]
  linear.y  → desired pitch [rad]
  angular.z → desired yaw rate [rad/s]
  linear.z  → desired vertical velocity [m/s]

quadcopterPlugin cmd_acc mode expects /p2176/quadcopter/cmd_acc
(mavros_msgs/PositionTarget):
  acceleration_or_force.xyz → desired world-frame acceleration [m/s²]
  yaw                       → desired yaw angle [rad]

Conversion:
  1. Roll/pitch (body frame) → body-frame horizontal accelerations:
       acc_bx =  g * tan(pitch)
       acc_by = -g * tan(roll)
  2. Rotate body → world using current vehicle yaw from odometry:
       acc_wx = acc_bx * cos(yaw) - acc_by * sin(yaw)
       acc_wy = acc_bx * sin(yaw) + acc_by * cos(yaw)
  3. Vertical velocity → vertical acceleration via P controller:
       acc_wz = vel_z_gain * (vel_z_desired - vel_z_current)
  4. Integrate yaw_rate → target_yaw angle setpoint.
  5. Auto-takeoff: first /attitude_control message triggers a single
     /p2176/quadcopter/takeoff publication so the plugin transitions
     from LANDED_MODEL → FLYING_MODEL automatically.
"""

import math
import rospy
from geometry_msgs.msg import TwistStamped
from nav_msgs.msg import Odometry
from mavros_msgs.msg import PositionTarget
from std_msgs.msg import Empty

G = 9.81


class AttitudeBridge:
    def __init__(self):
        rospy.init_node('attitude_bridge', anonymous=False)

        # --- Parameters ---
        self.vel_z_gain   = rospy.get_param('~vel_z_gain',   2.0)
        self.auto_takeoff = rospy.get_param('~auto_takeoff', True)
        # Seconds to wait before forwarding commands after takeoff
        self.takeoff_delay = rospy.get_param('~takeoff_delay', 0.8)

        # --- State ---
        self.target_yaw    = None   # initialized from first odometry
        self.current_yaw   = 0.0
        self.current_vel_z = 0.0
        self.last_cmd_time  = None
        self.odom_received  = False
        self.took_off       = False
        self.takeoff_time   = None

        # --- Publishers ---
        self.cmd_acc_pub = rospy.Publisher(
            '/p2176/quadcopter/cmd_acc', PositionTarget, queue_size=1)
        self.takeoff_pub = rospy.Publisher(
            '/p2176/quadcopter/takeoff', Empty, queue_size=1)

        # --- Subscribers ---
        rospy.Subscriber('/p2176/quadcopter/odom', Odometry,     self.odom_cb)
        rospy.Subscriber('/attitude_control',      TwistStamped, self.attitude_cb)

        rospy.loginfo('[attitude_bridge] ready — waiting for odometry')

    # ------------------------------------------------------------------
    def odom_cb(self, msg):
        q = msg.pose.pose.orientation
        # yaw from quaternion (ZYX convention)
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        self.current_yaw   = math.atan2(siny_cosp, cosy_cosp)
        self.current_vel_z = msg.twist.twist.linear.z

        if not self.odom_received:
            self.target_yaw = self.current_yaw
            self.odom_received = True
            rospy.loginfo('[attitude_bridge] odometry received — bridge active')

    # ------------------------------------------------------------------
    def attitude_cb(self, msg):
        if not self.odom_received:
            return

        now = rospy.Time.now()

        # ── Auto-takeoff ─────────────────────────────────────────────
        if self.auto_takeoff and not self.took_off:
            self.takeoff_pub.publish(Empty())
            self.takeoff_time = now
            self.took_off = True
            rospy.loginfo('[attitude_bridge] takeoff command sent')

        # Wait for drone to reach FLYING_MODEL before forwarding commands
        if self.took_off and self.takeoff_time is not None:
            elapsed = (now - self.takeoff_time).to_sec()
            if elapsed < self.takeoff_delay:
                return

        # ── dt for yaw integration ───────────────────────────────────
        if self.last_cmd_time is not None:
            dt = (now - self.last_cmd_time).to_sec()
            dt = max(0.0, min(dt, 0.1))   # clamp to [0, 100 ms]
        else:
            dt = 0.0
        self.last_cmd_time = now

        # ── Unpack attitude command ──────────────────────────────────
        roll_cmd  = msg.twist.linear.x    # desired roll  [rad]
        pitch_cmd = msg.twist.linear.y    # desired pitch [rad]
        yaw_rate  = msg.twist.angular.z   # desired yaw rate [rad/s]
        vel_z_cmd = msg.twist.linear.z    # desired vertical velocity [m/s]

        # ── Integrate yaw rate → yaw angle setpoint ─────────────────
        self.target_yaw += yaw_rate * dt
        # Normalize to (-π, π)
        self.target_yaw = math.atan2(
            math.sin(self.target_yaw), math.cos(self.target_yaw))

        # ── Roll/pitch (body frame) → body-frame horizontal acceleration ─
        #   pitch > 0 = nose-up = forward acc; roll > 0 = right bank = left acc
        acc_bx =  G * math.tan(pitch_cmd)
        acc_by = -G * math.tan(roll_cmd)

        # ── Rotate body-frame → world-frame (yaw rotation only) ─────
        cy = math.cos(self.current_yaw)
        sy = math.sin(self.current_yaw)
        acc_wx = acc_bx * cy - acc_by * sy
        acc_wy = acc_bx * sy + acc_by * cy

        # ── Vertical: P-controller on velocity error ─────────────────
        acc_wz = self.vel_z_gain * (vel_z_cmd - self.current_vel_z)

        # ── Build PositionTarget message ─────────────────────────────
        tgt = PositionTarget()
        tgt.header.stamp    = now
        tgt.header.frame_id = 'map'
        tgt.coordinate_frame = PositionTarget.FRAME_LOCAL_NED
        tgt.type_mask = 0
        tgt.acceleration_or_force.x = acc_wx
        tgt.acceleration_or_force.y = acc_wy
        tgt.acceleration_or_force.z = acc_wz
        tgt.yaw = self.target_yaw

        self.cmd_acc_pub.publish(tgt)


if __name__ == '__main__':
    try:
        bridge = AttitudeBridge()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
