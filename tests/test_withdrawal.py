# -*- coding: utf-8 -*-
from decimal import Decimal
import unittest
from mock import patch, Mock
from tests import mocks

from xbterminal.stages.withdrawal import Withdrawal, get_bitcoin_address
from xbterminal.exceptions import NetworkError


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


@patch.dict('xbterminal.helpers.api.state',
            remote_server='https://xbterminal.io')
class WithdrawalTestCase(unittest.TestCase):

    @patch('xbterminal.stages.withdrawal.api.send_request')
    @patch('xbterminal.helpers.crypto.read_secret_key',
           new=mocks.read_secret_key_mock)
    def test_create_order(self, send_mock):
        send_mock.return_value = Mock(**{
            'json.return_value': {
                'uid': 'test_uid',
                'btc_amount': '0.25',
                'exchange_rate': '200.0',
            },
        })

        order = Withdrawal.create_order('wdTestKey', Decimal('1.00'))
        self.assertTrue(send_mock.called)
        self.assertTrue(send_mock.call_args[1]['signed'])
        data = send_mock.call_args[0][2]
        self.assertEqual(data['device'], 'wdTestKey')
        self.assertEqual(data['amount'], '1.00')
        self.assertEqual(order.uid, 'test_uid')
        self.assertEqual(order.btc_amount, Decimal('0.25'))
        self.assertEqual(order.exchange_rate, Decimal('200.0'))
        self.assertFalse(order.confirmed)

    @patch('xbterminal.stages.withdrawal.api.send_request')
    @patch('xbterminal.helpers.crypto.read_secret_key',
           new=mocks.read_secret_key_mock)
    def test_confirm_order(self, send_mock):
        send_mock.return_value = Mock(**{'json.return_value': {
            'btc_amount': '0.26',
            'exchange_rate': '200.5',
        }})

        order = Withdrawal('test_uid', Decimal('0.25'), Decimal('200.0'))
        order.confirm('1PWVL1fW7Ysomg9rXNsS8ng5ZzURa2p9vE')
        self.assertTrue(send_mock.called)
        self.assertTrue(send_mock.call_args[1]['signed'])
        self.assertEqual(order.btc_amount, Decimal('0.26'))
        self.assertEqual(order.exchange_rate, Decimal('200.5'))
        self.assertTrue(order.confirmed)

    @patch('xbterminal.stages.withdrawal.api.send_request')
    @patch('xbterminal.helpers.crypto.read_secret_key',
           new=mocks.read_secret_key_mock)
    def test_cancel_order(self, send_mock):
        send_mock.return_value = Mock()

        order = Withdrawal('test_uid', Decimal('0.25'), Decimal('200'))
        result = order.cancel()
        self.assertTrue(result)
        self.assertTrue(send_mock.called)
        self.assertTrue(send_mock.call_args[1]['signed'])

    @patch('xbterminal.stages.withdrawal.api.send_request')
    @patch('xbterminal.helpers.crypto.read_secret_key',
           new=mocks.read_secret_key_mock)
    def test_cancel_order_error(self, send_mock):
        send_mock.side_effect = NetworkError

        order = Withdrawal('test_uid', Decimal('0.25'), Decimal('200'))
        result = order.cancel()
        self.assertFalse(result)
        self.assertTrue(send_mock.called)

    @patch('xbterminal.stages.withdrawal.api.send_request')
    def test_check_order(self, send_mock):
        order = Withdrawal('test_uid', Decimal('0.25'), Decimal('200'))
        send_mock.return_value = Mock(**{
            'json.return_value': {'status': 'sent'},
        })
        result = order.check()
        self.assertEqual(result, 'sent')

        send_mock.return_value = Mock(**{
            'json.return_value': {'status': 'completed'},
        })
        result = order.check()
        self.assertEqual(result, 'completed')

    @patch('xbterminal.stages.withdrawal.api.send_request')
    def test_check_order_error(self, send_mock):
        order = Withdrawal('test_uid', Decimal('0.25'), Decimal('200'))
        send_mock.side_effect = NetworkError
        result = order.check()
        self.assertIsNone(result)
        self.assertTrue(send_mock.called)

    def test_receipt_url(self):
        order = Withdrawal('test_uid', Decimal('0.25'), Decimal('200'))
        self.assertEqual(order.receipt_url,
                         'https://xbterminal.io/wrc/test_uid/')
