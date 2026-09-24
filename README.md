# VLA ROS 2

## Setup

have you setup realsense. For this project we update it to work with lyrical luth ros2. 
[Upgrade realsense depth camera to lyrical ros2](upgrade_realsense_cam.md)

```bash
source /opt/ros/lyrical/setup.bash
source ~/realsense_ws/install/setup.bash
source ~/perception_ws/install/setup.bash

```bash
source /opt/ros/lyrical/setup.bash
source ~/realsense_ws/install/setup.bash
source ~/vla-ros2/install/setup.bash
```

## Build

```bash
colcon build
source install/setup.bash
```

## Run

```bash
ros2 run vla_publisher vla_publisher
```
