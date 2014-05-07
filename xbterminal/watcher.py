import os
import logging
import threading
import time

import requests

logger = logging.getLogger(__name__)


class Watcher(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.state = {}
        self.period = 2

    def check_system_state(self):
        # Check wifi interface
        self.state['wifi'] = os.path.exists("/sys/class/net/wlan0")
        # Check internet connection
        try:
            requests.get("http://google.com", timeout=3)
            self.state['internet'] = True
        except requests.exceptions.RequestException:
            self.state['internet'] = False

    def run(self):
        logger.info("watcher started")
        while True:
            self.check_system_state()
            time.sleep(self.period)

