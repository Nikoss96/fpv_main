# Lightweight Gazebo/ROS-based Simulator for Unmanned Aerial Vehicles (UAVs)
This package implements a lightweight quadcopter UAV simulator including various static and dynamic environments based on Gazebo/ROS. It also includes an optional PX4-based quadcopter simulation wrapper.

**Project 2176** — МИЭМ НИУ ВШЭ / Исследовательский стенд моделирования БИС БПЛА.

## I. Installation Guide
This repo has been tested on [ROS Melodic](http://wiki.ros.org/ROS/Installation) with Ubuntu 18.04 and [ROS Noetic](http://wiki.ros.org/ROS/Installation) with Ubuntu 20.04.
#### a. Non-PX4 Simulator (Required)
To install the non-PX4 simulator, please follow the standard catkin package make process as follows:
```
sudo apt-get install ros-[melodic/noetic]-mavros* # this package depends on mavros related ROS packages
git clone <repository_url>

cd ~/catkin_ws
catkin_make
```

setup environment variable. Add following to your ```~/.bashrc```
```
source path/to/uav_simulator/gazeboSetup.bash
```
#### b. PX4-based Simulator Wrapper (Optional but Recommended)
Please make sure that you have follow the previous steps to build the non-px4 simulator.

**Step 1**: Install vehicle models and make it compatible with your current ROS. The following lines give the summaries:

&#x1F34E; Current PX4 version has some problems with offboard mode, please use v1.12.0 as modified in the following lines:&#x1F34E;
```
cd directory/to/install # this should not be your catkin workspace

git clone https://github.com/PX4/PX4-Autopilot.git --recursive --branch v1.12.0
bash ./PX4-Autopilot/Tools/setup/ubuntu.sh # this step will ask you to reboot

# Please make sure you reboot after the previous step
cd /path/to/PX4-Autopilot
DONT_RUN=1 make px4_sitl_default gazebo
```
**Step 2**: Add the following script to ```~/.bashrc```. Remember to replace ```<PX4-Autopilot_clone>``` with the path to your PX4-Autopolot directory. This step will you setup the environment variables properly.
```
source <PX4-Autopilot_clone>/Tools/setup_gazebo.bash <PX4-Autopilot_clone> <PX4-Autopilot_clone>/build/px4_sitl_default
export ROS_PACKAGE_PATH=$ROS_PACKAGE_PATH:<PX4-Autopilot_clone>
export ROS_PACKAGE_PATH=$ROS_PACKAGE_PATH:<PX4-Autopilot_clone>/Tools/sitl_gazebo
```
**Step 3**: Install geographiclib datasets for PX4 simulation.
```
wget https://raw.githubusercontent.com/mavlink/mavros/master/mavros/scripts/install_geographiclib_datasets.sh
sudo bash ./install_geographiclib_datasets.sh  
```



## II. Quick Start
a. To launch the non-PX4 simulator with a quadcopter:
```
roslaunch uav_simulator start.launch
```

You should be able to see a customized quadcopter in a predefined Gazebo environment.


b. To launch the PX4 simulator with a quadcopter:
```
roslaunch uav_simulator px4_start.launch
```

You should be able to see a PX4 IRIS quadcopter in a predefined Gazebo environment.

## III. Keyboard Control
Our non-PX4 customized simulator supports the keyboard control function. You are able to control the quadcopter motion **When you click the keyboard controller panel**, you can control the quadcopter motion.


## IV. Simulation Environments
- There are various predefined environments in this package and you can easily switch environment when you modify the launch file located in ```uav_simululator/launch/start.launch``` or ```uav_simululator/launch/px4_start.launch```. All the predefined environments are listed in the launch files.
- There are some environments which contain dynamic objects (e.g. moving persons). You can distinguish those dynamic environments by the name suffix. For example, the environment name ```indoor_navigation_case_01_dynamic_16.world``` indicates that there are 16 dynamic objects in the indoor navigation case 01 environment.

One example of the dynamic environment is shown as below:



## V. ROS Topics
Here lists some important ROS topics related to the simulator:
- **Non-PX4 Simulator:**
  - ```/p2176/quadcopter/cmd_acc```: The command acceleration to the quadcopter.
  - ```/p2176/quadcopter/pose```: The ground truth pose of the quadcopter.
  - ```/p2176/quadcopter/odom```: The ground truth odom of the quadcopter.
  - ```/p2176/quadcopter/setpoint_pose```: The command pose to the quadcopter.
  - ```/camera/color/image_raw```: The color image from the onboard camera.
  - ```/camera/depth/image_raw```: The depth image from the onboard camera.
  - ```/camera/depth/points```: The depth cloud from the onboard camera.
- **PX4 Simulator**
  - ```/mavros/setpoint_raw/attitude```: The command to the quadcopter.
  - ```/mavros/local_position/pose```: The ground truth pose of the quadcopter.
  - ```/mavros/local_position/odom```: The ground truth odom of the quadcopter.
  - ```/mavros/setpoint_position/local```: The command pose to the quadcopter.
  - ```/camera/color/image_raw```: The color image from the onboard camera.
  - ```/camera/depth/image_raw```: The depth image from the onboard camera.
  - ```/camera/depth/points```: The depth cloud from the onboard camera.


