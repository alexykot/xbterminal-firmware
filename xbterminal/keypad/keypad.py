# -*- coding: utf-8 -*-
import logging
import time

import xbterminal
from xbterminal.keypad import drivers

logger = logging.getLogger(__name__)

_buttons_to_chars = {1: ('1', '/', '%', '$', '&', '^', '*', '(', ')', '=', '-', '{', '}', '[', ']', ),
                    2: ('2', 'a', 'b', 'c', 'A', 'B', 'C', ),
                    3: ('3', 'd', 'e', 'f', 'D', 'E', 'F', ),
                    4: ('4', 'g', 'h', 'i', 'G', 'H', 'I', ),
                    5: ('5', 'j', 'k', 'l', 'J', 'K', 'L', ),
                    6: ('6', 'm', 'n', 'o', 'M', 'N', 'O', ),
                    7: ('7', 'p', 'q', 'r', 's', 'P', 'Q', 'R', 'S', ),
                    8: ('8', 't', 'u', 'v', 'T', 'U', 'V', ),
                    9: ('9', 'w', 'x', 'y', 'z', 'W', 'X', 'Y', 'Z', ),
                    0: ('0', '#', '!', '@', '.', ',', '\\', '~', '<', '>', '_', '+', ':', ';', ),
                    }


class Keypad():

    def __init__(self):
        if xbterminal.local_state.get("use_default_keypad_override"):
            self.driver = drivers.KeyboardDriver()
            logger.info("using standard keyboard driver")
        else:
            self.driver = drivers.KeypadDriverBBB()
        self._button_last_pressed = None
        self._cycle_index = -1
        self._alphanum_char_index = 0

    def getKey(self):
        key = self.driver.getKey()
        if key is not None:
            logger.debug('keypress {},'.format(key))

        return key

    #this allows to use numeric keypad to enter digits, upper and lower letters and special chars
    def toAlphaNum(self, button_pressed):
        if button_pressed not in _buttons_to_chars:
            self._button_last_pressed = button_pressed
            return button_pressed

        if (
            button_pressed != self._button_last_pressed
            or self._cycle_index + 1 == len(_buttons_to_chars[button_pressed])
        ):
            self._cycle_index = -1

        self._cycle_index += 1
        self._button_last_pressed = button_pressed

        return _buttons_to_chars[button_pressed][self._cycle_index]

    def createAlphaNumString(self, current_string, button_pressed):
        if button_pressed == 'enter':
            self._alphanum_char_index += 1
            self._button_last_pressed = button_pressed
            self._cycle_index = -1
            return current_string

        if button_pressed == 'backspace':
            current_string = current_string[:-1]
            if self._cycle_index == -1:
                self._alphanum_char_index = max(self._alphanum_char_index - 1, 0)
            self._button_last_pressed = button_pressed
            self._cycle_index = -1
            return current_string

        if button_pressed in ('escape', 'qr_code'):
            return current_string

        new_char = self.toAlphaNum(button_pressed)
        new_string = current_string[0:self._alphanum_char_index] + new_char

        return new_string

    def getCharSelectorTupl(self, button_pressed):
        try:
            return _buttons_to_chars[button_pressed]
        except KeyError:
            return None

    def checkIsDone(self, button_pressed):
        if button_pressed == 'enter' and self._button_last_pressed == 'enter':
            return True

        return False

    def checkIsCancelled(self, current_string, button_pressed):
        if button_pressed == 'backspace' and current_string == '':
            return True

        return False
