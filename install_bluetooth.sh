#!/bin/bash

sudo apt update
sudo apt install libgirepository1.0-dev libcairo2-dev python3-gi python3-gi-cairo gir1.2-gtk-3.0 libdbus-1-dev python3-dbus libgl1-mesa-glx -y
pip3 install -r requirements.txt