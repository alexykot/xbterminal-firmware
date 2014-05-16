import os
import logging
import threading
import time

import requests

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
            'wifi': False,
            'internet': False,
        }
        self.period = 2
        self.events = []

    @property
    def wifi(self):
        return self.state['wifi']

    @wifi.setter
    def wifi(self, value):
        if self.state['wifi'] and value is not True:
            self.events.append((logging.ERROR, "wifi disconnected"))
        if not self.state['wifi'] and value is True:
            self.events.append((logging.INFO, "wifi connected"))
        self.state['wifi'] = value

    @property
    def internet(self):
        return self.state['internet']

    @internet.setter
    def internet(self, value):
        if self.state['internet'] and value is not True:
            self.events.append((logging.ERROR, "internet disconnected"))
        if not self.state['internet'] and value is True:
            self.events.append((logging.INFO, "internet connected"))
        self.state['internet'] = value

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

