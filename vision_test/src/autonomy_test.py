#!/usr/bin/env python3
"""
autonomy_test.py
----------------
Project 2176 — МИЭМ НИУ ВШЭ
Тест автономного полёта: взлёт → облёт waypoints → посадка.

Топики (uav_simulator / p2176):
  /p2176/quadcopter/takeoff        std_msgs/Empty       — команда взлёта
  /p2176/quadcopter/land           std_msgs/Empty       — команда посадки
  /p2176/quadcopter/posctrl        std_msgs/Bool        — вкл/выкл позиционного контроля
  /p2176/quadcopter/setpoint_pose  geometry_msgs/PoseStamped — целевая точка
  /p2176/quadcopter/pose           geometry_msgs/PoseStamped — текущее положение (чтение)
"""

import math
import rospy
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Empty, Bool


# ---------------------------------------------------------------------------
# Параметры миссии
# ---------------------------------------------------------------------------

# Waypoints вида (x, y, z, label) — сцена corridor_navigation_test
# Дрон стартует у (0, 0, 0); коридор вытянут вдоль оси X
WAYPOINTS = [
    ( 0.0,  0.0,  2.0, "hover_start"),   # зависнуть над стартом
    ( 5.0,  0.0,  2.0, "forward_5m"),    # влететь в коридор
    (10.0,  0.0,  2.0, "mid_corridor"),  # середина коридора
    (10.0,  2.0,  2.0, "side_check"),    # проверить боковой манёвр
    (10.0,  0.0,  2.0, "back_center"),   # вернуться на ось
    ( 5.0,  0.0,  2.0, "return_5m"),     # лететь обратно
    ( 0.0,  0.0,  2.0, "home"),          # вернуться домой
]

POSITION_THRESHOLD = 0.5   # метров — считать точку достигнутой
WAYPOINT_TIMEOUT   = 20.0  # секунд — таймаут на каждую точку
TAKEOFF_WAIT       = 3.0   # секунд после команды взлёта
INIT_WAIT          = 5.0   # секунд ожидания старта симулятора
PUBLISH_RATE       = 20    # Гц — частота публикации setpoint_pose


# ---------------------------------------------------------------------------
# Класс миссии
# ---------------------------------------------------------------------------

class AutonomyTest:

    def __init__(self):
        rospy.init_node("autonomy_test", anonymous=False)

        # Публикаторы
        self.pub_takeoff  = rospy.Publisher("/p2176/quadcopter/takeoff",        Empty,        queue_size=1)
        self.pub_land     = rospy.Publisher("/p2176/quadcopter/land",           Empty,        queue_size=1)
        self.pub_posctrl  = rospy.Publisher("/p2176/quadcopter/posctrl",        Bool,         queue_size=1)
        self.pub_setpoint = rospy.Publisher("/p2176/quadcopter/setpoint_pose",  PoseStamped,  queue_size=1)

        # Подписчик: текущее положение
        self.current_pose = None
        rospy.Subscriber("/p2176/quadcopter/pose", PoseStamped, self._pose_cb)

        self.rate = rospy.Rate(PUBLISH_RATE)

    # ------------------------------------------------------------------
    def _pose_cb(self, msg: PoseStamped):
        self.current_pose = msg

    # ------------------------------------------------------------------
    def _dist_to(self, x: float, y: float, z: float) -> float:
        """Евклидово расстояние до целевой точки."""
        if self.current_pose is None:
            return float("inf")
        p = self.current_pose.pose.position
        return math.sqrt((p.x - x) ** 2 + (p.y - y) ** 2 + (p.z - z) ** 2)

    # ------------------------------------------------------------------
    def _fly_to(self, x: float, y: float, z: float, label: str = "") -> bool:
        """
        Публикует setpoint и ждёт достижения точки или таймаута.
        Возвращает True — достигнута, False — таймаут.
        """
        rospy.loginfo(f"[autonomy_test] → {label}  ({x:.1f}, {y:.1f}, {z:.1f})")

        msg = PoseStamped()
        msg.header.frame_id = "world"
        msg.pose.orientation.w = 1.0
        msg.pose.position.x = x
        msg.pose.position.y = y
        msg.pose.position.z = z

        t_start = rospy.Time.now()
        while not rospy.is_shutdown():
            msg.header.stamp = rospy.Time.now()
            self.pub_setpoint.publish(msg)

            dist = self._dist_to(x, y, z)
            if dist < POSITION_THRESHOLD:
                rospy.loginfo(f"[autonomy_test] ✓ {label}  (остаток {dist:.2f} м)")
                return True

            elapsed = (rospy.Time.now() - t_start).to_sec()
            if elapsed > WAYPOINT_TIMEOUT:
                rospy.logwarn(f"[autonomy_test] ✗ Таймаут {label}  (dist={dist:.2f} м)")
                return False

            self.rate.sleep()

        return False

    # ------------------------------------------------------------------
    def run(self):
        rospy.loginfo(f"[autonomy_test] Ожидание симулятора ({INIT_WAIT:.0f} с)...")
        rospy.sleep(INIT_WAIT)

        # --- Позиционный контроль ON ---
        rospy.loginfo("[autonomy_test] Включение позиционного контроля")
        self.pub_posctrl.publish(Bool(data=True))
        rospy.sleep(0.5)

        # --- Взлёт ---
        rospy.loginfo("[autonomy_test] Взлёт")
        self.pub_takeoff.publish(Empty())
        rospy.sleep(TAKEOFF_WAIT)

        # --- Миссия: облёт waypoints ---
        rospy.loginfo(f"[autonomy_test] Начало миссии: {len(WAYPOINTS)} точек")
        for (x, y, z, label) in WAYPOINTS:
            if rospy.is_shutdown():
                break
            self._fly_to(x, y, z, label)
            rospy.sleep(1.0)   # короткая пауза в каждой точке

        # --- Посадка ---
        rospy.loginfo("[autonomy_test] Посадка")
        self.pub_land.publish(Empty())
        rospy.loginfo("[autonomy_test] Миссия завершена")


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        AutonomyTest().run()
    except rospy.ROSInterruptException:
        pass
