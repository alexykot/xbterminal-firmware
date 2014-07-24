import os
import logging
import socket
import threading
import time

import requests
import psutil
import usb.core

import xbterminal
from xbterminal import defaults
from xbterminal.helpers import wireless

logger = logging.getLogger(__name__)

# http://www.linux-usb.org/usb.ids
# (vendor id, product id, device name)
USB_DEVICES = {
    'bt': [
        (0x0a5c, 0x21e8, 'BCM20702A0 Bluetooth 4.0'),
    ],
    'nfc': [
        (0x04e6, 0x5591, 'SCL3711-NFC&RW'),
    ],
    'wifi': [
        (0x148f, 0x5370, 'RT5370 Wireless Adapter'),
        (0x0bda, 0x8172, 'Realtek Semiconductor Corp. RTL8191SU 802.11n WLAN Adapter'),
    ],
}


class Watcher(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self._wifi = None
        self._internet = None
        self.period = 2
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
                    logger.error(message)
                    self.errors['wifi'] = message
            else:
                if not self._wifi:
                    message = "wireless interface found"
                    logger.info(message)
                self.errors.pop("wifi", None)
        self._wifi = interface_available

    @property
    def internet(self):
        return self._internet

    @internet.setter
    def internet(self, internet_connected):
        if xbterminal.runtime['init']['internet']:
            if self._internet is None and not internet_connected:
                logger.error("no internet")
                self.errors["internet"] = "no internet"
            elif self._internet and not internet_connected:
                logger.error("internet disconnected")
                self.errors["internet"] = "internet disconnected"
            elif not self._internet and internet_connected:
                logger.info("internet connected")
                self.errors.pop("internet", None)
        self._internet = internet_connected

    def check_system_state(self):
        # Check wifi interface
        if not xbterminal.local_state.get('use_predefined_connection', False):
            self.wifi = (wireless.interface is not None
                and os.path.exists(os.path.join("/sys/class/net", wireless.interface)))
        # Check internet connection
        try:
            requests.get("https://xbterminal.com",
                         timeout=defaults.EXTERNAL_CALLS_TIMEOUT)
            self.internet = True
        except (requests.exceptions.RequestException, socket.timeout):
            self.internet = False

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

    def get_errors(self):
        with threading.RLock():
            errors = list(self.errors.values())
        return errors

    def set_error(self, error_type, error_message):
        with threading.RLock():
            if self.errors.get(error_type) != error_message:
                logger.error(error_message)
                self.errors[error_type] = error_message

    def discard_error(self, error_type):
        with threading.RLock():
            self.errors.pop(error_type, None)

    def run(self):
        logger.info("watcher started")
        while True:
            self.check_system_state()
            if time.time() - self.system_stats_timestamp > 60:
                self.log_system_stats()
            time.sleep(self.period)
