import os
import logging
import threading
import time

import requests

import xbterminal
from xbterminal.blockchain import blockchain

logger = logging.getLogger(__name__)


class Watcher(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self._wifi = None
        self._internet = None
        self._peers = None
        self.period = 2
        self.messages = []
        self.errors = {}

    @property
    def wifi(self):
        return self._wifi

    @wifi.setter
    def wifi(self, wifi_connected):
        if xbterminal.runtime['init']['internet']:
            if self._wifi is None and not wifi_connected:
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
        if xbterminal.runtime['init']['internet']:
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

    @property
    def peers(self):
        return self._peers

    @peers.setter
    def peers(self, peers):
        if xbterminal.runtime['init']['blockchain']:
            if peers is None:
                self.messages.append((logging.ERROR, "bitcoin server is not running"))
                self.errors['blockchain'] = "bitcoin server is not running"
            elif peers == 0:
                self.messages.append((logging.ERROR, "bitcoin server - no peers"))
                self.errors['blockchain'] = "bitcoin server - no peers"
            else:
                if self._peers is None:
                    self.messages.append((logging.INFO, "bitcoin server is running ({0} peers)".format(peers)))
                self.errors.pop("blockchain", None)
        self._peers = peers

    def check_system_state(self):
        # Check wifi interface
        if not xbterminal.local_state.get('use_predefined_connection', False):
            self.wifi = os.path.exists("/sys/class/net/wlan0")
        # Check internet connection
        try:
            requests.get("http://google.com", timeout=3)
            self.internet = True
        except requests.exceptions.RequestException:
            self.internet = False
        # Check bitcoinj
        try:
            self.peers = int(blockchain.getInfo().get('connections'))
        except (requests.exceptions.RequestException, AttributeError):
            self.peers = None

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
