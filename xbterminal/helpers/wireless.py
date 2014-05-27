"""
https://wifi.readthedocs.org/en/latest/
"""
import os
import logging
import hashlib
import errno

import wifi
import wifi.scan
import wifi.utils
import wifi.exceptions

logger = logging.getLogger(__name__)


def find_wireless_interface():
    interfaces = os.listdir("/sys/class/net/")
    for interface in sorted(interfaces):
        if interface.startswith('wlan'):
            return interface
    return None

interface = find_wireless_interface()


def is_wifi_available():
    if interface is None:
        return False
    try:
        cell_list = wifi.scan.Cell.all(interface)
        if len(cell_list) > 0:
            return True
    except wifi.exceptions.InterfaceError as error:
        logger.exception(error)
    except OSError as error:
        if error.errno == errno.ENOENT:
            # [Errno 2] No such file or directory
            logger.error("iwlist not installed")
        else:
            raise
    return False

def discover_networks():
    networks = []
    try:
        cell_list = wifi.scan.Cell.all(interface)
    except wifi.exceptions.InterfaceError as error:
        logger.exception(error)
        return networks
    for cell in cell_list:
        networks.append({'ssid': cell.ssid,
                         'encrypted': cell.encrypted,
                         'encryption': cell.encryption_type if cell.encrypted else None,
                         })
    return networks

def connect(ssid, passkey=None):
    cell_list = wifi.scan.Cell.all(interface)
    for cell in cell_list:
        if cell.ssid == ssid:
            scheme_name = hashlib.sha256('{}_{}'.format(ssid, passkey)).hexdigest()
            scheme = wifi.Scheme.find(interface, scheme_name)
            if scheme is None:
                scheme = wifi.Scheme.for_cell(interface, scheme_name, cell, passkey=passkey)
                scheme.save()
            try:
                scheme.activate()
                return True
            except wifi.exceptions.ConnectionError as error:
                logger.exception(error)
                return False
