# -*- coding: utf-8 -*-
from decimal import Decimal
from mock import patch, Mock
import unittest

from xbterminal.gui import settings
from xbterminal.gui import stages
from xbterminal.gui.exceptions import ServerError


patcher = patch.dict(
    'xbterminal.gui.utils.amounts.state',
    remote_config={
        'language': {
            'code': 'en',
            'thousands_split': ',',
            'fractional_split': '.',
        },
        'currency': {
            'prefix': u'\xa3',
        },
    })


def setUpModule():
    patcher.start()


def tearDownModule():
    patcher.stop()


class BootupStageTestCase(unittest.TestCase):

    def test_bootup(self):
        state = {
            'remote_config': {
                'status': 'active',
                'language': {'code': 'en'},
                'currency': {'prefix': '$'},
            },
        }
        ui = Mock()
        next_stage = stages.bootup(state, ui)
        self.assertEqual(ui.showScreen.call_args[0][0], 'load_indefinite')
        self.assertEqual(next_stage, settings.STAGES['idle'])

    def test_registration(self):
        state = {
            'remote_config': {
                'status': 'activation',
                'language': {'code': 'en'},
                'currency': {'prefix': '$'},
            },
        }
        ui = Mock()
        next_stage = stages.bootup(state, ui)
        self.assertEqual(ui.showScreen.call_args[0][0], 'load_indefinite')
        self.assertEqual(next_stage, settings.STAGES['activate'])


class ActivateStageTestCase(unittest.TestCase):

    def test_proceed(self):
        client_mock = Mock(**{
            'get_activation_code.return_value': 'testCode',
        })
        state = {
            'client': client_mock,
            'remote_config': {
                'remote_server': 'https://xbterminal.io',
                'status': 'active',
            },
        }
        ui = Mock()
        next_stage = stages.activate(state, ui)
        self.assertTrue(client_mock.get_activation_code.called)
        self.assertEqual(ui.showScreen.call_args[0][0], 'activation')
        self.assertEqual(ui.setText.call_args_list[0][0][1],
                         'xbterminal.io')
        self.assertEqual(ui.setText.call_args_list[1][0][1],
                         'testCode')
        self.assertEqual(next_stage, settings.STAGES['idle'])


class IdleStageTestCase(unittest.TestCase):

    def test_begin_button(self):
        client_mock = Mock(**{
            'start_nfc_server.return_value': True,
        })
        state = {
            'client': client_mock,
            'remote_config': {
                'remote_server': 'https://xbterminal.io',
            },
            'screen_buttons': {
                'idle_begin_btn': True,
                'standby_wake_btn': False,
            },
        }
        ui = Mock()
        next_stage = stages.idle(state, ui)
        self.assertEqual(ui.showScreen.call_args[0][0], 'idle')
        self.assertEqual(
            client_mock.start_nfc_server.call_args[1]['message'],
            'https://xbterminal.io')
        self.assertTrue(client_mock.stop_nfc_server.called)
        self.assertEqual(next_stage,
                         settings.STAGES['payment']['pay_amount'])
        self.assertFalse(any(state for state
                             in state['screen_buttons'].values()))

    def test_enter_key_input(self):
        client_mock = Mock()
        keypad = Mock(last_key_pressed='enter')
        state = {
            'client': client_mock,
            'remote_config': {
                'remote_server': 'https://xbterminal.io',
            },
            'keypad': keypad,
            'screen_buttons': {
                'idle_begin_btn': False,
                'standby_wake_btn': False,
            },
        }
        ui = Mock()
        next_stage = stages.idle(state, ui)
        self.assertEqual(next_stage,
                         settings.STAGES['payment']['pay_amount'])

    def test_host_system_payout(self):
        client_mock = Mock(**{
            'host_get_payout.return_value': Decimal('0.15'),
        })
        state = {
            'client': client_mock,
            'remote_config': {
                'remote_server': 'https://xbterminal.io',
            },
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'idle_begin_btn': False,
                'standby_wake_btn': False,
            },
            'withdrawal': {},
        }
        ui = Mock()
        next_stage = stages.idle(state, ui)
        self.assertTrue(client_mock.host_get_payout.called)
        self.assertTrue(client_mock.stop_nfc_server.called)
        self.assertEqual(next_stage,
                         settings.STAGES['withdrawal']['withdraw_select'])
        self.assertEqual(state['withdrawal']['fiat_amount'], Decimal('0.15'))

    def test_alt_key_input(self):
        client_mock = Mock()
        keypad = Mock(last_key_pressed='alt')
        state = {
            'client': client_mock,
            'remote_config': {
                'remote_server': 'https://xbterminal.io',
            },
            'keypad': keypad,
            'gui_config': {'default_withdrawal_amount': '0.23'},
            'screen_buttons': {
                'idle_begin_btn': False,
                'standby_wake_btn': False,
            },
            'withdrawal': {},
        }
        ui = Mock()
        next_stage = stages.idle(state, ui)
        self.assertTrue(client_mock.host_get_payout.called)
        self.assertEqual(next_stage,
                         settings.STAGES['withdrawal']['withdraw_select'])
        self.assertEqual(state['withdrawal']['fiat_amount'], Decimal('0.23'))

    @patch('xbterminal.gui.stages.time.sleep')
    def test_standby(self, sleep_mock):
        client_mock = Mock(**{'host_get_payout.return_value': None})
        keypad = Mock(last_key_pressed=None)
        state = {
            'last_activity_timestamp': 0,
            'client': client_mock,
            'remote_config': {
                'remote_server': 'https://xbterminal.io',
            },
            'keypad': keypad,
            'screen_buttons': {
                'idle_begin_btn': False,
                'standby_wake_btn': False,
            },
            'withdrawal': {},
        }

        def standby_wake():
            state['screen_buttons']['standby_wake_btn'] = True

        ui = Mock(**{
            'showStandByScreen.side_effect': standby_wake,
        })
        next_stage = stages.idle(state, ui)
        self.assertTrue(ui.showStandByScreen.called)
        self.assertEqual(next_stage,
                         settings.STAGES['payment']['pay_amount'])
        self.assertFalse(any(state for state
                             in state['screen_buttons'].values()))


class PaymentAmountStageTestCase(unittest.TestCase):

    def setUp(self):
        self.remote_config = {
            'settings': {
                'amount_1': '0.50',
                'amount_2': '3.00',
                'amount_3': '15.00',
                'amount_shift': '0.10',
            },
        }

    def test_option_1(self):
        client_mock = Mock()
        state = {
            'client': client_mock,
            'keypad': Mock(last_key_pressed=None),
            'remote_config': self.remote_config,
            'screen_buttons': {
                'pamount_opt1_btn': True,
                'pamount_opt2_btn': False,
                'pamount_opt3_btn': False,
            },
            'payment': {},
        }
        ui = Mock()
        next_stage = stages.pay_amount(state, ui)
        self.assertEqual(ui.showScreen.call_args[0][0], 'pay_amount')
        self.assertFalse(client_mock.host_get_payout.called)
        self.assertEqual(next_stage,
                         settings.STAGES['payment']['pay_loading'])
        self.assertFalse(any(state for state
                             in state['screen_buttons'].values()))
        self.assertEqual(state['payment']['fiat_amount'], Decimal('0.50'))

    def test_option_2(self):
        client_mock = Mock()
        state = {
            'client': client_mock,
            'keypad': Mock(last_key_pressed=None),
            'remote_config': self.remote_config,
            'screen_buttons': {
                'pamount_opt1_btn': False,
                'pamount_opt2_btn': True,
                'pamount_opt3_btn': False,
            },
            'payment': {},
        }
        ui = Mock()
        next_stage = stages.pay_amount(state, ui)
        self.assertEqual(next_stage,
                         settings.STAGES['payment']['pay_loading'])
        self.assertFalse(any(state for state
                             in state['screen_buttons'].values()))
        self.assertEqual(state['payment']['fiat_amount'], Decimal('3.00'))

    def test_option_3(self):
        client_mock = Mock()
        state = {
            'client': client_mock,
            'keypad': Mock(last_key_pressed=None),
            'remote_config': self.remote_config,
            'screen_buttons': {
                'pamount_opt1_btn': False,
                'pamount_opt2_btn': False,
                'pamount_opt3_btn': True,
            },
            'payment': {},
        }
        ui = Mock()
        next_stage = stages.pay_amount(state, ui)
        self.assertEqual(next_stage,
                         settings.STAGES['payment']['pay_loading'])
        self.assertFalse(any(state for state
                             in state['screen_buttons'].values()))
        self.assertEqual(state['payment']['fiat_amount'], Decimal('15.00'))

    def test_return(self):
        client_mock = Mock()
        state = {
            'client': client_mock,
            'keypad': Mock(last_key_pressed='backspace'),
            'remote_config': self.remote_config,
            'screen_buttons': {
                'pamount_opt1_btn': False,
                'pamount_opt2_btn': False,
                'pamount_opt3_btn': False,
            },
            'payment': {},
        }
        ui = Mock()
        next_stage = stages.pay_amount(state, ui)
        self.assertEqual(next_stage,
                         settings.STAGES['idle'])
        self.assertFalse(any(state for state
                             in state['screen_buttons'].values()))

    def test_timeout(self):
        client_mock = Mock()
        state = {
            'client': client_mock,
            'keypad': Mock(last_key_pressed=None),
            'remote_config': self.remote_config,
            'last_activity_timestamp': 0,
            'screen_buttons': {
                'pamount_opt1_btn': False,
                'pamount_opt2_btn': False,
                'pamount_opt3_btn': False,
            },
            'payment': {},
        }
        ui = Mock()
        next_stage = stages.pay_amount(state, ui)
        self.assertEqual(next_stage,
                         settings.STAGES['idle'])
        self.assertFalse(any(state for state
                             in state['screen_buttons'].values()))


class PayConfirmStageTestCase(unittest.TestCase):

    def setUp(self):
        self.remote_config = {
            'settings': {
                'amount_1': '0.50',
                'amount_2': '3.00',
                'amount_3': '15.00',
                'amount_shift': '0.07',
            },
        }

    def test_decrement(self):
        client_mock = Mock()
        state = {
            'client': client_mock,
            'keypad': Mock(last_key_pressed=None),
            'remote_config': self.remote_config,
            'screen_buttons': {
                'pconfirm_decr_btn': True,
                'pconfirm_incr_btn': False,
                'pconfirm_confirm_btn': True,
                'pconfirm_goback_btn': False,
            },
            'payment': {'fiat_amount': Decimal('0.50')},
        }
        ui = Mock()
        next_stage = stages.pay_confirm(state, ui)
        self.assertEqual(ui.showScreen.call_args[0][0], 'pay_confirm')
        self.assertFalse(client_mock.host_get_payout.called)
        self.assertEqual(ui.setText.call_args_list[0][0][1], '-0.07')
        self.assertEqual(ui.setText.call_args_list[1][0][1], '+0.07')
        self.assertEqual(ui.setText.call_args_list[2][0][1], u'\xa30.50')
        self.assertEqual(ui.setText.call_args_list[3][0][1], u'\xa30.43')
        self.assertEqual(next_stage,
                         settings.STAGES['payment']['pay_loading'])
        self.assertEqual(state['payment']['fiat_amount'], Decimal('0.43'))
        self.assertFalse(any(state for state
                             in state['screen_buttons'].values()))

    def test_increment(self):
        client_mock = Mock()
        state = {
            'client': client_mock,
            'keypad': Mock(last_key_pressed=None),
            'remote_config': self.remote_config,
            'screen_buttons': {
                'pconfirm_decr_btn': False,
                'pconfirm_incr_btn': True,
                'pconfirm_confirm_btn': True,
                'pconfirm_goback_btn': False,
            },
            'payment': {'fiat_amount': Decimal('0.50')},
        }
        ui = Mock()
        next_stage = stages.pay_confirm(state, ui)
        self.assertEqual(next_stage,
                         settings.STAGES['payment']['pay_loading'])
        self.assertEqual(state['payment']['fiat_amount'], Decimal('0.57'))
        self.assertFalse(any(state for state
                             in state['screen_buttons'].values()))

    def test_return(self):
        client_mock = Mock()
        state = {
            'client': client_mock,
            'keypad': Mock(last_key_pressed=None),
            'remote_config': self.remote_config,
            'screen_buttons': {
                'pconfirm_decr_btn': False,
                'pconfirm_incr_btn': False,
                'pconfirm_confirm_btn': False,
                'pconfirm_goback_btn': True,
            },
            'payment': {'fiat_amount': Decimal('0.00')},
        }
        ui = Mock()
        next_stage = stages.pay_confirm(state, ui)
        self.assertEqual(next_stage,
                         settings.STAGES['payment']['pay_amount'])
        self.assertFalse(any(state for state
                             in state['screen_buttons'].values()))


class PayLoadingStageTestCase(unittest.TestCase):

    def test_no_amount(self):
        state = {
            'payment': {
                'fiat_amount': None,
            },
        }
        ui = Mock()
        next_stage = stages.pay_loading(state, ui)
        self.assertEqual(next_stage,
                         settings.STAGES['payment']['pay_amount'])

    @patch('xbterminal.gui.stages.qr.qr_gen')
    def test_proceed(self, qr_gen_mock):
        client_mock = Mock(**{
            'create_payment_order.return_value': {
                'uid': 'testUid',
                'payment_uri': 'test',
            },
        })
        state = {
            'client': client_mock,
            'payment': {
                'fiat_amount': Decimal('1.00'),
            },
        }
        ui = Mock()
        next_stage = stages.pay_loading(state, ui)
        self.assertEqual(ui.showScreen.call_args[0][0],
                         'load_indefinite')
        self.assertEqual(
            client_mock.create_payment_order.call_args[1]['fiat_amount'],
            Decimal('1.00'))
        self.assertEqual(state['payment']['uid'], 'testUid')
        self.assertTrue(qr_gen_mock.call_args[0][0], 'test')
        self.assertEqual(next_stage,
                         settings.STAGES['payment']['pay_info'])

    @patch('xbterminal.gui.stages.time.sleep')
    def test_server_error(self, sleep_mock):
        client_mock = Mock(**{
            'create_payment_order.side_effect': ServerError,
        })
        state = {
            'client': client_mock,
            'payment': {
                'fiat_amount': Decimal('1.00'),
            },
        }
        ui = Mock()
        next_stage = stages.pay_loading(state, ui)
        self.assertTrue(ui.showErrorScreen.called)
        self.assertEqual(ui.showErrorScreen.call_args[0][0],
                         'SERVER_ERROR')
        self.assertIsNone(state['payment']['fiat_amount'])
        self.assertEqual(next_stage,
                         settings.STAGES['idle'])


class PayInfoStageTestCase(unittest.TestCase):

    def test_cancel(self):
        client_mock = Mock(**{
            'cancel_payment.return_value': True,
        })
        state = {
            'client': client_mock,
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'pinfo_cancel_btn': True,
                'pinfo_pay_btn': False,
            },
            'payment': {
                'uid': 'testUid',
                'fiat_amount': Decimal('1.03'),
                'btc_amount': Decimal('0.123'),
                'exchange_rate': Decimal('234.55'),
                'payment_uri': 'test',
            },
        }
        ui = Mock()
        next_stage = stages.pay_info(state, ui)
        self.assertEqual(next_stage,
                         settings.STAGES['payment']['pay_amount'])
        self.assertEqual(client_mock.cancel_payment.call_args[1]['uid'],
                         'testUid')
        self.assertIsNone(state['payment']['uid'])
        self.assertIsNone(state['payment']['fiat_amount'])
        self.assertIsNone(state['payment']['btc_amount'])
        self.assertIsNone(state['payment']['exchange_rate'])
        self.assertIsNone(state['payment']['payment_uri'])
        self.assertFalse(any(state for state
                             in state['screen_buttons'].values()))

    def test_pay(self):
        state = {
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'pinfo_cancel_btn': False,
                'pinfo_pay_btn': True,
            },
            'payment': {
                'uid': 'testUid',
                'fiat_amount': Decimal('1.03'),
                'btc_amount': Decimal(0),
                'exchange_rate': Decimal(0),
                'payment_uri': 'test',
            },
        }
        ui = Mock()
        next_stage = stages.pay_info(state, ui)
        self.assertEqual(next_stage,
                         settings.STAGES['payment']['pay_wait'])
        self.assertEqual(ui.showScreen.call_args[0][0], 'pay_info')
        self.assertEqual(ui.setText.call_args_list[0][0][1], u'\xa31.03')
        self.assertFalse(any(state for state
                             in state['screen_buttons'].values()))


class PayWaitStageTestCase(unittest.TestCase):

    def test_cancel(self):
        client_mock = Mock(**{
            'start_bluetooth_server.return_value': True,
            'start_nfc_server.return_value': True,
            'stop_bluetooth_server.return_value': True,
            'stop_nfc_server.return_value': True,
            'host_add_credit.return_value': True,
            'cancel_payment.return_value': True,
        })
        state = {
            'client': client_mock,
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'pwait_cancel_btn': True,
            },
            'payment': {
                'uid': 'testUid',
                'fiat_amount': Decimal('1.00'),
                'btc_amount': Decimal(0),
                'exchange_rate': Decimal(0),
                'payment_uri': 'test',
            },
        }
        ui = Mock()
        next_stage = stages.pay_wait(state, ui)
        self.assertTrue(client_mock.start_bluetooth_server.called)
        self.assertTrue(client_mock.stop_bluetooth_server.called)
        self.assertFalse(client_mock.host_add_credit.called)
        self.assertTrue(client_mock.start_nfc_server.called)
        self.assertEqual(
            client_mock.start_nfc_server.call_args[1]['message'],
            'test')
        self.assertTrue(client_mock.stop_nfc_server.called)

        self.assertEqual(client_mock.cancel_payment.call_args[1]['uid'],
                         'testUid')
        self.assertIsNone(state['payment']['fiat_amount'])
        self.assertIsNone(state['payment']['payment_uri'])
        self.assertEqual(next_stage,
                         settings.STAGES['payment']['pay_amount'])
        self.assertFalse(any(state for state
                             in state['screen_buttons'].values()))

    def test_success(self):
        client_mock = Mock(**{
            'start_bluetooth_server.return_value': True,
            'start_nfc_server.return_value': True,
            'stop_bluetooth_server.return_value': True,
            'stop_nfc_server.return_value': True,
            'get_payment_status.return_value': 'notified',
            'get_payment_receipt.return_value': 'test_url',
            'host_add_credit.return_value': True,
        })
        state = {
            'client': client_mock,
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'pwait_cancel_btn': False,
            },
            'payment': {
                'uid': 'testUid',
                'fiat_amount': Decimal('1.00'),
                'btc_amount': Decimal(0),
                'exchange_rate': Decimal(0),
                'payment_uri': 'test',
            },
        }
        ui = Mock()
        next_stage = stages.pay_wait(state, ui)
        self.assertEqual(ui.showScreen.call_args[0][0],
                         'pay_wait')
        self.assertTrue(client_mock.start_bluetooth_server.called)
        self.assertTrue(client_mock.stop_bluetooth_server.called)
        self.assertTrue(client_mock.start_nfc_server.called)
        self.assertEqual(
            client_mock.start_nfc_server.call_args[1]['message'],
            'test')
        self.assertTrue(client_mock.stop_nfc_server.called)
        self.assertEqual(
            client_mock.get_payment_status.call_args[1]['uid'],
            'testUid')
        self.assertEqual(
            client_mock.get_payment_receipt.call_args[1]['uid'],
            'testUid')
        self.assertEqual(
            client_mock.host_add_credit.call_args[1]['fiat_amount'],
            Decimal('1.00'))
        self.assertEqual(state['payment']['receipt_url'], 'test_url')
        self.assertIsNotNone(state['payment']['uid'])
        self.assertEqual(next_stage,
                         settings.STAGES['payment']['pay_success'])

    def test_timeout(self):
        client_mock = Mock()
        state = {
            'client': client_mock,
            'keypad': Mock(last_key_pressed=None),
            'last_activity_timestamp': 0,
            'screen_buttons': {
                'pwait_cancel_btn': False,
            },
            'payment': {
                'uid': 'testUid',
                'fiat_amount': Decimal('1.00'),
                'btc_amount': Decimal(0),
                'exchange_rate': Decimal(0),
                'payment_uri': 'test',
            },
        }
        ui = Mock()
        next_stage = stages.pay_wait(state, ui)
        self.assertEqual(next_stage,
                         settings.STAGES['payment']['pay_cancel'])


class PaySuccessStageTestCase(unittest.TestCase):

    def test_no(self):
        state = {
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'psuccess_no_btn': True,
                'psuccess_yes_btn': False,
            },
            'payment': {
                'uid': 'testUid',
                'fiat_amount': Decimal('1.00'),
                'btc_amount': Decimal('0.12345678'),
                'receipt_url': 'test',
            },
        }
        ui = Mock()
        next_stage = stages.pay_success(state, ui)
        self.assertEqual(ui.showScreen.call_args_list[0][0][0],
                         'pay_success')
        self.assertEqual(ui.showScreen.call_args_list[1][0][0],
                         'load_indefinite')
        self.assertIsNone(state['payment']['uid'])
        self.assertIsNone(state['payment']['fiat_amount'])
        self.assertEqual(next_stage,
                         settings.STAGES['idle'])
        self.assertFalse(any(state for state
                             in state['screen_buttons'].values()))

    @patch('xbterminal.gui.stages.qr.qr_gen')
    def test_yes(self, qr_gen_mock):
        state = {
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'psuccess_no_btn': False,
                'psuccess_yes_btn': True,
            },
            'payment': {
                'uid': 'testUid',
                'fiat_amount': Decimal('1.00'),
                'btc_amount': Decimal('0.12345678'),
                'receipt_url': 'test',
            },
        }
        ui = Mock()
        next_stage = stages.pay_success(state, ui)
        self.assertEqual(next_stage,
                         settings.STAGES['payment']['pay_receipt'])
        self.assertIsNotNone(state['payment']['uid'])
        self.assertIsNotNone(state['payment']['receipt_url'])
        self.assertEqual(qr_gen_mock.call_args[0][0], 'test')
        self.assertFalse(any(state for state
                         in state['screen_buttons'].values()))


class PayReceiptStageTestCase(unittest.TestCase):

    def test_goback(self):
        client_mock = Mock(**{
            'start_nfc_server.return_value': True,
        })
        state = {
            'client': client_mock,
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'preceipt_goback_btn': True,
            },
            'payment': {
                'uid': 'testUid',
                'receipt_url': 'test',
            },
        }
        ui = Mock()
        next_stage = stages.pay_receipt(state, ui)
        self.assertEqual(ui.showScreen.call_args_list[0][0][0],
                         'pay_receipt')
        self.assertEqual(ui.showScreen.call_args_list[1][0][0],
                         'load_indefinite')
        self.assertEqual(
            client_mock.start_nfc_server.call_args[1]['message'],
            'test')
        self.assertTrue(client_mock.stop_nfc_server.called)
        self.assertIsNone(state['payment']['uid'])
        self.assertIsNone(state['payment']['fiat_amount'])
        self.assertIsNone(state['payment']['receipt_url'])
        self.assertEqual(next_stage,
                         settings.STAGES['idle'])
        self.assertFalse(any(state for state
                             in state['screen_buttons'].values()))


class PayCancelStageTestCase(unittest.TestCase):

    def test_return(self):
        state = {
            'keypad': Mock(last_key_pressed='enter'),
            'payment': {},
        }
        ui = Mock()
        next_stage = stages.pay_cancel(state, ui)
        self.assertEqual(ui.showScreen.call_args_list[0][0][0],
                         'pay_cancel')
        self.assertEqual(next_stage,
                         settings.STAGES['idle'])


class WithdrawSelectStageTestCase(unittest.TestCase):

    def test_fiat(self):
        client_mock = Mock(**{
            'host_pay_cash.return_value': True,
        })
        state = {
            'client': client_mock,
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'wselect_fiat_btn': True,
                'wselect_bitcoin_btn': False,
            },
            'withdrawal': {
                'fiat_amount': Decimal('1.00'),
            },
        }
        ui = Mock()
        next_stage = stages.withdraw_select(state, ui)
        self.assertTrue(client_mock.host_pay_cash.called)
        self.assertIsNone(state['withdrawal']['fiat_amount'])
        self.assertEqual(next_stage,
                         settings.STAGES['idle'])
        self.assertFalse(any(state for state
                             in state['screen_buttons'].values()))

    def test_bitcoin(self):
        client_mock = Mock()
        state = {
            'client': client_mock,
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'wselect_fiat_btn': False,
                'wselect_bitcoin_btn': True,
            },
            'withdrawal': {
                'fiat_amount': Decimal('1.00'),
            },
        }
        ui = Mock()
        next_stage = stages.withdraw_select(state, ui)
        self.assertEqual(ui.showScreen.call_args[0][0],
                         'withdraw_select')
        self.assertEqual(ui.setText.call_args[0][1],
                         u'£1.00')
        self.assertFalse(client_mock.host_pay_cash.called)
        self.assertIsNotNone(state['withdrawal']['fiat_amount'])
        self.assertEqual(next_stage,
                         settings.STAGES['withdrawal']['withdraw_loading1'])
        self.assertFalse(any(state for state
                             in state['screen_buttons'].values()))

    def test_return(self):
        client_mock = Mock()
        state = {
            'client': client_mock,
            'keypad': Mock(last_key_pressed='backspace'),
            'screen_buttons': {
                'wselect_fiat_btn': False,
                'wselect_bitcoin_btn': False,
            },
            'withdrawal': {
                'fiat_amount': Decimal('1.00'),
            },
        }
        ui = Mock()
        next_stage = stages.withdraw_select(state, ui)
        self.assertFalse(client_mock.host_pay_cash.called)
        self.assertIsNone(state['withdrawal']['fiat_amount'])
        self.assertEqual(next_stage,
                         settings.STAGES['idle'])


class WithdrawLoading1StageTestCase(unittest.TestCase):

    def test_proceed(self):
        client_mock = Mock(**{
            'create_withdrawal_order.return_value': {
                'uid': 'testUid',
                'btc_amount': Decimal('0.5'),
            },
        })
        state = {
            'client': client_mock,
            'withdrawal': {'fiat_amount': Decimal('1.00')},
        }
        ui = Mock()
        next_stage = stages.withdraw_loading1(state, ui)
        self.assertEqual(
            client_mock.create_withdrawal_order.call_args[1]['fiat_amount'],
            Decimal('1.00'))
        self.assertEqual(next_stage,
                         settings.STAGES['withdrawal']['withdraw_scan'])
        self.assertEqual(state['withdrawal']['uid'], 'testUid')
        self.assertEqual(state['withdrawal']['btc_amount'], Decimal('0.5'))

    @patch('xbterminal.gui.stages.time.sleep')
    def test_server_error(self, sleep_mock):
        client_mock = Mock(**{
            'create_withdrawal_order.side_effect': ServerError,
        })
        state = {
            'client': client_mock,
            'withdrawal': {
                'fiat_amount': Decimal('1.00'),
            },
        }
        ui = Mock()
        next_stage = stages.withdraw_loading1(state, ui)
        self.assertTrue(ui.showErrorScreen.called)
        self.assertEqual(ui.showErrorScreen.call_args[0][0],
                         'SERVER_ERROR')
        self.assertFalse(client_mock.cancel_withdrawal.called)
        self.assertIsNone(state['withdrawal']['uid'])
        self.assertIsNotNone(state['withdrawal']['fiat_amount'])
        self.assertEqual(next_stage,
                         settings.STAGES['withdrawal']['withdraw_select'])


class WithdrawScanStageTestCase(unittest.TestCase):

    def setUp(self):
        self.address = '1PWVL1fW7Ysomg9rXNsS8ng5ZzURa2p9vE'

    def test_return(self):
        client_mock = Mock(**{
            'start_qr_scanner.return_value': True,
            'get_scanned_address.return_value': None,
            'stop_qr_scanner.return_value': True,
        })
        state = {
            'client': client_mock,
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'wscan_goback_btn': True,
            },
            'gui_config': {},
            'withdrawal': {
                'uid': 'testUid',
                'fiat_amount': Decimal(0),
                'btc_amount': Decimal(0),
                'exchange_rate': Decimal(0),
            },
        }
        ui = Mock()
        next_stage = stages.withdraw_scan(state, ui)
        self.assertEqual(next_stage,
                         settings.STAGES['withdrawal']['withdraw_select'])
        self.assertTrue(client_mock.start_qr_scanner.called)
        self.assertTrue(client_mock.stop_qr_scanner.called)
        self.assertTrue(client_mock.cancel_withdrawal.call_args[1]['uid'],
                        'testUid')
        self.assertIsNone(state['withdrawal']['uid'])
        self.assertIsNotNone(state['withdrawal']['fiat_amount'])
        self.assertFalse(any(state for state
                             in state['screen_buttons'].values()))

    def test_proceed(self):
        client_mock = Mock(**{
            'start_qr_scanner.return_value': True,
            'get_scanned_address.return_value': self.address,
            'stop_qr_scanner.return_value': True,
        })
        state = {
            'client': client_mock,
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'wscan_goback_btn': False,
            },
            'gui_config': {},
            'withdrawal': {
                'uid': 'testUid',
                'fiat_amount': Decimal('1.12'),
                'btc_amount': Decimal('0.22354655'),
                'exchange_rate': Decimal('155.434'),
            },
        }
        ui = Mock()
        next_stage = stages.withdraw_scan(state, ui)
        self.assertEqual(ui.showScreen.call_args[0][0], 'withdraw_scan')
        self.assertEqual(ui.setText.call_args_list[0][0][1],
                         u'£1.12')
        self.assertEqual(ui.setText.call_args_list[2][0][1],
                         u'1 BTC = £155.43')
        self.assertTrue(client_mock.start_qr_scanner.called)
        self.assertTrue(client_mock.stop_qr_scanner.called)
        self.assertEqual(next_stage,
                         settings.STAGES['withdrawal']['withdraw_confirm'])
        self.assertIsNotNone(state['withdrawal']['address'])

    def test_default_address(self):
        client_mock = Mock(**{
            'start_qr_scanner.return_value': True,
            'get_scanned_address.return_value': None,
            'stop_qr_scanner.return_value': True,
        })
        state = {
            'client': client_mock,
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'wscan_goback_btn': False,
            },
            'gui_config': {'default_withdrawal_address': self.address},
            'withdrawal': {
                'uid': 'testUid',
                'fiat_amount': Decimal('1.12'),
                'btc_amount': Decimal('0.22354655'),
                'exchange_rate': Decimal('155.434'),
            },
        }
        ui = Mock()
        next_stage = stages.withdraw_scan(state, ui)
        self.assertTrue(client_mock.start_qr_scanner.called)
        self.assertTrue(client_mock.stop_qr_scanner.called)
        self.assertEqual(next_stage,
                         settings.STAGES['withdrawal']['withdraw_confirm'])
        self.assertEqual(state['withdrawal']['address'], self.address)

    def test_timeout(self):
        client_mock = Mock(**{
            'start_qr_scanner.return_value': True,
            'get_scanned_address.return_value': None,
            'stop_qr_scanner.return_value': True,
        })
        state = {
            'client': client_mock,
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'wscan_goback_btn': False,
            },
            'gui_config': {},
            'last_activity_timestamp': 0,
            'withdrawal': {
                'uid': 'testUid',
                'fiat_amount': Decimal(0),
                'btc_amount': Decimal(0),
                'exchange_rate': Decimal(0),
            },
        }
        ui = Mock()
        next_stage = stages.withdraw_scan(state, ui)
        self.assertEqual(next_stage,
                         settings.STAGES['withdrawal']['withdraw_select'])
        self.assertTrue(client_mock.stop_qr_scanner.called)
        self.assertFalse(client_mock.cancel_withdrawal.called)
        self.assertIsNone(state['withdrawal']['uid'])
        self.assertIsNotNone(state['withdrawal']['fiat_amount'])


class WithdrawConfirmStageTestCase(unittest.TestCase):

    def test_return(self):
        client_mock = Mock(**{
            'cancel_withdrawal.return_value': True,
        })
        state = {
            'client': client_mock,
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'wconfirm_confirm_btn': False,
                'wconfirm_cancel_btn': True,
            },
            'withdrawal': {
                'uid': 'testUid',
                'fiat_amount': Decimal(0),
                'btc_amount': Decimal(0),
                'exchange_rate': Decimal(0),
                'address': '1PWVL1fW7Ysomg9rXNsS8ng5ZzURa2p9vE',
            },
        }
        ui = Mock()
        next_stage = stages.withdraw_confirm(state, ui)
        self.assertEqual(next_stage,
                         settings.STAGES['withdrawal']['withdraw_select'])
        self.assertEqual(
            client_mock.cancel_withdrawal.call_args[1]['uid'],
            'testUid')
        self.assertIsNone(state['withdrawal']['uid'])
        self.assertIsNone(state['withdrawal']['address'])
        self.assertIsNotNone(state['withdrawal']['fiat_amount'])
        self.assertFalse(any(state for state
                             in state['screen_buttons'].values()))

    def test_proceed(self):
        state = {
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'wconfirm_confirm_btn': True,
                'wconfirm_cancel_btn': False,
            },
            'withdrawal': {
                'uid': 'testUid',
                'fiat_amount': Decimal('5.12'),
                'btc_amount': Decimal('0.34434334'),
                'exchange_rate': Decimal('553.12'),
                'address': '1PWVL1fW7Ysomg9rXNsS8ng5ZzURa2p9vE',
            },
        }
        ui = Mock()
        next_stage = stages.withdraw_confirm(state, ui)
        self.assertEqual(ui.showScreen.call_args[0][0], 'withdraw_confirm')
        self.assertEqual(ui.setText.call_args_list[0][0][1],
                         '1PWVL1fW7Ysomg9rXNsS8ng5ZzURa2p9vE')
        self.assertEqual(ui.setText.call_args_list[1][0][1],
                         u'£5.12')
        self.assertEqual(ui.setText.call_args_list[3][0][1],
                         u'1 BTC = £553.12')
        self.assertEqual(next_stage,
                         settings.STAGES['withdrawal']['withdraw_loading2'])
        self.assertFalse(any(state for state
                             in state['screen_buttons'].values()))


class WithdrawLoading2StageTestCase(unittest.TestCase):

    def test_proceed(self):
        client_mock = Mock(**{
            'get_withdrawal_status.return_value': 'completed',
            'confirm_withdrawal.return_value': {
                'btc_amount': Decimal('0.41'),
                'exchange_rate': Decimal('202.0'),
            },
            'get_withdrawal_receipt.return_value': 'test_url',
        })
        state = {
            'client': client_mock,
            'withdrawal': {
                'uid': 'testUid',
                'fiat_amount': Decimal('0.50'),
                'btc_amount': Decimal('0.4'),
                'exchange_rate': Decimal('201.0'),
                'address': '1PWVL1fW7Ysomg9rXNsS8ng5ZzURa2p9vE',
            },
        }
        ui = Mock()
        next_stage = stages.withdraw_loading2(state, ui)
        self.assertEqual(client_mock.get_withdrawal_status.call_count, 1)
        self.assertEqual(
            client_mock.confirm_withdrawal.call_args[1]['uid'],
            'testUid')
        self.assertEqual(next_stage,
                         settings.STAGES['withdrawal']['withdraw_success'])
        self.assertEqual(state['withdrawal']['btc_amount'], Decimal('0.41'))
        self.assertEqual(state['withdrawal']['exchange_rate'],
                         Decimal('202.0'))
        self.assertEqual(state['withdrawal']['receipt_url'], 'test_url')

    @patch('xbterminal.gui.stages.time.sleep')
    def test_server_error(self, sleep_mock):
        client_mock = Mock(**{
            'get_withdrawal_status.return_value': 'new',
            'confirm_withdrawal.side_effect': ServerError,
        })
        state = {
            'client': client_mock,
            'withdrawal': {
                'uid': 'testUid',
                'fiat_amount': Decimal('0.50'),
                'address': '1PWVL1fW7Ysomg9rXNsS8ng5ZzURa2p9vE',
            },
        }
        ui = Mock()
        next_stage = stages.withdraw_loading2(state, ui)
        self.assertEqual(
            client_mock.confirm_withdrawal.call_args[1]['uid'],
            'testUid')
        self.assertTrue(ui.showErrorScreen.called)
        self.assertEqual(ui.showErrorScreen.call_args[0][0],
                         'SERVER_ERROR')
        self.assertFalse(client_mock.cancel_withdrawal.called)
        self.assertEqual(next_stage,
                         settings.STAGES['withdrawal']['withdraw_select'])
        self.assertIsNone(state['withdrawal']['uid'])
        self.assertIsNone(state['withdrawal']['address'])
        self.assertIsNotNone(state['withdrawal']['fiat_amount'])


class WithdrawSuccessStageTestCase(unittest.TestCase):

    def test_no(self):
        state = {
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'wsuccess_no_btn': True,
                'wsuccess_yes_btn': False,
            },
            'withdrawal': {
                'fiat_amount': Decimal('1.00'),
                'btc_amount': Decimal('0.12345678'),
                'receipt_url': 'test',
            },
        }
        ui = Mock()
        next_stage = stages.withdraw_success(state, ui)
        self.assertEqual(ui.showScreen.call_args_list[0][0][0],
                         'withdraw_success')
        self.assertEqual(ui.showScreen.call_args_list[1][0][0],
                         'load_indefinite')
        self.assertIsNone(state['withdrawal']['uid'])
        self.assertIsNone(state['withdrawal']['fiat_amount'])
        self.assertEqual(next_stage,
                         settings.STAGES['idle'])
        self.assertFalse(any(state for state
                             in state['screen_buttons'].values()))

    @patch('xbterminal.gui.stages.qr.qr_gen')
    def test_yes(self, qr_gen_mock):
        state = {
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'wsuccess_no_btn': False,
                'wsuccess_yes_btn': True,
            },
            'withdrawal': {
                'uid': 'testUid',
                'fiat_amount': Decimal('1.00'),
                'btc_amount': Decimal('0.12345678'),
                'receipt_url': 'test',
            },
        }
        ui = Mock()
        next_stage = stages.withdraw_success(state, ui)
        self.assertEqual(next_stage,
                         settings.STAGES['withdrawal']['withdraw_receipt'])
        self.assertIsNotNone(state['withdrawal']['receipt_url'])
        self.assertEqual(qr_gen_mock.call_args[0][0], 'test')
        self.assertFalse(any(state for state
                         in state['screen_buttons'].values()))


class WithdrawReceiptStageTestCase(unittest.TestCase):

    def test_goback(self):
        client_mock = Mock(**{
            'start_nfc_server.return_value': True,
            'stop_nfc_server.return_value': True,
        })
        state = {
            'client': client_mock,
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'wreceipt_goback_btn': True,
            },
            'withdrawal': {
                'uid': 'testUid',
                'fiat_amount': Decimal('1.00'),
                'receipt_url': 'test',
            },
        }
        ui = Mock()
        next_stage = stages.withdraw_receipt(state, ui)
        self.assertEqual(ui.showScreen.call_args_list[0][0][0],
                         'withdraw_receipt')
        self.assertEqual(ui.showScreen.call_args_list[1][0][0],
                         'load_indefinite')
        self.assertEqual(
            client_mock.start_nfc_server.call_args[1]['message'],
            'test')
        self.assertTrue(client_mock.stop_nfc_server.called)
        self.assertIsNone(state['withdrawal']['uid'])
        self.assertIsNone(state['withdrawal']['fiat_amount'])
        self.assertEqual(next_stage,
                         settings.STAGES['idle'])
        self.assertFalse(any(state for state
                             in state['screen_buttons'].values()))
