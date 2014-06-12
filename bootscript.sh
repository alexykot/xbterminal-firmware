#!/bin/sh
echo '40' > /sys/class/backlight/backlight.11/brightness
xinit /opt/xbterminal/bootstrap.py >> /opt/xbterminal/xbterminal/runtime/firmware_console.system.log 2>> /opt/xbterminal/xbterminal/runtime/firmware_console.error.log
