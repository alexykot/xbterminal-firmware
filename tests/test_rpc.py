from decimal import Decimal
import json
import unittest
from mock import patch, Mock

from tornado.testing import AsyncHTTPTestCase

from xbterminal.main_rpc import Application
from xbterminal import api


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

    def test_echo(self):
        payload = {
            'method': 'echo',
            'jsonrpc': '2.0',
            'params': {'message': 'test'},
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
        self.assertEqual(result['result'], 'test')

    def test_echo_error(self):
        payload = {
            'method': 'echo',
            'jsonrpc': '2.0',
            'params': {},
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


class APITestCase(unittest.TestCase):

    def test_get_activation_status(self):
        state = {'remote_config': {'status': 'active'}}
        with patch.dict('xbterminal.api.state', **state):
            result = api.get_activation_status()
        self.assertEqual(result['status'], 'active')

    def test_get_activation_status_loading(self):
        with patch.dict('xbterminal.api.state'):
            result = api.get_activation_status()
        self.assertEqual(result['status'], 'loading')

    def test_get_activation_code(self):
        state = {'local_config': {'activation_code': 'test'}}
        with patch.dict('xbterminal.api.state', **state):
            result = api.get_activation_code()
        self.assertEqual(result['activation_code'], 'test')

    def test_get_activation_code_none(self):
        with patch.dict('xbterminal.api.state'):
            result = api.get_activation_code()
        self.assertIsNone(result['activation_code'])

    @patch('xbterminal.api.Payment.create_order')
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
        with patch.dict('xbterminal.api.state', **state):
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

    def test_check_payment_order(self):
        state = {
            'payments': {
                'test-uid': Mock(**{'check.return_value': 'new'}),
            },
        }
        with patch.dict('xbterminal.api.state', **state):
            result = api.check_payment_order(uid='test-uid')
        self.assertEqual(result['status'], 'new')

    def test_cancel_payment_order(self):
        state = {
            'payments': {
                'test-uid': Mock(**{'cancel.return_value': True}),
            },
        }
        with patch.dict('xbterminal.api.state', **state):
            result = api.cancel_payment_order(uid='test-uid')
        self.assertTrue(result['result'])

    def test_get_receipt_url(self):
        state = {
            'payments': {
                'test-uid': Mock(receipt_url='test-url'),
            },
        }
        with patch.dict('xbterminal.api.state', **state):
            result = api.get_payment_receipt(uid='test-uid')
        self.assertEqual(result['receipt_url'], 'test-url')
