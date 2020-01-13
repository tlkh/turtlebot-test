#!/usr/bin/env sh

mkdir -p src
cd src

git clone https://github.com/turtlebot/turtlebot.git
git clone https://github.com/turtlebot/turtlebot_msgs.git
git clone https://github.com/turtlebot/turtlebot_apps.git
git clone https://github.com/turtlebot/turtlebot_simulator
git clone https://github.com/ros-perception/vision_opencv

git clone https://github.com/yujinrobot/kobuki_msgs.git
cd kobuki_msgs && git checkout release/0.7-melodic
cd ..
git clone https://github.com/yujinrobot/kobuki.git
cd kobuki && git checkout release/0.7-melodic
cd ..
mv kobuki/kobuki_description kobuki/kobuki_node \
  kobuki/kobuki_keyop kobuki/kobuki_safety_controller \
  kobuki/kobuki_bumper2pc ./
rm -rf kobuki

git clone https://github.com/yujinrobot/yujin_ocs.git
mv yujin_ocs/yocs_cmd_vel_mux yujin_ocs/yocs_controllers .
rm -rf yujin_ocs

sudo apt-get install -y ros-melodic-kobuki-* ros-melodic-ecl-streams ros-melodic-joy
