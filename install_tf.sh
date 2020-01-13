#!/bin/bash

sudo pip3 install -U pip setuptools wheel

sudo pip3 install -U numpy grpcio h5py

sudo pip3 install -U absl-py py-cpuinfo psutil portpicker six mock requests gast astor termcolor protobuf keras-applications keras-preprocessing wrapt google-pasta

sudo pip3 install --pre --extra-index-url https://developer.download.nvidia.com/compute/redist/jp/v42 tensorflow-gpu==1.13.1

sudo ldconfig
