import os
import logging
import threading
import time

import requests

import xbterminal

logger = logging.getLogger(__name__)


def get_state(watcher):
    with threading.RLock():
        state = watcher.state
        events = []
        while watcher.events:
            events.append(watcher.events.pop(0))
    return state, events


class Watcher(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.state = {
            'wifi': None,
            'internet': None,
        }
        self.period = 2
        self.events = []

    @property
    def wifi(self):
        return self.state['wifi']

    @wifi.setter
    def wifi(self, wifi_connected):
        connection_override = xbterminal.local_state.get(
            'use_predefined_connection', False)
        if (
            self.state['wifi'] is None
            and not connection_override
            and not wifi_connected
        ):
            self.events.append((logging.ERROR, "no wifi"))
        elif self.state['wifi'] and not wifi_connected:
            self.events.append((logging.ERROR, "wifi disconnected"))
        elif not self.state['wifi'] and wifi_connected:
            self.events.append((logging.INFO, "wifi connected"))
        self.state['wifi'] = wifi_connected

    @property
    def internet(self):
        return self.state['internet']

    @internet.setter
    def internet(self, internet_connected):
        if self.state['internet'] is None and not internet_connected:
            self.events.append((logging.ERROR, "no internet"))
        elif self.state['internet'] and not internet_connected:
            self.events.append((logging.ERROR, "internet disconnected"))
        elif not self.state['internet'] and internet_connected:
            self.events.append((logging.INFO, "internet connected"))
        self.state['internet'] = internet_connected

    def check_system_state(self):
        # Check wifi interface
        self.wifi = os.path.exists("/sys/class/net/wlan0")
        # Check internet connection
        try:
            requests.get("http://google.com", timeout=3)
            self.internet = True
        except requests.exceptions.RequestException:
            self.internet = False

    def run(self):
        logger.info("watcher started")
        while True:
            self.check_system_state()
            time.sleep(self.period)

