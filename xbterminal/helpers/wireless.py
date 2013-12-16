import wifi
import wifi.scan
import wifi.utils


def is_wifi_available():
    try:
        cell_list = wifi.scan.Cell.all('wlan0')
        if len(cell_list) > 0:
            return True
    except wifi.utils.ScanFail:
        pass
    return False

def discover_networks():
    networks = []
    try:
        cell_list = wifi.scan.Cell.all('wlan0')
    except wifi.utils.ScanFail:
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
            scheme = wifi.Scheme.for_cell('wlan0', 'home', cell, passkey=passkey)
            try:
                scheme.activate()
                return True
            except wifi.utils.ConnectionFail:
                return False

