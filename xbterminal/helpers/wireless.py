import logging
import wifi
import wifi.scan
import wifi.utils
import wifi.exceptions
import hashlib


def is_wifi_available():
    try:
        cell_list = wifi.scan.Cell.all('wlan0')
        if len(cell_list) > 0:
            return True
    except wifi.exceptions.InterfaceError as error:
        logging.exception(error)
    return False

def discover_networks():
    networks = []
    try:
        cell_list = wifi.scan.Cell.all('wlan0')
    except wifi.exceptions.InterfaceError as error:
        logging.exception(error)
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
                logging.exception(error)
                return False

