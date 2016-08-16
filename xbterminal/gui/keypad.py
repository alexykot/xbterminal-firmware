# -*- coding: utf-8 -*-
import logging
import time

from PyQt4 import QtCore

from xbterminal.gui.state import state

logger = logging.getLogger(__name__)


class Keypad():

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

    _getkey_delay = 0.2

    def __init__(self):
        logger.info('using standard keyboard driver')

        self._getkey_value = None
        self._getkey_timestamp = 0

        self._cycle_index = None

    def _get_key(self):
        events = state['keyboard_events']
        try:
            key_code = events.pop()
        except IndexError:
            return None
        return self.key_map.get(key_code)

    def get_key(self):
        current_timestamp = time.time()
        if current_timestamp - self._getkey_timestamp > self._getkey_delay:
            key = self._get_key()
            if key is not None:
                logger.debug('keypress {0}'.format(key))
                self._getkey_value = key
                self._getkey_timestamp = current_timestamp

    def reset_key(self):
        self._getkey_value = None

    @property
    def last_key_pressed(self):
        return self._getkey_value

    @property
    def last_activity_timestamp(self):
        return self._getkey_timestamp
