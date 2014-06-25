# -*- coding: utf-8 -*-
import logging
import time

import xbterminal
from xbterminal.keypad import drivers
from xbterminal.gui.gui import wake_up_screen

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

    _getkey_delay = 0.2
    _screensaver_delay = 300

    def __init__(self):
        if xbterminal.local_state.get("use_default_keypad_override"):
            self.driver = drivers.KeyboardDriver()
            logger.info("using standard keyboard driver")
        else:
            self.driver = drivers.KeypadDriverBBB()

        self._getkey_value = None
        self._getkey_timestamp = 0

        self._cycle_index = 0
        self._alphanum_char_index = 0
        self._alphanum_char_prev = None

    def getKey(self):
        current_timestamp = time.time()
        if current_timestamp - self._getkey_timestamp > self._getkey_delay:
            key = self.driver.getKey()
            if key is not None:
                logger.debug('keypress {0}'.format(key))
                self._getkey_value = key
                if current_timestamp - self._getkey_timestamp > self._screensaver_delay:
                    wake_up_screen()
                self._getkey_timestamp = current_timestamp

    def resetKey(self):
        self._getkey_value = None

    @property
    def last_key_pressed(self):
        return self._getkey_value

    @property
    def last_activity_timestamp(self):
        return self._getkey_timestamp

    def createAlphaNumString(self, current_string):
        if self._getkey_value in _buttons_to_chars:
            # Select character
            char_tuple = _buttons_to_chars[self._getkey_value]
            if (
                self._getkey_value != self._alphanum_char_prev
                or self._cycle_index == len(char_tuple) - 1
            ):
                # Start new cycle
                self._cycle_index = 0
            else:
                self._cycle_index += 1
            new_string = current_string[0:self._alphanum_char_index] + char_tuple[self._cycle_index]
            self._alphanum_char_prev = self._getkey_value
            return new_string
        elif self._getkey_value == 'enter':
            # Accept current character
            self._alphanum_char_index += 1
            self._cycle_index = 0
            self._alphanum_char_prev = self._getkey_value
            return current_string
        elif self._getkey_value == 'backspace':
            # Remove last character
            if self._cycle_index == 0:
                self._alphanum_char_index = max(self._alphanum_char_index - 1, 0)
            self._cycle_index = 0
            self._alphanum_char_prev = self._getkey_value
            return current_string[:-1]
        else:
            self._alphanum_char_prev = self._getkey_value
            return current_string

    def getCharSelectorTupl(self):
        try:
            return _buttons_to_chars[self._getkey_value]
        except KeyError:
            return None

    def checkIsDone(self):
        return self._getkey_value == 'enter' and self._alphanum_char_prev == 'enter'

    def checkIsCancelled(self, current_string):
        return self._getkey_value == 'backspace' and current_string == ''
