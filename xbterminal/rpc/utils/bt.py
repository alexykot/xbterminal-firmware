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
import google.protobuf.internal.decoder as protobuf_decoder
import google.protobuf.internal.encoder as protobuf_encoder

logger = logging.getLogger(__name__)

# https://github.com/schildbach/bitcoin-wallet/blob/master/wallet/src/de/schildbach/wallet/util/Bluetooth.java
BLUETOOTH_SERVICE_UUIDS = {
    'Bitcoin payment requests': '3357A7BB-762D-464A-8D9A-DCA592D57D59',
    'Bitcoin payment protocol': '3357A7BB-762D-464A-8D9A-DCA592D57D5A',
    'Bitcoin classic': '3357A7BB-762D-464A-8D9A-DCA592D57D5B',
}

HCICONFIG_BIN = '/usr/sbin/hciconfig'

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


def create_sdp_record_xml(service_name, channel):
    """
    Create xml file for SDP record
    """
    record = xml_et.fromstring(SDP_RECORD_XML_TEMPLATE)  # nosec
    # 0x0001 - ServiceClassIDList
    sequence = record.find('./attribute[@id="0x0001"]/sequence')
    uuid = xml_et.SubElement(sequence, 'uuid')
    uuid.set('value', BLUETOOTH_SERVICE_UUIDS[service_name])
    # 0x0003 - ServiceID
    attribute = record.find('./attribute[@id="0x0003"]')
    uuid = xml_et.SubElement(attribute, 'uuid')
    uuid.set('value', BLUETOOTH_SERVICE_UUIDS[service_name])
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

    service_name = None

    _socket_backlog = 1
    _socket_timeout = 2

    def __init__(self, device_id, payment):
        super(BluetoothWorker, self).__init__()
        self.daemon = True
        self.device_id = device_id
        self.payment = payment
        self.server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.server_sock.bind(("", bluetooth.PORT_ANY))
        self.server_sock.listen(self._socket_backlog)
        self.client_sock = None
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
            self.server_sock.getsockname()[1])
        service.AddRecord(sdp_record_xml)

    def run(self):
        """
        Accept connections
        """
        logger.debug("{0} - waiting for connection".format(self.service_name))
        while True:
            if self._stop.is_set():
                break
            if self.client_sock is None:
                readable, _, _ = select.select([self.server_sock._sock],
                                               [], [],
                                               self._socket_timeout)
                if readable:
                    self.client_sock, client_info = self.server_sock.accept()
                    logger.debug("{0} - accepted connection from {1}".format(
                        self.service_name, client_info[0]))
                    self.client_sock.settimeout(self._socket_timeout)
            else:
                try:
                    data = self.client_sock.recv(4096)
                except IOError:
                    logger.debug("{0} - closing connection".format(self.service_name))
                    self.client_sock.close()
                    self.client_sock = None
                else:
                    self.handle_data(data)
        if self.client_sock:
            self.client_sock.close()
        self.server_sock.close()
        logger.debug("{0} - bluetooth worker stopped".format(self.service_name))

    def handle_data(self, data):
        """
        Override this method
        https://developers.google.com/protocol-buffers/docs/encoding
        """
        pass

    def stop(self):
        self._stop.set()


class PaymentRequestWorker(BluetoothWorker):

    service_name = 'Bitcoin payment requests'

    def handle_data(self, data):
        value, pos = protobuf_decoder._DecodeVarint(data, 0)
        value, pos = protobuf_decoder._DecodeVarint(data, pos)
        query, pos = protobuf_decoder.ReadTag(data, pos)
        logger.debug("{0} - query {1}".format(self.service_name, query))
        response_code = 200
        response = (protobuf_encoder._VarintBytes(response_code) +
                    protobuf_encoder._VarintBytes(len(self.payment.request)) +
                    self.payment.request)
        logger.debug("{0} - sending PaymentRequest".format(self.service_name))
        self.client_sock.send(response)


class PaymentResponseWorker(BluetoothWorker):

    service_name = 'Bitcoin payment protocol'

    def handle_data(self, data):
        """
        Process Payment message
        """
        logger.debug("{0} - recieved payment".format(self.service_name))
        value, pos = protobuf_decoder._DecodeVarint(data, 0)
        payment_message = data[pos:]
        payment_ack = self.payment.send(payment_message)
        if payment_ack:
            response = (protobuf_encoder._VarintBytes(len(payment_ack)) +
                        payment_ack)
            logger.debug('{0} - sending PaymentACK'.format(self.service_name))
            self.client_sock.send(response)
        else:
            logger.error('{0} - failed to send Payment to server'.format(
                self.service_name))


class BluetoothServer(object):

    def __init__(self):
        self.device_id = None
        self.mac_address = None
        self.workers = []
        # Read config
        try:
            hciconfig_result = subprocess.check_output([HCICONFIG_BIN])  # nosec
        except subprocess.CalledProcessError as error:
            logger.exception(error)
            return
        match = HCICONFIG_REGEX.search(hciconfig_result)
        if not match:
            logger.warning('bluetooth init failed')
            return
        self.device_id = match.group('device')
        self.mac_address = match.group('mac')
        # Disable SSP
        subprocess.check_call([  # nosec
            HCICONFIG_BIN,
            self.device_id,
            'sspmode', '0',
        ])
        # Disable auth
        subprocess.check_call([  # nosec
            HCICONFIG_BIN,
            self.device_id,
            'noauth',
        ])
        logger.info("bluetooth init done, mac address: {0}".format(self.mac_address))

    def make_discoverable(self):
        subprocess.check_call([  # nosec
            HCICONFIG_BIN,
            self.device_id,
            'piscan',
        ])

    def make_hidden(self):
        subprocess.check_call([  # nosec
            HCICONFIG_BIN,
            self.device_id,
            'noscan',
        ])

    def start(self, payment):
        if not self.device_id:
            # Do nothing if device is not available
            return
        self.make_discoverable()
        # Advertise services and accept connections
        self.workers = [
            PaymentRequestWorker(self.device_id, payment),
            PaymentResponseWorker(self.device_id, payment),
        ]
        for worker in self.workers:
            worker.start()

    def stop(self):
        if not self.device_id:
            # Do nothing if device is not available
            return
        # Stop workers
        for worker in self.workers:
            worker.stop()
            worker.join()
        del self.workers[:]
        self.make_hidden()

    def is_running(self):
        return any(w.is_alive() for w in self.workers)
