#!/bin/bash
echo '0' | sudo tee /sys/bus/usb/devices/usb1/authorized
sleep 2
echo '1' | sudo tee /sys/bus/usb/devices/usb1/authorized
sleep 2
echo 'on' | sudo tee /sys/bus/usb/devices/usb1/power/control
