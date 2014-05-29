import os
import logging
import threading
import time

import requests
import psutil
import usb.core

import xbterminal
from xbterminal.blockchain import blockchain

logger = logging.getLogger(__name__)

# http://www.linux-usb.org/usb.ids
# (vendor id, product id, device name)
USB_DEVICES = {
    'bluetooth': [
        (0x0a5c, 0x21e8, 'BCM20702A0 Bluetooth 4.0'),
    ],
    'nfc': [
        (0x04e6, 0x5591, 'SCL3711-NFC&RW'),
    ],
    'wifi': [
        (0x148f, 0x5370, 'RT5370 Wireless Adapter'),
    ],
}


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
                message = "bitcoin server is not running"
                if self.errors.get('blockchain') != message:
                    self.messages.append((logging.ERROR, message))
                    self.errors['blockchain'] = message
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
        self._peers = peers

    def check_system_state(self):
        # Check wifi interface
        if not xbterminal.local_state.get('use_predefined_connection', False):
            self.wifi = os.path.exists("/sys/class/net/wlan0")
        # Check internet connection
        try:
            requests.get("https://xbterminal.com", timeout=5)
            self.internet = True
        except requests.exceptions.RequestException:
            self.internet = False
        # Check bitcoinj
        try:
            self.peers = int(blockchain.getInfo().get('connections'))
        except (
            requests.exceptions.RequestException,
            AttributeError,
            TypeError):
            self.peers = None

    def log_system_stats(self):
        logger = logging.getLogger("system_monitor")
        stats = {
            'cpu': psutil.cpu_percent(interval=1),
            'memory': psutil.virtual_memory().percent,
            'disk': psutil.disk_usage("/").percent,
        }
        for device_type, device_list in USB_DEVICES.items():
            stats[device_type] = None
            for vendor_id, product_id, device_name in device_list:
                device = usb.core.find(idVendor=vendor_id,
                                       idProduct=product_id)
                if device:
                    stats[device_type] = device_name
                    break
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
