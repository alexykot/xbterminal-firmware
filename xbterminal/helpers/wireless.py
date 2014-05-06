"""
https://wifi.readthedocs.org/en/latest/
"""

import logging
import wifi
import wifi.scan
import wifi.utils
import wifi.exceptions
import hashlib
import errno

logger = logging.getLogger(__name__)


def is_wifi_available():
    try:
        cell_list = wifi.scan.Cell.all('wlan0')
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
        cell_list = wifi.scan.Cell.all('wlan0')
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
    cell_list = wifi.scan.Cell.all('wlan0')
    for cell in cell_list:
        if cell.ssid == ssid:
            scheme_name = hashlib.sha256('{}_{}'.format(ssid, passkey)).hexdigest()
            scheme = wifi.Scheme.find('wlan0', scheme_name)
            if scheme is None:
                scheme = wifi.Scheme.for_cell('wlan0', scheme_name, cell, passkey=passkey)
                scheme.save()
            try:
                scheme.activate()
                return True
            except wifi.exceptions.ConnectionError as error:
                logger.exception(error)
                return False

