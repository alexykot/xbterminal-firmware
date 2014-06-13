#!/bin/sh
echo '40' > /sys/class/backlight/backlight.11/brightness
xinit /opt/xbterminal/bootstrap.so >> /opt/xbterminal/xbterminal/runtime/firmware_console.log 2>&1 
