from decimal import Decimal
from mock import patch
import unittest

import xbterminal
from xbterminal import defaults
from xbterminal.stages import amounts


class AmountsUtilsTestCase(unittest.TestCase):

    def test_process_key_input(self):
        amount = Decimal(0)
        keys = [1, 5, 6, 'backspace', 7, '00']
        for key in keys:
            amount = amounts.process_key_input(amount, key)
        self.assertEqual(amount, Decimal('157.00'))

    @patch('xbterminal.stages.amounts.xbterminal')
    def test_format_amount(self, xbt_mock):
        xbt_mock.remote_config = {
            'OUTPUT_DEC_FRACTIONAL_SPLIT': '.',
            'OUTPUT_DEC_THOUSANDS_SPLIT': ',',
        }
        amount = Decimal('1215.75').quantize(defaults.FIAT_DEC_PLACES)
        result = amounts.format_amount(amount, 2)
        self.assertEqual(result, '1,215.75')

    @patch('xbterminal.stages.amounts.xbterminal')
    def test_format_btc_amount(self, xbt_mock):
        xbt_mock.remote_config = {
            'OUTPUT_DEC_FRACTIONAL_SPLIT': '.',
            'OUTPUT_DEC_THOUSANDS_SPLIT': ',',
        }
        amount = Decimal('1.5751').quantize(defaults.FIAT_DEC_PLACES)
        result = amounts.format_btc_amount(amount)
        self.assertEqual(result, '1,575.10')
