#!/usr/bin/python2.7
__author__ = 'tux'

from matrix_keypad import RPi_GPIO
import RPi.GPIO as GPIO
import time

kp = RPi_GPIO.keypad(columnCount=4)

# check if a key is pressed:
checkKeypad = kp.getKey()

def key_detect():
    # Loop while waiting for a keypress
    digitPressed = None
    while digitPressed is None:
        digitPressed = kp.getKey()
        time.sleep(0.1)
    return digitPressed

while True:
    print key_detect()
    if checkKeypad is 1:
        print "Key pressed was 1"
    time.sleep(0.1)

GPIO.cleanup ()