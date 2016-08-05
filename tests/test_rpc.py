from decimal import Decimal
import json
import unittest
from mock import patch, Mock

from tornado.testing import AsyncHTTPTestCase

from xbterminal.main_rpc import Application
from xbterminal import api
from xbterminal.api_client import JSONRPCClient


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
        'xbterminal.api.state',
        payments={'test-uid': Mock(**{'check.return_value': 'new'})})
    def test_check_payment_order(self):
        payload = {
            'method': 'check_payment_order',
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
        self.assertEqual(result['result']['status'], 'new')

    @patch.dict(
        'xbterminal.api.state',
        payments={'test-uid': Mock(**{'check.side_effect': ValueError})})
    def test_check_payment_order_error(self):
        payload = {
            'method': 'check_payment_order',
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
        with patch.dict('xbterminal.api.state', **state):
            result = api.get_connection_status()
        self.assertEqual(result['status'], 'online')

    def test_get_connection_status_offline(self):
        state = {'watcher': Mock(internet=False)}
        with patch.dict('xbterminal.api.state', **state):
            result = api.get_connection_status()
        self.assertEqual(result['status'], 'offline')

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

    @patch('xbterminal.api.configs.load_remote_config')
    def test_get_device_config(self, load_mock):
        state = {'remote_server': 'https://xbterminal.io'}
        load_mock.return_value = {'language': {'code': 'en'}}
        with patch.dict('xbterminal.api.state', **state):
            result = api.get_device_config()
        self.assertEqual(result['language']['code'], 'en')
        self.assertEqual(result['remote_server'],
                         'https://xbterminal.io')

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

    def test_get_payment_receipt(self):
        state = {
            'payments': {
                'test-uid': Mock(receipt_url='test-url'),
            },
        }
        with patch.dict('xbterminal.api.state', **state):
            result = api.get_payment_receipt(uid='test-uid')
        self.assertEqual(result['receipt_url'], 'test-url')

    @patch('xbterminal.api.Withdrawal.create_order')
    def test_create_withdrawal_order(self, create_order_mock):
        state = {
            'device_key': 'test-key',
            'withdrawals': {},
        }
        create_order_mock.return_value = order_mock = Mock(**{
            'uid': 'test-uid',
            'btc_amount': Decimal('0.25'),
            'exchange_rate': Decimal('10.0'),
        })
        with patch.dict('xbterminal.api.state', **state):
            result = api.create_withdrawal_order(fiat_amount='1.25')
        call_args = create_order_mock.call_args[0]
        self.assertEqual(call_args[0], 'test-key')
        self.assertEqual(call_args[1], '1.25')
        self.assertEqual(state['withdrawals']['test-uid'], order_mock)
        self.assertEqual(result['uid'], 'test-uid')
        self.assertEqual(result['btc_amount'], '0.25')
        self.assertEqual(result['exchange_rate'], '10.0')

    def test_confirm_withdrawal_order(self):
        order_mock = Mock(btc_amount=Decimal('0.2'),
                          exchange_rate=Decimal('200'))
        state = {
            'withdrawals': {
                'test-uid': order_mock,
            },
        }
        with patch.dict('xbterminal.api.state', **state):
            result = api.confirm_withdrawal_order(
                uid='test-uid', address='test-address')
        self.assertEqual(order_mock.confirm.call_args[0][0],
                         'test-address')
        self.assertEqual(result['btc_amount'], '0.2')
        self.assertEqual(result['exchange_rate'], '200')

    def test_check_withdrawal_order(self):
        state = {
            'withdrawals': {
                'test-uid': Mock(**{'check.return_value': 'new'}),
            },
        }
        with patch.dict('xbterminal.api.state', **state):
            result = api.check_withdrawal_order(uid='test-uid')
        self.assertEqual(result['status'], 'new')

    def test_cancel_withdrawal_order(self):
        state = {
            'withdrawals': {
                'test-uid': Mock(**{'cancel.return_value': True}),
            },
        }
        with patch.dict('xbterminal.api.state', **state):
            result = api.cancel_withdrawal_order(uid='test-uid')
        self.assertTrue(result['result'])

    def test_get_withdrawal_receipt(self):
        state = {
            'withdrawals': {
                'test-uid': Mock(receipt_url='test-url'),
            },
        }
        with patch.dict('xbterminal.api.state', **state):
            result = api.get_withdrawal_receipt(uid='test-uid')
        self.assertEqual(result['receipt_url'], 'test-url')


class JSONRPCClientTestCase(unittest.TestCase):

    @patch('xbterminal.api_client.requests.post')
    def test_get_connection_status(self, post_mock):
        post_mock.return_value = Mock(**{
            'json.return_value': {
                'jsonrpc': '2.0',
                'result': {'status': 'online'},
                'id': 0,
            },
        })
        cli = JSONRPCClient()
        result = cli.get_connection_status()
        self.assertEqual(result['status'], 'online')
        self.assertEqual(post_mock.call_args[0][0], 'http://127.0.0.1:8888/')
        data = post_mock.call_args[1]['json']
        self.assertEqual(data['method'], 'get_connection_status')
        self.assertEqual(data['params'], {})
        self.assertEqual(data['jsonrpc'], '2.0')
        self.assertEqual(data['id'], 0)
        headers = post_mock.call_args[1]['headers']
        self.assertEqual(headers['content-type'], 'application/json')
