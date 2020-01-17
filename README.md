# Turtlebot Demo

## Usage

### 1. Start ROS Components

These are used to interface with and control the Turtlebot.

Open a new Terminal/SSH connection and run:

```shell
roslaunch turtlebot_bringup minimal.launch
```

This stats the ROS main core and initializes the Turtlebot. You should hear a startup tone.

**A. Keyboard Operation**

Open a new Terminal/SSH connection and run:

```shell
roslaunch turtlebot_teleop keyboard_teleop.launch
```

**B. Joystick Operation**

Open a new Terminal/SSH connection and run:

```shell
roslaunch turtlebot_teleop logitech.launch
```

### 2. Start Video Stream

Open a new Terminal/SSH connection and run:

```
# get IP address
ip a | grep inet

# start web server
python3 server.py
```

Navigate to your Jetson's IP address (port 5000) and you should see the video stream.

## Installation

1. Flash JetPack 4.3 onto Jetson device
2. Install ROS (https://www.jetsonhacks.com/2019/10/23/install-ros-on-jetson-nano/)
3. Run `install_turtlebot.sh` (TODO: fix OpenCV version)
4. TODO: joystick instructions
5. Install `jetson-inference` (https://github.com/dusty-nv/jetson-inference)
6. Install `requirements.txt`
7. Add `source ~/workspace/devel/setup.bash` to last line in `~/.bashrc`

## Useful commands

```shell
# running ROS stuff
source ~/workspace/devel/setup.bash
roslaunch turtlebot_bringup minimal.launch
roslaunch turtlebot_teleop keyboard_teleop.launch
roslaunch turtlebot_teleop logitech.launch

# joystick op
ls -l /dev/input/
sudo jstest /dev/input/js0
sudo chmod a+rw /dev/input/js0
rosparam set joy_node/dev "/dev/input/js0"
rosrun joy joy_node
rostopic echo joy
```

