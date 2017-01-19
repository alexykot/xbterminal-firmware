# -*- coding: utf-8 -*-
from decimal import Decimal
import unittest
from mock import patch, Mock

from xbterminal.rpc.payment import Payment
from xbterminal.rpc.exceptions import NetworkError


@patch.dict('xbterminal.rpc.utils.api.state',
            remote_server='https://xbterminal.io')
class PaymentTestCase(unittest.TestCase):

    @patch('xbterminal.rpc.payment.api.send_request')
    def test_create_order(self, send_mock):
        send_mock.return_value = Mock(**{
            'json.return_value': {
                'uid': 'test_uid',
                'btc_amount': '0.25',
                'paid_btc_amount': '0.00',
                'exchange_rate': '200.0',
                'status': 'new',
                'payment_uri': 'bitcoin:test',
            },
        })
        mac_addr = '01:23:45:67:89:00'

        order = Payment.create_order(
            'paymentTestKey', Decimal('1.00'), mac_addr)
        self.assertTrue(send_mock.called)
        data = send_mock.call_args[1]['data']
        self.assertEqual(data['device'], 'paymentTestKey')
        self.assertEqual(data['amount'], '1.00')
        self.assertEqual(data['bt_mac'], mac_addr)

        self.assertEqual(order.uid, 'test_uid')
        self.assertEqual(order.btc_amount, Decimal('0.25'))
        self.assertEqual(order.paid_btc_amount, Decimal('0.00'))
        self.assertEqual(order.exchange_rate, Decimal('200.0'))
        self.assertEqual(order.status, 'new')
        self.assertEqual(order.payment_uri, 'bitcoin:test')
        self.assertIsNone(order.request)

    @patch('xbterminal.rpc.payment.api.send_request')
    def test_cancel(self, send_mock):
        order = Payment('test_uid',
                        Decimal('0.25'), Decimal('0.00'), Decimal('200'),
                        'new', 'test_uri', None)
        result = order.cancel()
        self.assertTrue(send_mock.called)
        self.assertTrue(result)

    @patch('xbterminal.rpc.payment.api.send_request')
    def test_cancel_error(self, send_mock):
        send_mock.side_effect = ValueError
        order = Payment('test_uid',
                        Decimal('0.25'), Decimal('0.00'), Decimal('200'),
                        'new', 'test_uri', None)
        result = order.cancel()
        self.assertTrue(send_mock.called)
        self.assertFalse(result)

    @patch('xbterminal.rpc.payment.api.send_request')
    def test_send(self, send_mock):
        send_mock.return_value = Mock(content='ack')

        order = Payment('test_uid',
                        Decimal('0.25'), Decimal('0.00'), Decimal('200'),
                        'new', 'bitcoin:uri', None)
        result = order.send('message')

        self.assertTrue(send_mock.called)
        kwargs = send_mock.call_args[1]
        self.assertEqual(kwargs['data'], 'message')
        self.assertEqual(kwargs['headers']['Content-Type'],
                         'application/bitcoin-payment')
        self.assertEqual(result, 'ack')

    @patch('xbterminal.rpc.payment.api.send_request')
    def test_check_new(self, send_mock):
        send_mock.return_value = Mock(**{
            'json.return_value': {
                'paid_btc_amount': '0.00',
                'status': 'new',
            },
        })

        order = Payment('test_uid',
                        Decimal('0.25'), Decimal('0.00'), Decimal('200'),
                        'new', 'bitcoin:uri', None)
        order.check()
        self.assertTrue(send_mock.called)
        self.assertEqual(order.status, 'new')
        self.assertEqual(order.paid_btc_amount, Decimal('0.00'))

    @patch('xbterminal.rpc.payment.api.send_request')
    def test_check_notified(self, send_mock):
        send_mock.return_value = Mock(**{
            'json.return_value': {
                'paid_btc_amount': '0.25',
                'status': 'notified',
            },
        })

        order = Payment('test_uid',
                        Decimal('0.25'), Decimal('0.00'), Decimal('200'),
                        'new', 'bitcoin:uri', None)
        order.check()
        self.assertTrue(send_mock.called)
        self.assertEqual(order.status, 'notified')
        self.assertEqual(order.paid_btc_amount, Decimal('0.25'))

    @patch('xbterminal.rpc.payment.api.send_request')
    def test_check_error(self, send_mock):
        send_mock.side_effect = NetworkError

        order = Payment('test_uid',
                        Decimal('0.25'), Decimal('0.00'), Decimal('200'),
                        'new', 'bitcoin:uri', None)
        result = order.check()
        self.assertIsNone(result)
        self.assertTrue(send_mock.called)

    def test_receipt_url(self):
        order = Payment('test_uid',
                        Decimal('0.25'), Decimal('0.00'), Decimal('200'),
                        'new', 'bitcoin:uri', None)
        self.assertEqual(order.receipt_url,
                         'https://xbterminal.io/prc/test_uid/')
