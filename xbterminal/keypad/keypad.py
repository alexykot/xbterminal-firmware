# -*- coding: utf-8 -*-
import time


_button_last_pressed = None
_cycle_index = -1
_alphanum_char_index = 0
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

class keypad():
    def __init__(self):
        from xbterminal.keypad.drivers import keypadDriverBBB
        self.driver = keypadDriverBBB()

    def getKey(self):
        return self.driver.getKey()

    #this allows to use numeric keypad to enter digits, upper and lower letters and special chars
    def toAlphaNum(self, button_pressed):
        global _button_last_pressed, _cycle_index, _buttons_to_chars

        if button_pressed not in _buttons_to_chars:
            _button_last_pressed = button_pressed
            return button_pressed

        if button_pressed != _button_last_pressed or _cycle_index+1 == len(_buttons_to_chars[button_pressed]):
            _cycle_index = -1

        _cycle_index = _cycle_index + 1
        _button_last_pressed = button_pressed

        return _buttons_to_chars[button_pressed][_cycle_index]

    def createAlphaNumString(self, current_string, button_pressed):
        global _alphanum_char_index, _cycle_index, _button_last_pressed

        if button_pressed == 'enter':
            _alphanum_char_index = _alphanum_char_index + 1
            _button_last_pressed = button_pressed
            _cycle_index = -1
            return current_string

        if button_pressed == 'backspace':
            current_string = current_string[:-1]
            if _cycle_index == -1:
                _alphanum_char_index = max(_alphanum_char_index - 1, 0)
            _button_last_pressed = button_pressed
            _cycle_index = -1
            return current_string

        if button_pressed in ('escape', 'qr_code'):
            return current_string

        new_char = self.toAlphaNum(button_pressed)
        new_string = current_string[0:_alphanum_char_index] + new_char

        return new_string


    def getCharSelectorTupl(self, button_pressed):
        global _buttons_to_chars

        try:
            return _buttons_to_chars[button_pressed]
        except KeyError:
            return None

    def checkIsDone(self, button_pressed):
        global _button_last_pressed

        if button_pressed == 'enter' and _button_last_pressed == 'enter':
            return True

        return False

    def checkIsCancelled(self, current_string, button_pressed):
        if button_pressed == 'backspace' and current_string == '':
            return True

        return False
