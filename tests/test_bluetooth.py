import binascii
import subprocess
import unittest
from mock import patch, Mock

from xbterminal.rpc.utils.bt import (
    BluetoothServer,
    BluetoothWorker,
    PaymentRequestWorker,
    PaymentResponseWorker)


class BluetoothServerTestCase(unittest.TestCase):

    def setUp(self):
        self.hciconfig_output = """
            hci0:
                Type: BR/EDR  Bus: USB
                BD Address: 11:22:33:44:55:66  ACL MTU: 310:10  SCO MTU: 64:8
                UP RUNNING PSCAN
                RX bytes:628 acl:0 sco:0 events:39 errors:0
                TX bytes:952 acl:0 sco:0 commands:38 errors:0
        """

    @patch('xbterminal.rpc.utils.bt.subprocess.check_output')
    @patch('xbterminal.rpc.utils.bt.subprocess.check_call')
    def test_init(self, check_call_mock, check_output_mock):
        check_output_mock.return_value = self.hciconfig_output
        bt_server = BluetoothServer()
        self.assertEqual(bt_server.device_id, 'hci0')
        self.assertEqual(bt_server.mac_address, '11:22:33:44:55:66')
        self.assertEqual(len(bt_server.workers), 0)
        self.assertEqual(check_call_mock.call_count, 2)
        args_1 = check_call_mock.call_args_list[0][0][0]
        self.assertEqual(args_1, ['hciconfig', 'hci0', 'sspmode', '0'])
        args_2 = check_call_mock.call_args_list[1][0][0]
        self.assertEqual(args_2, ['hciconfig', 'hci0', 'noauth'])

    @patch('xbterminal.rpc.utils.bt.subprocess.check_output')
    def test_init_proc_error(self, check_output_mock):
        check_output_mock.side_effect = subprocess.CalledProcessError(1, 2, 3)
        bt_server = BluetoothServer()
        self.assertIsNone(bt_server.device_id)
        self.assertIsNone(bt_server.mac_address)

    @patch('xbterminal.rpc.utils.bt.subprocess.check_output')
    @patch('xbterminal.rpc.utils.bt.subprocess.check_call')
    @patch('xbterminal.rpc.utils.bt.PaymentRequestWorker')
    @patch('xbterminal.rpc.utils.bt.PaymentResponseWorker')
    def test_start_stop(self, prsp_worker_cls_mock, preq_worker_cls_mock,
                        check_call_mock, check_output_mock):
        check_output_mock.return_value = self.hciconfig_output
        preq_worker_cls_mock.return_value = preq_worker_mock = Mock(**{
            'is_alive.return_value': True})
        prsp_worker_cls_mock.return_value = prsp_worker_mock = Mock(**{
            'is_alive.return_value': True})
        bt_server = BluetoothServer()
        # Start
        check_call_mock.reset_mock()
        bt_server.start('test')
        self.assertEqual(check_call_mock.call_count, 1)
        self.assertEqual(check_call_mock.call_args[0][0],
                         ['hciconfig', 'hci0', 'piscan'])
        self.assertEqual(len(bt_server.workers), 2)
        self.assertEqual(preq_worker_cls_mock.call_args[0][1], 'test')
        self.assertTrue(preq_worker_mock.start.called)
        self.assertEqual(prsp_worker_cls_mock.call_args[0][1], 'test')
        self.assertTrue(prsp_worker_mock.start.called)
        self.assertTrue(bt_server.is_running())
        # Stop
        check_call_mock.reset_mock()
        bt_server.stop()
        self.assertEqual(check_call_mock.call_count, 1)
        self.assertEqual(check_call_mock.call_args[0][0],
                         ['hciconfig', 'hci0', 'noscan'])
        self.assertEqual(len(bt_server.workers), 0)
        self.assertFalse(bt_server.is_running())

    @patch('xbterminal.rpc.utils.bt.subprocess.check_output')
    @patch('xbterminal.rpc.utils.bt.subprocess.check_call')
    def test_start_stop_no_device(self, check_call_mock, check_output_mock):
        check_output_mock.side_effect = subprocess.CalledProcessError(1, 2, 3)
        bt_server = BluetoothServer()
        # Start
        check_call_mock.reset_mock()
        bt_server.start('test')
        self.assertFalse(check_call_mock.called)
        self.assertEqual(len(bt_server.workers), 0)
        self.assertFalse(bt_server.is_running())
        # Stop
        check_call_mock.reset_mock()
        bt_server.stop()
        self.assertFalse(check_call_mock.called)
        self.assertEqual(len(bt_server.workers), 0)
        self.assertFalse(bt_server.is_running())


class BluetoothWorkerTestCase(unittest.TestCase):

    @patch('xbterminal.rpc.utils.bt.bluetooth.BluetoothSocket')
    @patch('xbterminal.rpc.utils.bt.dbus.SystemBus')
    @patch('xbterminal.rpc.utils.bt.dbus.Interface')
    @patch('xbterminal.rpc.utils.bt.create_sdp_record_xml')
    def test_init(self, create_sdp_rec_mock,
                  interface_cls_mock, system_bus_cls_mock,
                  bt_socket_cls_mock):
        bt_socket_cls_mock.return_value = Mock(**{
            'getsockname.return_value': ('00:00:00:00:00:00', 1),
        })
        bt_worker = BluetoothWorker('hci0', 'test')
        self.assertEqual(bt_worker.device_id, 'hci0')
        self.assertEqual(bt_worker.payment, 'test')
        self.assertIsNotNone(bt_worker.server_sock)
        self.assertIsNone(bt_worker.client_sock)
        self.assertTrue(create_sdp_rec_mock.called)

    @patch('xbterminal.rpc.utils.bt.bluetooth.BluetoothSocket')
    @patch('xbterminal.rpc.utils.bt.dbus.SystemBus')
    @patch('xbterminal.rpc.utils.bt.dbus.Interface')
    def test_payment_request(self, interface_cls_mock, system_bus_cls_mock,
                             bt_socket_cls_mock):
        bt_socket_cls_mock.return_value = Mock(**{
            'getsockname.return_value': ('00:00:00:00:00:00', 1),
        })
        payment_mock = Mock(**{
            'request': binascii.unhexlify('120b78'),
        })
        bt_worker = PaymentRequestWorker('hci0', payment_mock)
        bt_worker.client_sock = Mock()
        hello = binascii.unhexlify('00012f')
        bt_worker.handle_data(hello)
        self.assertTrue(bt_worker.client_sock.send.called)
        self.assertEqual(bt_worker.client_sock.send.call_args[0][0],
                         '\xc8\x01\x03\x12\x0bx')

    @patch('xbterminal.rpc.utils.bt.bluetooth.BluetoothSocket')
    @patch('xbterminal.rpc.utils.bt.dbus.SystemBus')
    @patch('xbterminal.rpc.utils.bt.dbus.Interface')
    def test_payment_response(self, interface_cls_mock, system_bus_cls_mock,
                              bt_socket_cls_mock):
        bt_socket_cls_mock.return_value = Mock(**{
            'getsockname.return_value': ('00:00:00:00:00:00', 1),
        })
        payment_mock = Mock(**{
            'send.return_value': binascii.unhexlify('0a8502'),
        })
        bt_worker = PaymentResponseWorker('hci0', payment_mock)
        bt_worker.client_sock = Mock()
        message = binascii.unhexlify('850212')
        bt_worker.handle_data(message)
        self.assertTrue(bt_worker.client_sock.send.called)
        self.assertEqual(bt_worker.client_sock.send.call_args[0][0],
                         '\x03\n\x85\x02')

    @patch('xbterminal.rpc.utils.bt.bluetooth.BluetoothSocket')
    @patch('xbterminal.rpc.utils.bt.dbus.SystemBus')
    @patch('xbterminal.rpc.utils.bt.dbus.Interface')
    def test_payment_response_error(self, interface_cls_mock,
                                    system_bus_cls_mock,
                                    bt_socket_cls_mock):
        bt_socket_cls_mock.return_value = Mock(**{
            'getsockname.return_value': ('00:00:00:00:00:00', 1),
        })
        payment_mock = Mock(**{
            'send.return_value': None,
        })
        bt_worker = PaymentResponseWorker('hci0', payment_mock)
        bt_worker.client_sock = Mock()
        message = binascii.unhexlify('850212')
        bt_worker.handle_data(message)
        self.assertFalse(bt_worker.client_sock.send.called)
