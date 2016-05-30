# -*- coding: utf-8 -*-
from decimal import Decimal
import unittest
from mock import patch, Mock
from tests import mocks

from xbterminal import defaults
from xbterminal.stages import amounts
from xbterminal.stages.payment import Payment
from xbterminal.stages.withdrawal import Withdrawal, get_bitcoin_address
from xbterminal.helpers import api
from xbterminal.exceptions import NetworkError, ServerError


@patch.dict('xbterminal.stages.amounts.xbterminal.runtime',
            remote_config={
                'language': {
                    'code': 'en',
                    'thousands_split': ',',
                    'fractional_split': '.',
                },
                'currency': {
                    'prefix': '$',
                },
            })
class AmountsUtilsTestCase(unittest.TestCase):

    def test_format_fiat_amount_pretty(self):
        amount = Decimal('3513.00').quantize(defaults.FIAT_DEC_PLACES)
        result = amounts.format_fiat_amount_pretty(amount)
        self.assertEqual(result, u'3,513.00')
        result = amounts.format_fiat_amount_pretty(amount, prefix=True)
        self.assertEqual(result, u'$3,513.00')

    def test_format_btc_amount_pretty(self):
        amount = Decimal('0.21231923').quantize(defaults.BTC_DEC_PLACES)
        result = amounts.format_btc_amount_pretty(amount)
        self.assertIn(u'212.31<span style="font-size: small;">923</span>',
                      result)
        result = amounts.format_btc_amount_pretty(amount, frac2_size='12px')
        self.assertIn(u'212.31<span style="font-size: 12px;">923</span>',
                      result)
        result = amounts.format_btc_amount_pretty(amount, prefix=True)
        self.assertIn(u'm฿212.31<span style="font-size: small;">923</span>',
                      result)

    def test_format_exchange_rate_pretty(self):
        amount = Decimal('241.8').quantize(defaults.FIAT_DEC_PLACES)
        result = amounts.format_exchange_rate_pretty(amount)
        self.assertEqual(result, u'1 BTC = $241.80')


@patch.dict('xbterminal.helpers.api.xbterminal.runtime',
            remote_server='https://xbterminal.io')
class ApiUtilsTestCase(unittest.TestCase):

    def test_get_url(self):
        url = api.get_url('config', device_key='test')
        self.assertEqual(url, 'https://xbterminal.io/api/v2/devices/test/')

    @patch('xbterminal.helpers.api.requests.Session')
    def test_send_request(self, session_cls_mock):
        response_mock = Mock(status_code=200)
        session_mock = Mock(**{'send.return_value': response_mock})
        session_cls_mock.return_value = session_mock

        api.send_request('get', 'http://test_url.com')
        self.assertTrue(session_mock.send.called)
        request = session_mock.send.call_args[0][0]
        self.assertEqual(request.url, 'http://test_url.com/')
        self.assertEqual(request.headers['User-Agent'],
                         defaults.EXTERNAL_CALLS_REQUEST_HEADERS['User-Agent'])
        self.assertNotIn('X-Signature', request.headers)
        self.assertEqual(session_mock.send.call_args[1]['timeout'],
                         defaults.EXTERNAL_CALLS_TIMEOUT)

    @patch('xbterminal.helpers.api.requests.Session')
    @patch('xbterminal.helpers.crypto.read_secret_key',
           new=mocks.read_secret_key_mock)
    def test_send_request_signed(self, session_cls_mock):
        response_mock = Mock(status_code=200)
        session_mock = Mock(**{'send.return_value': response_mock})
        session_cls_mock.return_value = session_mock

        api.send_request('post', 'http://test_url.com',
                         data={'aaa': 111}, signed=True)
        self.assertTrue(session_mock.send.called)
        request = session_mock.send.call_args[0][0]
        self.assertEqual(request.url, 'http://test_url.com/')
        self.assertIn('X-Signature', request.headers)

    @patch('xbterminal.helpers.api.requests.Session')
    @patch('xbterminal.helpers.crypto.read_secret_key',
           new=mocks.read_secret_key_mock)
    def test_send_request_signed_no_body(self, session_cls_mock):
        response_mock = Mock(status_code=204)
        session_mock = Mock(**{'send.return_value': response_mock})
        session_cls_mock.return_value = session_mock

        api.send_request('post', 'http://test_url.com', signed=True)
        self.assertTrue(session_mock.send.called)
        request = session_mock.send.call_args[0][0]
        self.assertEqual(request.url, 'http://test_url.com/')
        self.assertIn('X-Signature', request.headers)

    @patch('xbterminal.helpers.api.requests.Session')
    def test_send_request_network_error(self, session_cls_mock):
        session_mock = Mock(**{'send.side_effect': IOError})
        session_cls_mock.return_value = session_mock

        with self.assertRaises(NetworkError):
            api.send_request('get', 'http://test_url.com')

    @patch('xbterminal.helpers.api.requests.Session')
    def test_send_request_server_error(self, session_cls_mock):
        response_mock = Mock(status_code=500)
        session_mock = Mock(**{'send.return_value': response_mock})
        session_cls_mock.return_value = session_mock

        with self.assertRaises(ServerError):
            api.send_request('get', 'http://test_url.com')


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


@patch.dict('xbterminal.helpers.api.xbterminal.runtime',
            remote_server='https://xbterminal.io')
class PaymentTestCase(unittest.TestCase):

    @patch('xbterminal.stages.payment.api.send_request')
    def test_create_order(self, send_mock):
        send_mock.return_value = Mock(**{
            'json.return_value': {
                'uid': 'test_uid',
                'btc_amount': '0.25',
                'exchange_rate': '200.0',
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
        self.assertEqual(order.exchange_rate, Decimal('200.0'))
        self.assertEqual(order.payment_uri, 'bitcoin:test')
        self.assertIsNone(order.request)

    @patch('xbterminal.stages.payment.api.send_request')
    def test_cancel(self, send_mock):
        order = Payment('test_uid', Decimal('0.25'), Decimal(200),
                        'test_uri', None)
        result = order.cancel()
        self.assertTrue(send_mock.called)
        self.assertTrue(result)

    @patch('xbterminal.stages.payment.api.send_request')
    def test_cancel_error(self, send_mock):
        send_mock.side_effect = ValueError
        order = Payment('test_uid', Decimal('0.25'), Decimal(200),
                        'test_uri', None)
        result = order.cancel()
        self.assertTrue(send_mock.called)
        self.assertFalse(result)

    @patch('xbterminal.stages.payment.api.send_request')
    def test_send(self, send_mock):
        send_mock.return_value = Mock(content='ack')

        order = Payment('test_uid', Decimal('0.25'), Decimal('200'),
                        'bitcoin:uri', None)
        result = order.send('message')

        self.assertTrue(send_mock.called)
        kwargs = send_mock.call_args[1]
        self.assertEqual(kwargs['data'], 'message')
        self.assertEqual(kwargs['headers']['Content-Type'],
                         'application/bitcoin-payment')
        self.assertEqual(result, 'ack')

    @patch('xbterminal.stages.payment.api.send_request')
    def test_check_new(self, send_mock):
        send_mock.return_value = Mock(**{
            'json.return_value': {
                'status': 'new',
            },
        })

        order = Payment('test_uid', Decimal('0.25'), Decimal('200'),
                        'bitcoin:uri', None)
        result = order.check()
        self.assertTrue(send_mock.called)
        self.assertEqual(result, 'new')

    @patch('xbterminal.stages.payment.api.send_request')
    def test_check_notified(self, send_mock):
        send_mock.return_value = Mock(**{
            'json.return_value': {
                'status': 'notified',
            },
        })

        order = Payment('test_uid', Decimal('0.25'), Decimal('200'),
                        'bitcoin:uri', None)
        result = order.check()
        self.assertTrue(send_mock.called)
        self.assertEqual(result, 'notified')

    @patch('xbterminal.stages.payment.api.send_request')
    def test_check_error(self, send_mock):
        send_mock.side_effect = NetworkError

        order = Payment('test_uid', Decimal('0.25'), Decimal('200'),
                        'bitcoin:uri', None)
        result = order.check()
        self.assertIsNone(result)
        self.assertTrue(send_mock.called)

    def test_receipt_url(self):
        order = Payment('test_uid', Decimal('0.25'), Decimal('200'),
                        'bitcoin:uri', None)
        self.assertEqual(order.receipt_url,
                         'https://xbterminal.io/prc/test_uid/')


@patch.dict('xbterminal.helpers.api.xbterminal.runtime',
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
        send_mock.return_value = Mock(**{'json.return_value': {}})

        order = Withdrawal('test_uid', Decimal('0.25'), Decimal('200'))
        order.confirm('1PWVL1fW7Ysomg9rXNsS8ng5ZzURa2p9vE')
        self.assertTrue(send_mock.called)
        self.assertTrue(send_mock.call_args[1]['signed'])
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
