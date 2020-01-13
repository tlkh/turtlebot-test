#!/bin/bash

echo "Set Jetson to Max Clocks"

jetson_clocks

echo "Clear RAM"

sync; echo 3 > /proc/sys/vm/drop_caches
