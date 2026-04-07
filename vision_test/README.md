# vision_test — тестовый модуль автономного полёта
**Проект 2176 / МИЭМ НИУ ВШЭ / Исследовательский стенд моделирования БИС БПЛА**

Отдельный ROS-пакет для тестирования автономного управления квадрокоптером
в симуляторе `uav_simulator`. Не требует изменений в основном пакете.

---

## Структура пакета

```
vision_test/
├── CMakeLists.txt
├── package.xml
├── README.md
├── src/
│   ├── autonomy_test.py      # полная автономная миссия (waypoints)
│   └── waypoint_publisher.py # публикатор одной точки (для ручного теста)
└── launch/
    ├── autonomy_test.launch  # симулятор + автономная миссия
    └── waypoint_test.launch  # публикатор одного waypoint
```

---

## Зависимости

- ROS Melodic / Noetic  
- `uav_simulator` (пакет `base_simulator` из этого проекта)  
- Python 3  
- пакеты ROS: `rospy`, `std_msgs`, `geometry_msgs`, `nav_msgs`

---

## Сборка

Пакет написан на Python — **компиляция C++ не нужна**.  
`catkin_make` только регистрирует скрипты как исполняемые узлы.

```bash
# 1. Поместить оба пакета в src/ catkin-воркспейса
cd ~/catkin_ws/src
# base_simulator и vision_test должны лежать рядом:
#   catkin_ws/src/base_simulator/
#   catkin_ws/src/vision_test/

# 2. Собрать воркспейс
cd ~/catkin_ws
catkin_make

# 3. Применить окружение
source devel/setup.bash

# 4. (один раз) Убедиться, что скрипты исполняемые
chmod +x ~/catkin_ws/src/vision_test/src/autonomy_test.py
chmod +x ~/catkin_ws/src/vision_test/src/waypoint_publisher.py
```

> Если воркспейс собирается через `catkin build` (catkin_tools):
> ```bash
> catkin build vision_test
> source devel/setup.bash
> ```

---

## Запуск

### Вариант 1 — Полная автономная миссия (симулятор + тест одной командой)

```bash
roslaunch vision_test autonomy_test.launch
```

Что произойдёт:
1. Запустится Gazebo со сценой `corridor_navigation_test` (динамические препятствия)
2. Через 5 секунд стартует нода `autonomy_test`
3. Через ещё 5 секунд квадрокоптер взлетит и начнёт облёт waypoints:

```
(0, 0, 2) → (5, 0, 2) → (10, 0, 2) → (10, 2, 2) → (10, 0, 2) → (5, 0, 2) → (0, 0, 2) → посадка
```

### Вариант 2 — Тест одного waypoint

Симулятор уже запущен (`roslaunch uav_simulator start.launch`), нужно проверить одну точку:

```bash
# Взлететь вручную через keyboard_control, затем:
roslaunch vision_test waypoint_test.launch x:=5.0 y:=0.0 z:=2.0
```

### Вариант 3 — Запуск узла напрямую

```bash
# Симулятор уже запущен
rosrun vision_test autonomy_test.py
```

---

## Настройка миссии

Waypoints и параметры редактируются в начале файла [src/autonomy_test.py](src/autonomy_test.py):

```python
WAYPOINTS = [
    ( 0.0,  0.0,  2.0, "hover_start"),
    ( 5.0,  0.0,  2.0, "forward_5m"),
    ...
]

POSITION_THRESHOLD = 0.5   # метров — считать точку достигнутой
WAYPOINT_TIMEOUT   = 20.0  # секунд — таймаут на точку
```

---

## Используемые ROS-топики

| Топик | Тип | Направление |
|---|---|---|
| `/p2176/quadcopter/takeoff` | `std_msgs/Empty` | → симулятор |
| `/p2176/quadcopter/land` | `std_msgs/Empty` | → симулятор |
| `/p2176/quadcopter/posctrl` | `std_msgs/Bool` | → симулятор |
| `/p2176/quadcopter/setpoint_pose` | `geometry_msgs/PoseStamped` | → симулятор |
| `/p2176/quadcopter/pose` | `geometry_msgs/PoseStamped` | ← симулятор |
