#!/bin/sh
sleep 5
sudo xinit /home/debian/XBTerminal/gui.py
sleep 5
sudo xset -display :0 dpms 0 0 0 (disable all modes, standy, suspend, off)
sudo xset -display :0 -dpms
sudo xset -display :0 s off
sudo xset -display :0 s noblank
