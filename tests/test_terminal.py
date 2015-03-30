from decimal import Decimal
from mock import patch
import unittest

import xbterminal
from xbterminal.stages import payment
from xbterminal import defaults


class PaymentUtilsTestCase(unittest.TestCase):

    def test_process_key_input(self):
        value = ''
        keys = [1, 5, 6, 'backspace', 7, '00']
        for key in keys:
            value = payment.processKeyInput(value, key)
        self.assertEqual(value, '15700')

    @patch('xbterminal.stages.payment.xbterminal')
    def test_format_input(self, xbt_mock):
        xbt_mock.remote_config = {
            'OUTPUT_DEC_FRACTIONAL_SPLIT': '.',
            'OUTPUT_DEC_THOUSANDS_SPLIT': ',',
        }
        value = '1234567'
        result = payment.formatInput(value, 2)
        self.assertEqual(result, '12,345.67')

    def test_input_to_decimal(self):
        value = '1250'
        amount = payment.inputToDecimal(value)
        expected = Decimal('12.5').quantize(defaults.FIAT_DEC_PLACES)
        self.assertEqual(amount, expected)

    @patch('xbterminal.stages.payment.xbterminal')
    def test_format_amount(self, xbt_mock):
        xbt_mock.remote_config = {
            'OUTPUT_DEC_FRACTIONAL_SPLIT': '.',
            'OUTPUT_DEC_THOUSANDS_SPLIT': ',',
        }
        amount = Decimal('1215.75').quantize(defaults.FIAT_DEC_PLACES)
        result = payment.formatDecimal(amount, 2)
        self.assertEqual(result, '1,215.75')

    @patch('xbterminal.stages.payment.xbterminal')
    def test_format_btc_amount(self, xbt_mock):
        xbt_mock.remote_config = {
            'OUTPUT_DEC_FRACTIONAL_SPLIT': '.',
            'OUTPUT_DEC_THOUSANDS_SPLIT': ',',
        }
        amount = Decimal('1.5751').quantize(defaults.FIAT_DEC_PLACES)
        result = payment.formatBitcoin(amount)
        self.assertEqual(result, '1,575.10')
