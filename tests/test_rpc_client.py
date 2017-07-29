from decimal import Decimal
import unittest
from mock import patch, Mock

from xbterminal.gui import exceptions
from xbterminal.gui.rpc_client import JSONRPCClient


class JSONRPCClientTestCase(unittest.TestCase):

    @patch('xbterminal.gui.rpc_client.requests.post')
    def test_get_connection_status(self, post_mock):
        post_mock.return_value = Mock(**{
            'json.return_value': {
                'jsonrpc': '2.0',
                'result': 'online',
                'id': 0,
            },
        })
        cli = JSONRPCClient()
        result = cli.get_connection_status()
        self.assertEqual(result, 'online')
        self.assertEqual(post_mock.call_args[0][0], 'http://127.0.0.1:8888/')
        data = post_mock.call_args[1]['json']
        self.assertEqual(data['method'], 'get_connection_status')
        self.assertEqual(data['params'], {})
        self.assertEqual(data['jsonrpc'], '2.0')
        self.assertEqual(data['id'], 0)
        headers = post_mock.call_args[1]['headers']
        self.assertEqual(headers['content-type'], 'application/json')

    @patch('xbterminal.gui.rpc_client.requests.post')
    def test_network_error(self, post_mock):
        post_mock.return_value = Mock(**{
            'json.return_value': {
                'jsonrpc': '2.0',
                'error': {
                    'data': {
                        'type': 'NetworkError',
                        'args': [],
                    },
                },
                'id': 0,
            },
        })
        cli = JSONRPCClient()
        with self.assertRaises(exceptions.NetworkError):
            cli.get_payment_status(uid='test')

    @patch('xbterminal.gui.rpc_client.requests.post')
    def test_assertion_error(self, post_mock):
        post_mock.return_value = Mock(**{
            'json.return_value': {
                'jsonrpc': '2.0',
                'error': {'data': {'type': 'AssertionError'}},
                'id': 0,
            },
        })
        cli = JSONRPCClient()
        with self.assertRaises(Exception):
            cli.get_payment_status(uid='test')

    @patch('xbterminal.gui.rpc_client.requests.post')
    def test_create_payment_order(self, post_mock):
        post_mock.return_value = Mock(**{
            'json.return_value': {
                'jsonrpc': '2.0',
                'result': {
                    'uid': 'abc',
                    'btc_amount': '0.50000000',
                    'exchange_rate': '200.00000000',
                    'payment_uri': 'uri',
                },
                'id': 0,
            },
        })
        cli = JSONRPCClient()
        result = cli.create_payment_order(Decimal('10.00'))
        self.assertEqual(result['btc_amount'], Decimal('0.5'))
        self.assertEqual(result['exchange_rate'], Decimal('200.0'))
        data = post_mock.call_args[1]['json']
        self.assertEqual(data['method'], 'create_payment_order')
        self.assertEqual(data['params']['fiat_amount'], '10.00')

    @patch('xbterminal.gui.rpc_client.requests.post')
    def test_get_payment_status(self, post_mock):
        post_mock.return_value = Mock(**{
            'json.return_value': {
                'jsonrpc': '2.0',
                'result': {
                    'paid_btc_amount': '0.5',
                    'status': 'received',
                },
                'id': 0,
            },
        })
        cli = JSONRPCClient()
        result = cli.get_payment_status('test-uid')
        self.assertEqual(result['status'], 'received')
        self.assertEqual(result['paid_btc_amount'], Decimal('0.5'))
        data = post_mock.call_args[1]['json']
        self.assertEqual(data['method'], 'get_payment_status')

    @patch('xbterminal.gui.rpc_client.requests.post')
    def test_create_withdrawal_order(self, post_mock):
        post_mock.return_value = Mock(**{
            'json.return_value': {
                'jsonrpc': '2.0',
                'result': {
                    'uid': 'abc',
                    'btc_amount': '0.50000000',
                    'tx_fee_btc_amount': '0.0001000',
                    'exchange_rate': '200.00000000',
                },
                'id': 0,
            },
        })
        cli = JSONRPCClient()
        result = cli.create_withdrawal_order(Decimal('10.00'))
        self.assertEqual(result['btc_amount'], Decimal('0.5'))
        self.assertEqual(result['exchange_rate'], Decimal('200.0'))
        data = post_mock.call_args[1]['json']
        self.assertEqual(data['method'], 'create_withdrawal_order')
        self.assertEqual(data['params']['fiat_amount'], '10.00')

    @patch('xbterminal.gui.rpc_client.requests.post')
    def test_get_withdrawal_info(self, post_mock):
        post_mock.return_value = Mock(**{
            'json.return_value': {
                'jsonrpc': '2.0',
                'result': {
                    'uid': 'abcdef',
                    'fiat_amount': '100.00',
                    'btc_amount': '0.50000000',
                    'tx_fee_btc_amount': '0.0001000',
                    'exchange_rate': '200.00000000',
                    'status': 'new',
                },
                'id': 0,
            },
        })
        cli = JSONRPCClient()
        result = cli.get_withdrawal_info(uid='abcdef')
        self.assertEqual(result['uid'], 'abcdef')
        self.assertEqual(result['fiat_amount'], Decimal('100.00'))
        self.assertEqual(result['btc_amount'], Decimal('0.5'))
        self.assertEqual(result['tx_fee_btc_amount'], Decimal('0.0001'))
        self.assertEqual(result['exchange_rate'], Decimal('200.0'))
        self.assertEqual(result['status'], 'new')

    @patch('xbterminal.gui.rpc_client.requests.post')
    def test_confirm_withdrawal(self, post_mock):
        post_mock.return_value = Mock(**{
            'json.return_value': {
                'jsonrpc': '2.0',
                'result': {
                    'btc_amount': '0.50000000',
                    'exchange_rate': '200.00000000',
                },
                'id': 0,
            },
        })
        cli = JSONRPCClient()
        result = cli.confirm_withdrawal(1, 'address')
        self.assertEqual(result['btc_amount'], Decimal('0.5'))
        self.assertEqual(result['exchange_rate'], Decimal('200.0'))
        data = post_mock.call_args[1]['json']
        self.assertEqual(data['method'], 'confirm_withdrawal')

    @patch('xbterminal.gui.rpc_client.requests.post')
    def test_host_add_credit(self, post_mock):
        post_mock.return_value = Mock(**{
            'json.return_value': {
                'jsonrpc': '2.0',
                'result': True,
                'id': 0,
            },
        })
        cli = JSONRPCClient()
        result = cli.host_add_credit(Decimal('10.00'))
        self.assertEqual(result, True)
        data = post_mock.call_args[1]['json']
        self.assertEqual(data['method'], 'host_add_credit')
        self.assertEqual(data['params']['fiat_amount'], '10.00')

    @patch('xbterminal.gui.rpc_client.requests.post')
    @patch('xbterminal.gui.rpc_client.time.time')
    def test_host_get_payout_status(self, time_mock, post_mock):
        time_mock.side_effect = [1000, 0]  # Disable cache
        post_mock.return_value = Mock(**{
            'json.return_value': {
                'jsonrpc': '2.0',
                'result': 'idle',
                'id': 0,
            },
        })
        cli = JSONRPCClient()
        result = cli.host_get_payout_status()
        self.assertEqual(result, 'idle')

    @patch('xbterminal.gui.rpc_client.requests.post')
    def test_host_get_payout_amount(self, post_mock):
        post_mock.return_value = Mock(**{
            'json.return_value': {
                'jsonrpc': '2.0',
                'result': '12.0',
                'id': 0,
            },
        })
        cli = JSONRPCClient()
        result = cli.host_get_payout_amount()
        self.assertEqual(result, Decimal('12.0'))

    @patch('xbterminal.gui.rpc_client.requests.post')
    def test_host_withdrawal_completed(self, post_mock):
        post_mock.return_value = Mock(**{
            'json.return_value': {
                'jsonrpc': '2.0',
                'result': True,
                'id': 0,
            },
        })
        cli = JSONRPCClient()
        result = cli.host_withdrawal_completed('abcdef', Decimal('10.00'))
        self.assertIs(result, True)
        data = post_mock.call_args[1]['json']
        self.assertEqual(data['method'], 'host_withdrawal_completed')
        self.assertEqual(data['params']['uid'], 'abcdef')
        self.assertEqual(data['params']['fiat_amount'], '10.00')

    @patch('xbterminal.gui.rpc_client.requests.post')
    def test_host_pay_cash(self, post_mock):
        post_mock.return_value = Mock(**{
            'json.return_value': {
                'jsonrpc': '2.0',
                'result': True,
                'id': 0,
            },
        })
        cli = JSONRPCClient()
        result = cli.host_pay_cash(Decimal('10.00'))
        self.assertIs(result, True)
        data = post_mock.call_args[1]['json']
        self.assertEqual(data['method'], 'host_pay_cash')
        self.assertEqual(data['params']['fiat_amount'], '10.00')

    @patch('xbterminal.gui.rpc_client.requests.post')
    def test_get_withdrawal_status_cached(self, post_mock):
        post_mock.return_value = Mock(**{
            'json.side_effect': [{
                'jsonrpc': '2.0',
                'result': 'new',
                'id': 0,
            }, {'error': ''}],
        })
        cli = JSONRPCClient()
        result = cli.get_withdrawal_status('xxx')
        self.assertEqual(result, 'new')
        result = cli.get_withdrawal_status('xxx')
        self.assertEqual(result, 'new')
