"""
Bluetooth server, build with PyBlueZ library:
    https://code.google.com/p/pybluez/wiki/Documentation
Disable pnat plugin in /etc/bluetooth/main.conf:
    DisablePlugins = pnat
"""
import logging
import re
import select
import subprocess
import threading
import xml.etree.ElementTree as xml_et

import bluetooth
import dbus

logger = logging.getLogger(__name__)

# https://github.com/schildbach/bitcoin-wallet/blob/master/wallet/src/de/schildbach/wallet/util/Bluetooth.java
BLUETOOTH_SERVICE_UUIDS = {
    'Bitcoin payment requests': '3357A7BB-762D-464A-8D9A-DCA592D57D59',
    'Bitcoin payment protocol': '3357A7BB-762D-464A-8D9A-DCA592D57D5A',
    'Bitcoin classic': '3357A7BB-762D-464A-8D9A-DCA592D57D5B',
}

HCICONFIG_REGEX = re.compile(
    r"""
    ^\s*(?P<device>hci[0-9]).+
    BD\s+Address:\s+(?P<mac>[0-9A-F:]{17})
    """,
    re.VERBOSE | re.IGNORECASE | re.DOTALL)

SDP_RECORD_XML_TEMPLATE = """
    <record>
        <attribute id="0x0001">
            <sequence></sequence>
        </attribute>
        <attribute id="0x0003"></attribute>
        <attribute id="0x0004">
            <sequence>
                <sequence><uuid value="0x0100" /></sequence>
                <sequence><uuid value="0x0003" /></sequence>
            </sequence>
        </attribute>
        <attribute id="0x0005">
            <sequence><uuid value="0x1002" /></sequence>
        </attribute>
        <attribute id="0x0100"></attribute>
    </record>
    """


def create_sdp_record_xml(service_name, service_id, channel):
    """
    Create xml file for SDP record
    """
    record = xml_et.fromstring(SDP_RECORD_XML_TEMPLATE)
    # 0x0001 - ServiceClassIDList
    sequence = record.find('./attribute[@id="0x0001"]/sequence')
    uuid = xml_et.SubElement(sequence, 'uuid')
    uuid.set('value', service_id)
    # 0x0003 - ServiceID
    attribute = record.find('./attribute[@id="0x0003"]')
    uuid = xml_et.SubElement(attribute, 'uuid')
    uuid.set('value', service_id)
    # 0x0004 - ProtocolDescriptorList
    sequence = record.find('./attribute[@id="0x0004"]/*/*/uuid[@value="0x0003"]/..')
    uint8 = xml_et.SubElement(sequence, 'uint8')
    uint8.set('value', hex(channel))
    # 0x0100 - ServiceName
    attribute = record.find('./attribute[@id="0x0100"]')
    text = xml_et.SubElement(attribute, 'text')
    text.set('value', service_name)
    # Return as string
    result = '<?xml version="1.0" encoding="utf-8" ?>\n'
    result += xml_et.tostring(record)
    return result


class BluetoothWorker(threading.Thread):

    _socket_backlog = 1
    _socket_timeout = 2

    def __init__(self, device_id, service_name):
        super(BluetoothWorker, self).__init__()
        self.device_id = device_id
        self.service_name = service_name
        self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.sock.bind(("", bluetooth.PORT_ANY))
        self.sock.listen(self._socket_backlog)
        self._stop = threading.Event()
        self.advertise_service()

    def advertise_service(self):
        """
        Create SDP record
        """
        # bluetooth.advertise_service - NOT WORKING
        # Create SDP record using BlueZ D-Bus API
        # https://android.googlesource.com/platform/external/bluetooth/bluez/+/master/doc/
        bus = dbus.SystemBus()
        manager = dbus.Interface(bus.get_object("org.bluez", "/"),
                                 "org.bluez.Manager")
        adapter_path = manager.FindAdapter(self.device_id)
        service = dbus.Interface(bus.get_object("org.bluez", adapter_path),
                                 "org.bluez.Service")
        sdp_record_xml = create_sdp_record_xml(
            self.service_name,
            BLUETOOTH_SERVICE_UUIDS[self.service_name],
            self.sock.getsockname()[1])
        service.AddRecord(sdp_record_xml)

    def run(self):
        """
        Accept connections
        """
        logger.debug("{0} - waiting for connection".format(self.service_name))
        client_sock = None
        while True:
            if self._stop.is_set():
                break
            if client_sock is None:
                readable, _, _ = select.select([self.sock._sock], [], [],
                                               self._socket_timeout)
                if readable:
                    client_sock, client_info = self.sock.accept()
                    logger.debug("{0} - accepted connection from {1}".\
                        format(self.service_name, client_info))
                    client_sock.settimeout(self._socket_timeout)
            else:
                try:
                    data = client_sock.recv(1024)
                    logger.debug(str(data))
                except IOError:
                    pass
        try:
            client_sock.close()
        except Exception:
            pass
        self.sock.close()
        logger.debug("{0} - bluetooth worker stopped".\
            format(self.service_name))

    def stop(self):
        self._stop.set()


class BluetoothServer(object):

    def __init__(self):
        hciconfig_result = subprocess.check_output(['hciconfig'])
        match = HCICONFIG_REGEX.search(hciconfig_result)
        self.device_id = match.group('device')
        self.mac_address = match.group('mac')
        self.workers = {}
        logger.info("bluetooth init done, mac address: {0}".\
            format(self.mac_address))

    def get_bluetooth_url(self):
        return 'bt:' + self.mac_address.replace(':', '')

    def start(self):
        # Make device visible
        subprocess.check_call(['hciconfig', self.device_id, 'piscan'])
        # Advertise services and accept connections
        for service_name in BLUETOOTH_SERVICE_UUIDS:
            worker = BluetoothWorker(self.device_id, service_name)
            worker.start()
            self.workers[service_name] = worker

    def stop(self):
        # Stop workers
        for service_name in BLUETOOTH_SERVICE_UUIDS:
            worker = self.workers.pop(service_name)
            worker.stop()
            worker.join()
        # Make device hidden
        subprocess.check_call(['hciconfig', self.device_id, 'noscan'])

    def is_running(self):
        return any(w.is_alive() for w in self.workers.values())
