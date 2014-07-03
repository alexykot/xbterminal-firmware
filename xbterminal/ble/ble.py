"""
Attribute protocol (ATT):
    Bluetooth Core Spec v4.1, vol. 3, part F
Advertising:
    http://www.eetimes.com/document.asp?doc_id=1280724
"""
import binascii
import logging
import os
import re

from wrapper import Wrapper
import conv
import ad
import att

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)


class BLEServer(object):

    _hci_exec = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hci-ble")
    _l2cap_exec = os.path.join(os.path.dirname(os.path.abspath(__file__)), "l2cap-ble")

    def __init__(self):
        self._hci = Wrapper(self._hci_exec)
        self._l2cap = Wrapper(self._l2cap_exec)
        self._hci.start()
        self._l2cap.start()
        self.client_addr = None
        self._gatt_db = {}

    def listen(self):
        while True:
            if not self._l2cap.events.empty():
                line = self._l2cap.events.get()
                if line == "listen success":
                    logger.debug("listening...")
                elif line.startswith('accept'):
                    match = re.match("^accept (?P<addr>.*)$", line)
                    self.client_addr = match.group('addr')
                    logger.debug("accepted connection from {0}".\
                        format(self.client_addr))
                elif line.startswith('data'):
                    match = re.match("^data (?P<request>.*)$", line)
                    request = match.group('request')
                    logger.debug("recieved request {0}".format(request))
                    response = att.handle_request(request, self._gatt_db)
                    self._l2cap.inputs.put(response)
        self._hci.stop()
        self._l2cap_stop()

    def start_advertising(self, packet):
        adv_data = ad.encode_data(packet)
        scan_data = ad.encode_data(
            {'short_name': packet.get('short_name', 'serv')})
        self._start_advertising(adv_data, scan_data)

    def _start_advertising(self, adv_data, scan_data):
        #assert len(adv_data) <= 31
        #assert len(scan_data) <= 31
        data = "{0} {1}\n".format(
            binascii.hexlify(adv_data),
            binascii.hexlify(scan_data))
        logger.debug("start adv: {0}".format(data.strip()))
        self._hci.inputs.put(data)

    def set_services(self, services):
        self._gatt_db = att.set_services(services)


if __name__ == "__main__":
    server = BLEServer()
    advertisement = {
        'flags': [0x05],
        'incomplete_uuid_16': ['2A00','2A01'],
        'short_name': 'terminal',
    }
    service = {
        'uuid': 'fff0',
        'characteristics': [
            {'uuid': 'fff1', 'properties': [], 'secure': [], 'value': '', 'descriptors': []},
        ],
    }
    server.set_services([service])
    server.start_advertising(advertisement)
    server.listen()
