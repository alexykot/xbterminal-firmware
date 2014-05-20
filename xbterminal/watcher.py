import os
import logging
import threading
import time

import requests

import xbterminal

logger = logging.getLogger(__name__)


class Watcher(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self._wifi = None
        self._internet = None
        self.period = 2
        self.messages = []
        self.errors = {}

    @property
    def wifi(self):
        return self._wifi

    @wifi.setter
    def wifi(self, wifi_connected):
        connection_override = xbterminal.local_state.get(
            'use_predefined_connection', False)
        if self._wifi is None and not wifi_connected:
            if connection_override:
                self.messages.append((logging.INFO, "wifi override"))
                self.errors.pop("wifi", None)
            else:
                self.messages.append((logging.ERROR, "no wifi"))
                self.errors["wifi"] = "no wifi"
        elif self._wifi and not wifi_connected:
            self.messages.append((logging.ERROR, "wifi disconnected"))
            self.errors["wifi"] = "wifi disconnected"
        elif not self._wifi and wifi_connected:
            self.messages.append((logging.INFO, "wifi connected"))
            self.errors.pop("wifi", None)
        self._wifi = wifi_connected

    @property
    def internet(self):
        return self._internet

    @internet.setter
    def internet(self, internet_connected):
        if self._internet is None and not internet_connected:
            self.messages.append((logging.ERROR, "no internet"))
            self.errors["internet"] = "no internet"
        elif self._internet and not internet_connected:
            self.messages.append((logging.ERROR, "internet disconnected"))
            self.errors["internet"] = "internet disconnected"
        elif not self._internet and internet_connected:
            self.messages.append((logging.INFO, "internet connected"))
            self.errors.pop("internet", None)
        self._internet = internet_connected

    def check_system_state(self):
        # Check wifi interface
        self.wifi = os.path.exists("/sys/class/net/wlan0")
        # Check internet connection
        try:
            requests.get("http://google.com", timeout=3)
            self.internet = True
        except requests.exceptions.RequestException:
            self.internet = False

    def get_data(self):
        with threading.RLock():
            messages, self.messages = self.messages, []
            errors = list(self.errors.values())
        return messages, errors

    def run(self):
        logger.info("watcher started")
        while True:
            self.check_system_state()
            time.sleep(self.period)

