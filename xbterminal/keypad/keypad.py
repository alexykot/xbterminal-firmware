# -*- coding: utf-8 -*-
import logging
import time

from xbterminal.keypad import drivers

logger = logging.getLogger(__name__)


class Keypad():

    _getkey_delay = 0.2

    def __init__(self):
        self.driver = drivers.KeyboardDriver()
        logger.info('using standard keyboard driver')

        self._getkey_value = None
        self._getkey_timestamp = 0

        self._cycle_index = None

    def getKey(self):
        current_timestamp = time.time()
        if current_timestamp - self._getkey_timestamp > self._getkey_delay:
            key = self.driver.getKey()
            if key is not None:
                logger.debug('keypress {0}'.format(key))
                self._getkey_value = key
                self._getkey_timestamp = current_timestamp

    def resetKey(self):
        self._getkey_value = None

    @property
    def last_key_pressed(self):
        return self._getkey_value

    @property
    def last_activity_timestamp(self):
        return self._getkey_timestamp
