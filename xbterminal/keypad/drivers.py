# -*- coding: utf-8 -*-
from PyQt4 import QtCore

from xbterminal.state import gui_state as state


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
        QtCore.Qt.Key_Escape: 'application_halt',
    }

    def getKey(self):
        events = state['keyboard_events']
        try:
            key = events.pop()
        except IndexError:
            return None
        return self.key_map.get(key)
