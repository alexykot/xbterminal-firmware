# -*- coding: utf-8 -*-
from decimal import Decimal
import unittest
from mock import patch, Mock
from tests import mocks

from xbterminal.rpc.withdrawal import Withdrawal, get_bitcoin_address
from xbterminal.rpc.exceptions import NetworkError


class GetAddressTestCase(unittest.TestCase):

    def setUp(self):
        self.address = '1PWVL1fW7Ysomg9rXNsS8ng5ZzURa2p9vE'

    def test_only_address(self):
        message = self.address
        result = get_bitcoin_address(message)
        self.assertEqual(result, self.address)

    def test_bitcoin_uri(self):
        message = 'bitcoin:{0}?label=MyAddr'.format(self.address)
        result = get_bitcoin_address(message)
        self.assertEqual(result, self.address)


@patch.dict('xbterminal.rpc.utils.api.state',
            remote_server='https://xbterminal.io')
class WithdrawalTestCase(unittest.TestCase):

    @patch('xbterminal.rpc.withdrawal.api.send_request')
    @patch('xbterminal.rpc.utils.crypto.read_secret_key',
           new=mocks.read_secret_key_mock)
    def test_create(self, send_mock):
        send_mock.return_value = Mock(**{
            'json.return_value': {
                'uid': 'test_uid',
                'fiat_amount': '50.0',
                'btc_amount': '0.25',
                'tx_fee_btc_amount': '0.0001',
                'exchange_rate': '200.0',
                'status': 'new',
            },
        })

        order = Withdrawal.create('wdTestKey', Decimal('1.00'))
        self.assertTrue(send_mock.called)
        self.assertTrue(send_mock.call_args[1]['signed'])
        data = send_mock.call_args[0][2]
        self.assertEqual(data['device'], 'wdTestKey')
        self.assertEqual(data['amount'], '1.00')
        self.assertEqual(order.uid, 'test_uid')
        self.assertEqual(order.fiat_amount, Decimal('50.0'))
        self.assertEqual(order.btc_amount, Decimal('0.25'))
        self.assertEqual(order.tx_fee_btc_amount, Decimal('0.0001'))
        self.assertEqual(order.exchange_rate, Decimal('200.0'))
        self.assertEqual(order.status, 'new')

    @patch('xbterminal.rpc.withdrawal.api.send_request')
    def test_get(self, send_mock):
        send_mock.return_value = Mock(**{
            'json.return_value': {
                'uid': 'test_uid',
                'fiat_amount': '50.0',
                'btc_amount': '0.25',
                'tx_fee_btc_amount': '0.0001',
                'exchange_rate': '200.0',
                'status': 'new',
            },
        })

        order = Withdrawal.get('test_uid')
        self.assertIs(send_mock.called, True)
        self.assertIn('test_uid', send_mock.call_args[0][1])
        self.assertEqual(order.uid, 'test_uid')
        self.assertEqual(order.fiat_amount, Decimal('50.0'))
        self.assertEqual(order.btc_amount, Decimal('0.25'))
        self.assertEqual(order.tx_fee_btc_amount, Decimal('0.0001'))
        self.assertEqual(order.exchange_rate, Decimal('200.0'))
        self.assertEqual(order.status, 'new')

    @patch('xbterminal.rpc.withdrawal.api.send_request')
    @patch('xbterminal.rpc.utils.crypto.read_secret_key',
           new=mocks.read_secret_key_mock)
    def test_confirm(self, send_mock):
        send_mock.return_value = Mock(**{'json.return_value': {
            'btc_amount': '0.26',
            'exchange_rate': '200.5',
        }})

        order = Withdrawal('test_uid', Decimal('50.0'), Decimal('0.25'),
                           Decimal('0.0001'), Decimal('200.0'), 'new')
        order.confirm('1PWVL1fW7Ysomg9rXNsS8ng5ZzURa2p9vE')
        self.assertTrue(send_mock.called)
        self.assertTrue(send_mock.call_args[1]['signed'])
        self.assertEqual(order.btc_amount, Decimal('0.26'))
        self.assertEqual(order.exchange_rate, Decimal('200.5'))

    @patch('xbterminal.rpc.withdrawal.api.send_request')
    @patch('xbterminal.rpc.utils.crypto.read_secret_key',
           new=mocks.read_secret_key_mock)
    def test_cancel(self, send_mock):
        send_mock.return_value = Mock()

        order = Withdrawal('test_uid', Decimal('50.0'), Decimal('0.25'),
                           Decimal('0.0001'), Decimal('200'), 'new')
        result = order.cancel()
        self.assertTrue(result)
        self.assertTrue(send_mock.called)
        self.assertTrue(send_mock.call_args[1]['signed'])

    @patch('xbterminal.rpc.withdrawal.api.send_request')
    @patch('xbterminal.rpc.utils.crypto.read_secret_key',
           new=mocks.read_secret_key_mock)
    def test_cancel_error(self, send_mock):
        send_mock.side_effect = NetworkError

        order = Withdrawal('test_uid', Decimal('50.0'), Decimal('0.25'),
                           Decimal('0.0001'), Decimal('200'), 'new')
        result = order.cancel()
        self.assertFalse(result)
        self.assertTrue(send_mock.called)

    @patch('xbterminal.rpc.withdrawal.api.send_request')
    def test_check(self, send_mock):
        order = Withdrawal('test_uid', Decimal('50.0'), Decimal('0.25'),
                           Decimal('0.0001'), Decimal('200'), 'new')
        send_mock.return_value = Mock(**{
            'json.return_value': {'status': 'sent'},
        })
        order.check()
        self.assertEqual(order.status, 'sent')

        send_mock.return_value = Mock(**{
            'json.return_value': {'status': 'completed'},
        })
        order.check()
        self.assertEqual(order.status, 'completed')

    @patch('xbterminal.rpc.withdrawal.api.send_request')
    def test_check_error(self, send_mock):
        order = Withdrawal('test_uid', Decimal('50.0'), Decimal('0.25'),
                           Decimal('0.0001'), Decimal('200'), 'new')
        send_mock.side_effect = NetworkError
        result = order.check()
        self.assertIsNone(result)
        self.assertTrue(send_mock.called)

    def test_receipt_url(self):
        order = Withdrawal('test_uid', Decimal('50.0'), Decimal('0.25'),
                           Decimal('0.0001'), Decimal('200'), 'new')
        self.assertEqual(order.receipt_url,
                         'https://xbterminal.io/wrc/test_uid/')
