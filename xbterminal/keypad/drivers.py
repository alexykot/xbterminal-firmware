# -*- coding: utf-8 -*-
import logging

from PyQt4 import QtCore
import Adafruit_BBIO.GPIO as GPIO

import xbterminal

logger = logging.getLogger(__name__)


class KeypadDriverBBB():

    pins_set_up = False
    pins = {'pin1': "P8_14",
            'pin2': "P8_16",
            'pin3': "P8_11",
            'pin4': "P8_10",
            'pin5': "P8_7",
            'pin6': "P8_9",
            'pin7': "P8_26",
            'pin8': "P8_8",
            }

    KEY_MAP = {0: 0,
               1: 1,
               2: 2,
               3: 3,
               4: 4,
               5: 5,
               6: 6,
               7: 7,
               8: 8,
               9: 9,
               'A': 'backspace',
               'D': 'enter',
               '00': '00',
               '#BC': 'system_halt',
               }

    KEYPAD = {17: 1,
              18: 2,
              20: 3,
              49: 4,
              50: 5,
              52: 6,
              81: 7,
              82: 8,
              84: 9,
              146: 0,
              24: 'A',
              56: 'B',
              88: 'C',
              152: 'D',
              148: '00',
              145: '#',
              249: '#BC',
              }

    ROW = [pins['pin8'], pins['pin7'], pins['pin6'], pins['pin5']]
    COLUMN = [pins['pin4'], pins['pin3'], pins['pin2'], pins['pin1']]

    def getKey(self):
        key = None
        bits_list = [0, 0, 0, 0, 0, 0, 0, 0]

        if not self.pins_set_up:
            for j in range(len(self.COLUMN)):
                GPIO.setup(self.COLUMN[j], GPIO.OUT)

            for i in range(len(self.ROW)):
                GPIO.setup(self.ROW[i], GPIO.IN, GPIO.PUD_DOWN)

            for j in range(len(self.COLUMN)):
                GPIO.output(self.COLUMN[j], GPIO.LOW)

            self.pins_set_up = True

        # Scan rows for pushed key/button
        # A valid key press should set "rowVal"  between 0 and 3.
        rowVal = -1
        for i in range(len(self.ROW)):
            tmpRead = GPIO.input(self.ROW[i])
            if tmpRead == 0:
                rowVal = i
                bits_list[7 - i] = 1

        if rowVal in range(len(self.ROW)):
            for j in range(len(self.COLUMN)):
                GPIO.setup(self.COLUMN[j], GPIO.IN, GPIO.PUD_DOWN)

            GPIO.setup(self.ROW[rowVal], GPIO.OUT)
            GPIO.output(self.ROW[rowVal], GPIO.HIGH)

            # Scan columns for still-pushed key/button
            # A valid key press should set "colVal"  between 0 and 2.
            colVal = -1
            for j in range(len(self.COLUMN)):
                tmpRead = GPIO.input(self.COLUMN[j])
                if tmpRead == 1:
                    colVal = j
                    bits_list[3 - j] = 1

            if colVal in range(len(self.COLUMN)):
                for key, val in enumerate(bits_list):
                    bits_list[key] = str(val)
                binary_str = ''.join(bits_list)
                binary_str = '0b' + binary_str
                keynum = int(binary_str, 2)
                try:
                    key = self.KEY_MAP[self.KEYPAD[keynum]]
                except KeyError as error:
                    pass
                GPIO.cleanup()
                self.pins_set_up = False

        return key


class KeyboardDriver(object):

    key_map = {
        QtCore.Qt.Key_0: 0,
        QtCore.Qt.Key_1: 1,
        QtCore.Qt.Key_2: 2,
        QtCore.Qt.Key_3: 3,
        QtCore.Qt.Key_4: 4,
        QtCore.Qt.Key_5: 5,
        QtCore.Qt.Key_6: 6,
        QtCore.Qt.Key_7: 7,
        QtCore.Qt.Key_8: 8,
        QtCore.Qt.Key_9: 9,
        QtCore.Qt.Key_Backspace: 'backspace',
        QtCore.Qt.Key_Enter: 'enter',
        QtCore.Qt.Key_Return: 'enter',
        QtCore.Qt.Key_Alt: 'alt',
        QtCore.Qt.Key_Escape: 'system_halt',
    }

    def getKey(self):
        events = xbterminal.runtime['keyboard_events']
        try:
            key = events.pop()
        except IndexError:
            return None
        return self.key_map.get(key)
