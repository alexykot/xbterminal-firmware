from decimal import Decimal
from mock import patch, Mock
import unittest
import sys

sys.modules['PyQt4'] = Mock()
sys.modules['dbus'] = Mock()
sys.modules['nfc'] = Mock()
sys.modules['nfc.snep'] = Mock()
sys.modules['nfc.llcp'] = Mock()
sys.modules['cv2'] = Mock()
sys.modules['zbar'] = Mock()

import xbterminal

xbterminal.remote_config = {
    'OUTPUT_DEC_FRACTIONAL_SPLIT': '.',
    'OUTPUT_DEC_THOUSANDS_SPLIT': ',',
}

from xbterminal import defaults
from xbterminal.stages import stages


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

    def test_withdraw_button(self):
        run = {
            'screen_buttons': {'pay': False, 'withdraw': True},
            'withdrawal': {},
        }
        ui = Mock()
        next_stage = stages.idle(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['withdrawal']['withdraw_amount'])
        self.assertEqual(run['withdrawal']['fiat_amount'], 0)

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


class WithdrawAmountStageTestCase(unittest.TestCase):

    def test_return(self):
        run = {
            'keypad': Mock(last_key_pressed='backspace'),
            'withdrawal': {'fiat_amount': Decimal(0)},
        }
        ui = Mock()
        next_stage = stages.withdraw_amount(run, ui)
        self.assertEqual(next_stage, defaults.STAGES['idle'])
        self.assertIsNone(run['withdrawal']['fiat_amount'])

    def test_proceed(self):
        run = {
            'keypad': Mock(last_key_pressed='enter'),
            'withdrawal': {'fiat_amount': Decimal('1.00')},
        }
        ui = Mock()
        next_stage = stages.withdraw_amount(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['withdrawal']['withdraw_loading1'])


class WithdrawLoading1StageTestCase(unittest.TestCase):

    def test_proceed(self):
        run = {
            'withdrawal': {'fiat_amount': Decimal('1.00')},
        }
        ui = Mock()
        next_stage = stages.withdraw_loading1(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['withdrawal']['withdraw_scan'])
        self.assertIsNotNone(run['withdrawal']['order'])


class WithdrawScanStageTestCase(unittest.TestCase):

    def setUp(self):
        self.address = '1PWVL1fW7Ysomg9rXNsS8ng5ZzURa2p9vE'

    def test_return(self):
        run = {
            'keypad': Mock(last_key_pressed='backspace'),
            'qr_scanner': Mock(**{'get_data.return_value': None}),
            'withdrawal': {
                'fiat_amount': Decimal(0),
                'order': {
                    'btc_amount': Decimal(0),
                    'exchange_rate': Decimal(0),
                },
            },
        }
        ui = Mock()
        next_stage = stages.withdraw_scan(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['withdrawal']['withdraw_amount'])
        self.assertIsNone(run['withdrawal']['order'])
        self.assertIsNotNone(run['withdrawal']['fiat_amount'])

    def test_proceed(self):
        run = {
            'keypad': Mock(last_key_pressed=None),
            'qr_scanner': Mock(**{'get_data.return_value': self.address}),
            'withdrawal': {
                'fiat_amount': Decimal(0),
                'order': {
                    'btc_amount': Decimal(0),
                    'exchange_rate': Decimal(0),
                },
            },
        }
        ui = Mock()
        next_stage = stages.withdraw_scan(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['withdrawal']['withdraw_confirm'])
        self.assertIsNotNone(run['withdrawal']['address'])


class WithdrawConfirmStageTestCase(unittest.TestCase):

    def test_return(self):
        run = {
            'keypad': Mock(last_key_pressed='backspace'),
            'screen_buttons': {'confirm_withdrawal': False},
            'withdrawal': {
                'fiat_amount': Decimal(0),
                'order': {
                    'btc_amount': Decimal(0),
                    'exchange_rate': Decimal(0),
                },
                'address': '1PWVL1fW7Ysomg9rXNsS8ng5ZzURa2p9vE',
            },
        }
        ui = Mock()
        next_stage = stages.withdraw_confirm(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['withdrawal']['withdraw_amount'])
        self.assertIsNone(run['withdrawal']['order'])
        self.assertIsNone(run['withdrawal']['address'])
        self.assertIsNotNone(run['withdrawal']['fiat_amount'])

    def test_proceed(self):
        run = {
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {'confirm_withdrawal': True},
            'withdrawal': {
                'fiat_amount': Decimal(0),
                'order': {
                    'btc_amount': Decimal(0),
                    'exchange_rate': Decimal(0),
                },
                'address': '1PWVL1fW7Ysomg9rXNsS8ng5ZzURa2p9vE',
            },
        }
        ui = Mock()
        next_stage = stages.withdraw_confirm(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['withdrawal']['withdraw_loading2'])


class WithdrawLoading2StageTestCase(unittest.TestCase):

    def test_proceed(self):
        run = {
            'withdrawal': {
                'address': '1PWVL1fW7Ysomg9rXNsS8ng5ZzURa2p9vE',
            },
        }
        ui = Mock()
        next_stage = stages.withdraw_loading2(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['withdrawal']['withdraw_success'])
        self.assertIsNotNone(run['withdrawal']['receipt_url'])
        self.assertIsNotNone(run['withdrawal']['qr_image_path'])


class WithdrawConfirmStageTestCase(unittest.TestCase):

    def test_return(self):
        run = {
            'keypad': Mock(last_key_pressed='enter'),
            'withdrawal': {
                'qr_image_path': '/path/to/image',
            },
        }
        ui = Mock()
        next_stage = stages.withdraw_success(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['idle'])
        self.assertIsNone(run['withdrawal']['qr_image_path'])
