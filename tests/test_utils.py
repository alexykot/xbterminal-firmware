from decimal import Decimal
import unittest
from mock import patch, Mock

from xbterminal import defaults
from xbterminal.stages import amounts
from xbterminal.stages.withdrawal import Withdrawal, get_bitcoin_address


class AmountsUtilsTestCase(unittest.TestCase):

    def test_process_key_input(self):
        amount = Decimal(0)
        keys = [1, 5, 6, 'backspace', 7, '00']
        for key in keys:
            amount = amounts.process_key_input(amount, key)
        self.assertEqual(amount, Decimal('157.00'))

    def test_format_amount(self):
        amount = Decimal('1215.75').quantize(defaults.FIAT_DEC_PLACES)
        result = amounts.format_amount(amount, 2)
        self.assertEqual(result, '1,215.75')

    def test_format_btc_amount(self):
        amount = Decimal('1.5751').quantize(defaults.FIAT_DEC_PLACES)
        result = amounts.format_btc_amount(amount)
        self.assertEqual(result, '1,575.10')

    def test_format_exchange_rate(self):
        rate = Decimal('241.85').quantize(defaults.FIAT_DEC_PLACES)
        result = amounts.format_exchange_rate(rate)
        self.assertEqual(result, '0.242')


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


@patch.dict('xbterminal.stages.withdrawal.xbterminal.runtime',
            remote_server='https://xbterminal.io')
class WithdrawalTestCase(unittest.TestCase):

    @patch('xbterminal.stages.withdrawal.requests.Session')
    def test_create_order(self, session_cls_mock):
        response_mock = Mock(**{
            'json.return_value': {
                'uid': 'test_uid',
                'btc_amount': '0.25',
                'exchange_rate': '200.0',
            },
        })
        session_mock = Mock(**{'send.return_value': response_mock})
        session_cls_mock.return_value = session_mock

        order = Withdrawal.create_order(Decimal('1.00'))
        self.assertTrue(session_mock.send.called)
        request = session_mock.send.call_args[0][0]
        self.assertIn('X-Signature', request.headers)
        self.assertEqual(order.uid, 'test_uid')
        self.assertEqual(order.btc_amount, Decimal('0.25'))
        self.assertEqual(order.exchange_rate, Decimal('200.0'))

    @patch('xbterminal.stages.withdrawal.requests.Session')
    def test_confirm_order(self, session_cls_mock):
        response_mock = Mock(**{'json.return_value': {}})
        session_mock = Mock(**{'send.return_value': response_mock})
        session_cls_mock.return_value = session_mock

        order = Withdrawal('test_uid', Decimal('0.25'), Decimal('200'))
        order.confirm('1PWVL1fW7Ysomg9rXNsS8ng5ZzURa2p9vE')
        self.assertTrue(session_mock.send.called)
        request = session_mock.send.call_args[0][0]
        self.assertIn('X-Signature', request.headers)

    @patch('xbterminal.stages.withdrawal.requests.get')
    def test_check_order(self, get_mock):
        order = Withdrawal('test_uid', Decimal('0.25'), Decimal('200'))
        get_mock.return_value = Mock(**{
            'json.return_value': {'status': 'sent'},
        })
        result = order.check()
        self.assertIsNone(result)

        get_mock.return_value = Mock(**{
            'json.return_value': {'status': 'completed'},
        })
        result = order.check()
        self.assertIsNotNone(result)
