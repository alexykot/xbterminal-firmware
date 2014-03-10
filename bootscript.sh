#!/bin/sh
sleep 5
xinit /opt/xbterminal/bootstrap.py > /opt/xbterminal/xbterminal/runtime/console.log 2> /opt/xbterminal/xbterminal/runtime/console.error.log
sleep 5
xset -display :0 dpms 0 0 0 #(disable all modes, standy, suspend, off)
xset -display :0 -dpms
xset -display :0 s off
xset -display :0 s noblank
