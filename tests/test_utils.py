from decimal import Decimal
import unittest

from xbterminal import defaults
from xbterminal.stages import amounts
from xbterminal.stages.withdrawal import get_bitcoin_address


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
