#!/usr/bin/python2.7
from nfc_test.matrix_keypad import RPi_GPIO

__author__ = 'tux'

import RPi.GPIO as GPIO
import time

kp = RPi_GPIO.keypad(columnCount=4)

# check if a key is pressed:
#checkKeypad = kp.getKey()

def key_detect():
    # Loop while waiting for a keypress
    digitPressed = None
    while digitPressed is None:
        digitPressed = kp.getKey()
        time.sleep(0.1)
    return digitPressed

GPIO.cleanup ()