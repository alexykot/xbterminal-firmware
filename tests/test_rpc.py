from decimal import Decimal
import json
import unittest
from mock import patch, Mock

from tornado.testing import AsyncHTTPTestCase

from xbterminal.main_rpc import Application
from xbterminal.rpc import api, exceptions


class ApplicationTestCase(unittest.TestCase):

    @patch('xbterminal.main_rpc.logging.config.dictConfig')
    @patch('xbterminal.main_rpc.init_step_1')
    @patch('xbterminal.main_rpc.init_step_2')
    def test_init(self, init_2_mock, init_1_mock, log_conf_mock):
        Application()
        self.assertTrue(log_conf_mock.called)
        self.assertTrue(init_1_mock.called)
        self.assertTrue(init_2_mock.called)


class JSONRPCServerTestCase(AsyncHTTPTestCase):

    def get_app(self):
        with patch('xbterminal.main_rpc.logging.config.dictConfig'), \
                patch('xbterminal.main_rpc.init_step_1'), \
                patch('xbterminal.main_rpc.init_step_2'):
            return Application()

    @patch.dict(
        'xbterminal.rpc.api.state',
        payments={'test-uid': Mock(
            paid_btc_amount=Decimal('0.05'),
            status='new',
        )})
    def test_get_payment_status(self):
        payload = {
            'method': 'get_payment_status',
            'jsonrpc': '2.0',
            'params': {'uid': 'test-uid'},
            'id': 0,
        }
        headers = {'Content-Type': 'application/json'}
        response = self.fetch(
            '/',
            method='POST',
            body=json.dumps(payload),
            headers=headers)
        self.assertEqual(response.code, 200)
        result = json.loads(response.body)
        self.assertEqual(result['result'], {
            'paid_btc_amount': '0.05',
            'status': 'new',
        })

    @patch.dict(
        'xbterminal.rpc.api.state',
        payments={'test-uid': Mock(**{'check.side_effect': ValueError})})
    def test_get_payment_status_error(self):
        payload = {
            'method': 'get_payment_status',
            'jsonrpc': '2.0',
            'params': {'uid': 'test-uid'},
            'id': 0,
        }
        headers = {'Content-Type': 'application/json'}
        response = self.fetch(
            '/',
            method='POST',
            body=json.dumps(payload),
            headers=headers)
        self.assertEqual(response.code, 200)
        result = json.loads(response.body)
        self.assertIn('error', result)
        self.assertEqual(result['error']['message'], 'Server error')
        self.assertEqual(result['error']['code'], -32000)
        self.assertEqual(result['error']['data']['type'], 'ValueError')


class APITestCase(unittest.TestCase):

    def test_get_connection_status_online(self):
        state = {'watcher': Mock(internet=True)}
        with patch.dict('xbterminal.rpc.api.state', **state):
            result = api.get_connection_status()
        self.assertEqual(result, 'online')

    def test_get_connection_status_offline(self):
        state = {'watcher': Mock(internet=False)}
        with patch.dict('xbterminal.rpc.api.state', **state):
            result = api.get_connection_status()
        self.assertEqual(result, 'offline')

    def test_get_device_status(self):
        state = {'remote_config': {'status': 'active'}}
        with patch.dict('xbterminal.rpc.api.state', **state):
            result = api.get_device_status()
        self.assertEqual(result, 'active')

    def test_get_device_status_loading(self):
        with patch.dict('xbterminal.rpc.api.state'):
            result = api.get_device_status()
        self.assertEqual(result, 'loading')

    def test_get_activation_code(self):
        state = {'rpc_config': {'activation_code': 'test'}}
        with patch.dict('xbterminal.rpc.api.state', **state):
            result = api.get_activation_code()
        self.assertEqual(result, 'test')

    def test_get_activation_code_none(self):
        with patch.dict('xbterminal.rpc.api.state'):
            result = api.get_activation_code()
        self.assertIsNone(result)

    @patch('xbterminal.rpc.api.configs.load_remote_config')
    def test_get_device_config(self, load_mock):
        state = {'remote_server': 'https://xbterminal.io'}
        load_mock.return_value = {'language': {'code': 'en'}}
        with patch.dict('xbterminal.rpc.api.state', **state):
            result = api.get_device_config()
        self.assertEqual(result['language']['code'], 'en')
        self.assertEqual(result['remote_server'],
                         'https://xbterminal.io')

    @patch('xbterminal.rpc.api.Payment.create_order')
    def test_create_payment_order(self, create_order_mock):
        state = {
            'device_key': 'test-key',
            'bluetooth_server': Mock(mac_address='00:00:00:00:00:00'),
            'payments': {},
        }
        create_order_mock.return_value = order_mock = Mock(**{
            'uid': 'test-uid',
            'btc_amount': Decimal('0.25'),
            'exchange_rate': Decimal('10.0'),
            'payment_uri': 'test-uri',
        })
        with patch.dict('xbterminal.rpc.api.state', **state):
            result = api.create_payment_order(fiat_amount='1.25')
        call_args = create_order_mock.call_args[0]
        self.assertEqual(call_args[0], 'test-key')
        self.assertEqual(call_args[1], '1.25')
        self.assertEqual(call_args[2], '00:00:00:00:00:00')
        self.assertEqual(state['payments']['test-uid'], order_mock)
        self.assertEqual(result['uid'], 'test-uid')
        self.assertEqual(result['btc_amount'], '0.25')
        self.assertEqual(result['exchange_rate'], '10.0')
        self.assertEqual(result['payment_uri'], 'test-uri')

    def test_get_payment_status(self):
        order_mock = Mock(paid_btc_amount=Decimal('0.5'), status='new')
        state = {
            'payments': {
                'test-uid': order_mock,
            },
        }
        with patch.dict('xbterminal.rpc.api.state', **state):
            result = api.get_payment_status(uid='test-uid')
        self.assertEqual(result['status'], 'new')
        self.assertEqual(result['paid_btc_amount'], '0.5')
        self.assertTrue(order_mock.check.called)

    def test_get_payment_status_not_found(self):
        state = {'payments': {}}
        with patch.dict('xbterminal.rpc.api.state', **state):
            with self.assertRaises(exceptions.OrderNotFound):
                api.get_payment_status(uid='test-uid')

    def test_cancel_payment(self):
        state = {
            'payments': {
                'test-uid': Mock(**{'cancel.return_value': True}),
            },
        }
        with patch.dict('xbterminal.rpc.api.state', **state):
            result = api.cancel_payment(uid='test-uid')
        self.assertTrue(result)

    def test_get_payment_receipt(self):
        state = {
            'payments': {
                'test-uid': Mock(receipt_url='test-url'),
            },
        }
        with patch.dict('xbterminal.rpc.api.state', **state):
            result = api.get_payment_receipt(uid='test-uid')
        self.assertEqual(result, 'test-url')

    @patch('xbterminal.rpc.api.Withdrawal.create_order')
    def test_create_withdrawal_order(self, create_order_mock):
        state = {
            'device_key': 'test-key',
            'withdrawals': {},
        }
        create_order_mock.return_value = order_mock = Mock(**{
            'uid': 'test-uid',
            'btc_amount': Decimal('0.25'),
            'tx_fee_btc_amount': Decimal('0.0001'),
            'exchange_rate': Decimal('10.0'),
            'status': 'new',
        })
        with patch.dict('xbterminal.rpc.api.state', **state):
            result = api.create_withdrawal_order(fiat_amount='1.25')
        call_args = create_order_mock.call_args[0]
        self.assertEqual(call_args[0], 'test-key')
        self.assertEqual(call_args[1], '1.25')
        self.assertEqual(state['withdrawals']['test-uid'], order_mock)
        self.assertEqual(result['uid'], 'test-uid')
        self.assertEqual(result['btc_amount'], '0.25')
        self.assertEqual(result['tx_fee_btc_amount'], '0.0001')
        self.assertEqual(result['exchange_rate'], '10.0')

    def test_confirm_withdrawal(self):
        order_mock = Mock(btc_amount=Decimal('0.2'),
                          exchange_rate=Decimal('200'))
        state = {
            'withdrawals': {
                'test-uid': order_mock,
            },
        }
        with patch.dict('xbterminal.rpc.api.state', **state):
            result = api.confirm_withdrawal(
                uid='test-uid', address='test-address')
        self.assertEqual(order_mock.confirm.call_args[0][0],
                         'test-address')
        self.assertEqual(result['btc_amount'], '0.2')
        self.assertEqual(result['exchange_rate'], '200')

    def test_get_withdrawal_status(self):
        order_mock = Mock(status='new')
        state = {
            'withdrawals': {
                'test-uid': order_mock,
            },
        }
        with patch.dict('xbterminal.rpc.api.state', **state):
            result = api.get_withdrawal_status(uid='test-uid')
        self.assertEqual(result, 'new')
        self.assertTrue(order_mock.check.called)

    def test_get_withdrawal_status_not_found(self):
        state = {'withdrawals': {}}
        with patch.dict('xbterminal.rpc.api.state', **state):
            with self.assertRaises(exceptions.OrderNotFound):
                api.get_withdrawal_status(uid='test-uid')

    def test_cancel_withdrawal(self):
        state = {
            'withdrawals': {
                'test-uid': Mock(**{'cancel.return_value': True}),
            },
        }
        with patch.dict('xbterminal.rpc.api.state', **state):
            result = api.cancel_withdrawal(uid='test-uid')
        self.assertTrue(result)

    def test_get_withdrawal_receipt(self):
        state = {
            'withdrawals': {
                'test-uid': Mock(receipt_url='test-url'),
            },
        }
        with patch.dict('xbterminal.rpc.api.state', **state):
            result = api.get_withdrawal_receipt(uid='test-uid')
        self.assertEqual(result, 'test-url')

    def test_start_bluetooth_server(self):
        bt_server_mock = Mock()
        order_mock = Mock()
        state = {
            'bluetooth_server': bt_server_mock,
            'payments': {
                'test-uid': order_mock,
            },
        }
        with patch.dict('xbterminal.rpc.api.state', **state):
            result = api.start_bluetooth_server(payment_uid='test-uid')
        self.assertTrue(result)
        self.assertEqual(bt_server_mock.start.call_args[0][0], order_mock)

    def test_start_bluetooth_server_payment_not_found(self):
        state = {
            'bluetooth_server': Mock(),
            'payments': {},
        }
        with patch.dict('xbterminal.rpc.api.state', **state):
            with self.assertRaises(exceptions.OrderNotFound):
                api.start_bluetooth_server(payment_uid='test-uid')

    def test_stop_bluetooth_server(self):
        bt_server_mock = Mock()
        state = {'bluetooth_server': bt_server_mock}
        with patch.dict('xbterminal.rpc.api.state', **state):
            result = api.stop_bluetooth_server()
        self.assertTrue(result)
        self.assertTrue(bt_server_mock.stop.called)

    def test_start_nfc_server(self):
        bsp_mock = Mock()
        state = {'bsp_interface': bsp_mock}
        with patch.dict('xbterminal.rpc.api.state', **state):
            result = api.start_nfc_server(message='test')
        self.assertTrue(result)
        self.assertEqual(bsp_mock.write_ndef.call_args[0][0], 'test')

    def test_stop_nfc_server(self):
        bsp_mock = Mock()
        state = {'bsp_interface': bsp_mock}
        with patch.dict('xbterminal.rpc.api.state', **state):
            result = api.stop_nfc_server()
        self.assertTrue(result)
        self.assertTrue(bsp_mock.erase_ndef.called)

    def test_start_qr_scanner(self):
        qr_scanner_mock = Mock()
        state = {'qr_scanner': qr_scanner_mock}
        with patch.dict('xbterminal.rpc.api.state', **state):
            result = api.start_qr_scanner()
        self.assertTrue(result)
        self.assertTrue(qr_scanner_mock.start.called)

    def test_stop_qr_scanner(self):
        qr_scanner_mock = Mock()
        state = {'qr_scanner': qr_scanner_mock}
        with patch.dict('xbterminal.rpc.api.state', **state):
            result = api.stop_qr_scanner()
        self.assertTrue(result)
        self.assertTrue(qr_scanner_mock.stop.called)

    def test_get_scanned_address(self):
        address = '1PWVL1fW7Ysomg9rXNsS8ng5ZzURa2p9vE'
        qr_scanner_mock = Mock(**{
            'get_data.return_value': address,
        })
        state = {'qr_scanner': qr_scanner_mock}
        with patch.dict('xbterminal.rpc.api.state', **state):
            result = api.get_scanned_address()
        self.assertEqual(result, address)

    def test_enable_display(self):
        bsp_mock = Mock()
        state = {'bsp_interface': bsp_mock}
        with patch.dict('xbterminal.rpc.api.state', **state):
            result = api.enable_display()
        self.assertIs(result, True)
        self.assertIs(bsp_mock.enable_display.called, True)

    def test_disable_display(self):
        bsp_mock = Mock()
        state = {'bsp_interface': bsp_mock}
        with patch.dict('xbterminal.rpc.api.state', **state):
            result = api.disable_display()
        self.assertIs(result, True)
        self.assertIs(bsp_mock.disable_display.called, True)

    def test_host_add_credit(self):
        bsp_mock = Mock()
        state = {'bsp_interface': bsp_mock}
        with patch.dict('xbterminal.rpc.api.state', **state):
            result = api.host_add_credit(fiat_amount='0.5')
        self.assertTrue(result)
        self.assertEqual(bsp_mock.add_credit.call_args[0][0],
                         Decimal('0.5'))

    def test_host_get_payout(self):
        bsp_mock = Mock(**{'get_payout.return_value': Decimal('0.25')})
        state = {'bsp_interface': bsp_mock}
        with patch.dict('xbterminal.rpc.api.state', **state):
            result = api.host_get_payout()
        self.assertEqual(result, '0.25')

    def test_host_get_payout_none(self):
        bsp_mock = Mock(**{'get_payout.return_value': None})
        state = {'bsp_interface': bsp_mock}
        with patch.dict('xbterminal.rpc.api.state', **state):
            result = api.host_get_payout()
        self.assertIsNone(result)

    def test_host_pay_cash(self):
        bsp_mock = Mock()
        state = {'bsp_interface': bsp_mock}
        with patch.dict('xbterminal.rpc.api.state', **state):
            result = api.host_pay_cash(fiat_amount='0.5')
        self.assertTrue(result)
        self.assertEqual(bsp_mock.pay_cash.call_args[0][0],
                         Decimal('0.5'))
