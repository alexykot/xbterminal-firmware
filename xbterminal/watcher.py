import os
import logging
import socket
import threading
import time

import requests
import psutil
import usb.core

import xbterminal
from xbterminal.blockchain import blockchain
from xbterminal.helpers import wireless

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
        self.system_stats_timestamp = 0

    @property
    def wifi(self):
        return self._wifi

    @wifi.setter
    def wifi(self, interface_available):
        # TODO: add runtime['init']['wifi']
        if xbterminal.runtime['init']['internet']:
            if not interface_available:
                message = "wireless interface not found"
                if self.errors.get('wifi') != message:
                    self.messages.append((logging.ERROR, message))
                    self.errors['wifi'] = message
            else:
                if not self._wifi:
                    message = "wireless interface found"
                    self.messages.append((logging.INFO, message))
                self.errors.pop("wifi", None)
        self._wifi = interface_available

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
                message = "bitcoin server is not running"
                if self.errors.get('blockchain') != message:
                    self.messages.append((logging.ERROR, message))
                    self.errors['blockchain'] = message
                blockchain.updateDriverState(is_running=False)
            elif peers == 0:
                message = "bitcoin server - no peers"
                if self.errors.get('blockchain') != message:
                    self.messages.append((logging.ERROR, message))
                    self.errors['blockchain'] = message
            else:
                if not self._peers:
                    message = "bitcoin server is running ({0} peers)".format(peers)
                    self.messages.append((logging.INFO, message))
                self.errors.pop("blockchain", None)
                blockchain.updateDriverState(is_running=True)
        self._peers = peers

    def check_system_state(self):
        # Check wifi interface
        if not xbterminal.local_state.get('use_predefined_connection', False):
            self.wifi = (wireless.interface is not None
                and os.path.exists(os.path.join("/sys/class/net", wireless.interface)))
        # Check internet connection
        try:
            requests.get("http://google.com", timeout=3)
            self.internet = True
        except requests.exceptions.RequestException:
            self.internet = False
        # Check bitcoinj
        try:
            self.peers = int(blockchain.getInfo().get('connections'))
        except (
            requests.exceptions.RequestException,  # Bitcoinj network error
            socket.error,  # Bitcoind network error
            AttributeError,
            TypeError):
            self.peers = None

    def log_system_stats(self):
        logger = logging.getLogger("system_monitor")
        # http://www.usb.org/developers/defined_class
        wl_device = usb.core.find(bDeviceClass=0xE0)
        wl_product_id = wl_device.idProduct if wl_device else None
        stats = {
            'cpu': psutil.cpu_percent(interval=1),
            'memory': psutil.virtual_memory().percent,
            'disk': psutil.disk_usage("/").percent,
            'wireless': wl_product_id,
        }
        logger.info(str(stats))
        self.system_stats_timestamp = time.time()

    def get_data(self):
        with threading.RLock():
            messages, self.messages = self.messages, []
            errors = list(self.errors.values())
        return messages, errors

    def run(self):
        logger.info("watcher started")
        while True:
            self.check_system_state()
            if time.time() - self.system_stats_timestamp > 60:
                self.log_system_stats()
            time.sleep(self.period)
