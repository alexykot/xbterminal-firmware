from decimal import Decimal
from mock import patch, Mock
import unittest
import sys

sys.modules['PyQt4'] = Mock()
sys.modules['dbus'] = Mock()
sys.modules['nfc'] = Mock()
sys.modules['nfc.snep'] = Mock()
sys.modules['nfc.llcp'] = Mock()

import xbterminal

xbterminal.remote_config = {
    'OUTPUT_DEC_FRACTIONAL_SPLIT': '.',
    'OUTPUT_DEC_THOUSANDS_SPLIT': ',',
}

from xbterminal import defaults
from xbterminal.stages import stages, amounts


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


class IdleStageTestCase(unittest.TestCase):

    def test_pay_button(self):
        run = {
            'screen_buttons': {'pay': True, 'withdraw': False},
            'payment': {},
        }
        ui = Mock()
        next_stage = stages.idle(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['payment']['pay_amount'])
        self.assertEqual(run['payment']['fiat_amount'], 0)

    def test_key_input(self):
        keypad = Mock(last_key_pressed=1)
        run = {
            'keypad': keypad,
            'screen_buttons': {'pay': False, 'withdraw': False},
            'payment': {},
        }
        ui = Mock()
        next_stage = stages.idle(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['payment']['pay_amount'])
        self.assertEqual(run['payment']['fiat_amount'], Decimal('0.01'))


class PayAmountStageTestCase(unittest.TestCase):

    def test_return(self):
        run = {
            'keypad': Mock(last_key_pressed='backspace'),
            'payment': {'fiat_amount': Decimal(0)},
        }
        ui = Mock()
        next_stage = stages.pay_amount(run, ui)
        self.assertEqual(next_stage, defaults.STAGES['idle'])

    def test_proceed(self):
        run = {
            'keypad': Mock(last_key_pressed='enter'),
            'payment': {'fiat_amount': Decimal('1.00')},
        }
        ui = Mock()
        next_stage = stages.pay_amount(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['payment']['pay_loading'])
