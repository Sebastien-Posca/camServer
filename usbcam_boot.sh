#!/bin/bash

export LD_PRELOAD=/usr/lib/arm-linux-gnueabihf/libatomic.so.1.2.0 python3
cd /home/pi/camServer
python3 usbcam.py
cd /
