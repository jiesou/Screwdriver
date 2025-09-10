#!/bin/bash

sudo apt update
sudo apt install libgirepository1.0-dev libcairo2-dev python3-gi python3-gi-cairo gir1.2-gtk-3.0 libdbus-1-dev python3-dbus libgl1-mesa-glx -y
sudo apt install freeglut3-dev -y # fix ImportError: libEGL.so.1
# For X11: sudo apt install libxcb-cursor0 libxcb-xinerama0 libxcb-randr0 -y
pip3 install -r requirements.txt
export QT_QPA_PLATFORM=wayland-egl
export XDG_SESSION_TYPE=wayland