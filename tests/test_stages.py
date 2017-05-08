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
                'status': 'active',
            },
            'screen_buttons': {
                'idle_begin_btn': True,
                'idle_help_btn': False,
                'standby_wake_btn': False,
            },
            'is_suspended': False,
        }
        ui = Mock()
        next_stage = stages.idle(state, ui)
        self.assertEqual(ui.showScreen.call_args[0][0], 'idle')
        self.assertEqual(
            client_mock.start_nfc_server.call_args[1]['message'],
            'http://www.apmodule.co.uk/')
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
                'status': 'active',
            },
            'keypad': keypad,
            'screen_buttons': {
                'idle_begin_btn': False,
                'idle_help_btn': False,
                'standby_wake_btn': False,
            },
            'is_suspended': False,
        }
        ui = Mock()
        next_stage = stages.idle(state, ui)
        self.assertEqual(next_stage,
                         settings.STAGES['payment']['pay_amount'])

    def test_help_button(self):
        client_mock = Mock()
        state = {
            'client': client_mock,
            'remote_config': {
                'status': 'active',
            },
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'idle_begin_btn': False,
                'idle_help_btn': True,
                'standby_wake_btn': False,
            },
            'is_suspended': False,
        }
        ui = Mock()
        next_stage = stages.idle(state, ui)
        self.assertIs(client_mock.stop_nfc_server.called, True)
        self.assertEqual(next_stage, settings.STAGES['help'])
        self.assertFalse(any(state for state
                             in state['screen_buttons'].values()))

    def test_host_system_payout(self):
        client_mock = Mock(**{
            'host_get_payout.return_value': Decimal('0.15'),
        })
        state = {
            'client': client_mock,
            'remote_config': {
                'status': 'active',
            },
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'idle_begin_btn': False,
                'idle_help_btn': False,
                'standby_wake_btn': False,
            },
            'is_suspended': False,
            'withdrawal': {},
        }
        ui = Mock()
        next_stage = stages.idle(state, ui)
        self.assertTrue(client_mock.host_get_payout.called)
        self.assertTrue(client_mock.stop_nfc_server.called)
        self.assertEqual(next_stage,
                         settings.STAGES['withdrawal']['withdraw_wait'])
        self.assertEqual(state['withdrawal']['fiat_amount'], Decimal('0.15'))

    def test_alt_key_input(self):
        client_mock = Mock()
        keypad = Mock(last_key_pressed='alt')
        state = {
            'client': client_mock,
            'remote_config': {
                'status': 'active',
            },
            'keypad': keypad,
            'gui_config': {'default_withdrawal_amount': '0.23'},
            'screen_buttons': {
                'idle_begin_btn': False,
                'idle_help_btn': False,
                'standby_wake_btn': False,
            },
            'is_suspended': False,
            'withdrawal': {},
        }
        ui = Mock()
        next_stage = stages.idle(state, ui)
        self.assertTrue(client_mock.host_get_payout.called)
        self.assertEqual(next_stage,
                         settings.STAGES['withdrawal']['withdraw_wait'])
        self.assertEqual(state['withdrawal']['fiat_amount'], Decimal('0.23'))

    @patch('xbterminal.gui.stages.time.sleep')
    def test_standby(self, sleep_mock):
        client_mock = Mock(**{'host_get_payout.return_value': None})
        keypad = Mock(last_key_pressed=None)
        state = {
            'last_activity_timestamp': 0,
            'client': client_mock,
            'remote_config': {
                'status': 'active',
            },
            'keypad': keypad,
            'screen_buttons': {
                'idle_begin_btn': False,
                'idle_help_btn': False,
                'standby_wake_btn': False,
            },
            'is_suspended': False,
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

    @patch('xbterminal.gui.stages.time.sleep')
    def test_suspended(self, sleep_mock):
        client_mock = Mock()
        state = {
            'client': client_mock,
            'remote_config': {
                'remote_server': 'https://xbterminal.io',
                'status': 'suspended',
            },
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'idle_begin_btn': False,
                'standby_wake_btn': False,
            },
            'is_suspended': False,
            'withdrawal': {},
        }
        ui = Mock()
        sleep_mock.side_effect = ValueError  # Break cycle on first iter
        with self.assertRaises(ValueError):
            stages.idle(state, ui)
        self.assertIs(client_mock.disable_display.called, True)
        self.assertIs(client_mock.host_get_payout.called, False)
        self.assertIs(client_mock.stop_nfc_server.called, False)
        self.assertIs(state['is_suspended'], True)

    def test_reenabled(self):
        client_mock = Mock()
        state = {
            'client': client_mock,
            'remote_config': {
                'remote_server': 'https://xbterminal.io',
                'status': 'active',
            },
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'idle_begin_btn': True,
                'standby_wake_btn': False,
            },
            'is_suspended': True,
            'withdrawal': {},
        }
        ui = Mock()
        next_stage = stages.idle(state, ui)
        self.assertEqual(next_stage,
                         settings.STAGES['payment']['pay_amount'])
        self.assertIs(client_mock.enable_display.called, True)
        self.assertIs(state['is_suspended'], False)


class HelpStageTestCase(unittest.TestCase):

    @patch('xbterminal.gui.stages.qr.qr_gen')
    def test_goback_button(self, qr_gen_mock):
        client_mock = Mock(**{
            'start_nfc_server.return_value': True,
        })
        qr_gen_mock.return_value = 'image'
        state = {
            'client': client_mock,
            'remote_config': {},
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'help_goback_btn': True,
            },
        }
        ui = Mock()
        next_stage = stages.help(state, ui)
        self.assertEqual(ui.showScreen.call_args[0][0], 'help')
        self.assertEqual(ui.setImage.call_args[0][1], 'image')
        self.assertEqual(ui.setText.call_args[0][1],
                         'http://www.apmodule.co.uk/')
        self.assertIs(client_mock.start_nfc_server.called, True)
        self.assertIs(client_mock.stop_nfc_server.called, True)
        self.assertEqual(next_stage, settings.STAGES['idle'])


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
        client_mock = Mock(**{'host_get_payout.return_value': None})
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
        client_mock = Mock(**{'host_get_payout.return_value': None})
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
        client_mock = Mock(**{'host_get_payout.return_value': None})
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
        client_mock = Mock(**{'host_get_payout.return_value': None})
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

    def test_host_system_payout(self):
        client_mock = Mock(**{
            'host_get_payout.return_value': Decimal('10.0'),
        })
        state = {
            'client': client_mock,
            'keypad': Mock(last_key_pressed=None),
            'remote_config': self.remote_config,
            'screen_buttons': {
                'pamount_opt1_btn': False,
                'pamount_opt2_btn': False,
                'pamount_opt3_btn': False,
            },
            'payment': {},
            'withdrawal': {},
        }
        ui = Mock()
        next_stage = stages.pay_amount(state, ui)
        self.assertEqual(state['withdrawal']['fiat_amount'],
                         Decimal('10.00'))
        self.assertEqual(next_stage,
                         settings.STAGES['withdrawal']['withdraw_loading1'])

    def test_timeout(self):
        client_mock = Mock(**{'host_get_payout.return_value': None})
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
            'withdrawal': {},
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
        qr_gen_mock.return_value = 'image'
        state = {
            'client': client_mock,
            'payment': {
                'fiat_amount': Decimal('1.00'),
            },
        }
        ui = Mock()
        next_stage = stages.pay_loading(state, ui)
        self.assertEqual(ui.showScreen.call_args[0][0],
                         'pay_loading')
        self.assertEqual(
            client_mock.create_payment_order.call_args[1]['fiat_amount'],
            Decimal('1.00'))
        self.assertEqual(state['payment']['uid'], 'testUid')
        self.assertEqual(qr_gen_mock.call_args[0][0], 'test')
        self.assertEqual(state['payment']['qrcode'], 'image')
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

    def test_host_system_payout(self):
        client_mock = Mock(**{
            'host_get_payout.return_value': Decimal('10.0'),
        })
        state = {
            'client': client_mock,
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'pinfo_cancel_btn': False,
                'pinfo_pay_btn': False,
            },
            'payment': {
                'uid': 'testUid',
                'fiat_amount': Decimal('5.0'),
                'btc_amount': Decimal('0.05'),
                'exchange_rate': Decimal('100'),
            },
            'withdrawal': {},
        }
        ui = Mock()
        next_stage = stages.pay_info(state, ui)
        self.assertIsNone(state['payment']['uid'])
        self.assertIs(client_mock.cancel_payment.called, True)
        self.assertEqual(state['withdrawal']['fiat_amount'],
                         Decimal('10.0'))
        self.assertEqual(next_stage,
                         settings.STAGES['withdrawal']['withdraw_loading1'])


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
                'pwait_cancel_refund_btn': False,
            },
            'payment': {
                'uid': 'testUid',
                'fiat_amount': Decimal('1.00'),
                'btc_amount': Decimal(0),
                'exchange_rate': Decimal(0),
                'payment_uri': 'test',
                'qrcode': 'image',
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
        self.assertIsNone(state['payment']['qrcode'])
        self.assertEqual(next_stage,
                         settings.STAGES['payment']['pay_amount'])
        self.assertFalse(any(state for state
                             in state['screen_buttons'].values()))

    def test_received(self):
        client_mock = Mock(**{
            'start_bluetooth_server.return_value': True,
            'start_nfc_server.return_value': True,
            'stop_bluetooth_server.return_value': True,
            'stop_nfc_server.return_value': True,
            'get_payment_status.return_value': {
                'paid_btc_amount': Decimal('0.05'),
                'status': 'received',
            },
        })
        state = {
            'client': client_mock,
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'pwait_cancel_btn': False,
                'pwait_cancel_refund_btn': False,
            },
            'payment': {
                'uid': 'testUid',
                'fiat_amount': Decimal('1.00'),
                'btc_amount': Decimal('0.05'),
                'exchange_rate': Decimal('20'),
                'payment_uri': 'test',
                'qrcode': 'image',
            },
        }
        ui = Mock()
        next_stage = stages.pay_wait(state, ui)
        self.assertEqual(ui.showScreen.call_args[0][0],
                         'pay_wait')
        self.assertEqual(ui.setImage.call_args[0][1],
                         state['payment']['qrcode'])
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
        self.assertIsNotNone(state['payment']['uid'])
        self.assertFalse(ui.showWidget.called)
        self.assertFalse(ui.hideWidget.called)
        self.assertEqual(next_stage,
                         settings.STAGES['payment']['pay_progress'])

    @patch('xbterminal.gui.stages._wait_for_screen_timeout')
    def test_underpaid(self, wait_for_mock):
        client_mock = Mock(**{
            'get_payment_status.side_effect': [{
                'paid_btc_amount': Decimal('0.05'),
                'status': 'underpaid',
            }, {
                'paid_btc_amount': Decimal('0.1'),
                'status': 'received',
            }],
        })
        state = {
            'client': client_mock,
            'keypad': Mock(last_key_pressed=None),
            'last_activity_timestamp': 0,
            'screen_buttons': {
                'pwait_cancel_btn': False,
                'pwait_cancel_refund_btn': False,
            },
            'payment': {
                'uid': 'testUid',
                'fiat_amount': Decimal('1.00'),
                'btc_amount': Decimal('0.1'),
                'exchange_rate': Decimal('20'),
                'payment_uri': 'test',
                'qrcode': 'image',
            },
        }
        ui = Mock()
        next_stage = stages.pay_wait(state, ui)
        self.assertEqual(ui.showWidget.call_args_list[0][0][0],
                         'pwait_paid_lbl')
        self.assertEqual(ui.showWidget.call_args_list[1][0][0],
                         'pwait_paid_btc_amount_lbl')
        self.assertEqual(ui.showWidget.call_args_list[2][0][0],
                         'pwait_cancel_refund_btn')
        self.assertEqual(ui.hideWidget.call_args[0][0],
                         'pwait_cancel_btn')
        self.assertEqual(next_stage,
                         settings.STAGES['payment']['pay_progress'])

    def test_timeout(self):
        client_mock = Mock(**{
            'get_payment_status.return_value': {
                'paid_btc_amount': Decimal(0),
                'status': 'new',
            },
        })
        state = {
            'client': client_mock,
            'keypad': Mock(last_key_pressed=None),
            'last_activity_timestamp': 0,
            'screen_buttons': {
                'pwait_cancel_btn': False,
                'pwait_cancel_refund_btn': False,
            },
            'payment': {
                'uid': 'testUid',
                'fiat_amount': Decimal('1.00'),
                'btc_amount': Decimal(0),
                'exchange_rate': Decimal(0),
                'payment_uri': 'test',
                'qrcode': 'image',
            },
        }
        ui = Mock()
        next_stage = stages.pay_wait(state, ui)
        self.assertEqual(next_stage,
                         settings.STAGES['payment']['pay_cancel'])


class PayProgressStageTestCase(unittest.TestCase):

    @patch('xbterminal.gui.stages.qr.qr_gen')
    @patch('xbterminal.gui.stages.time.sleep')
    def test_proceed(self, sleep_mock, qr_gen_mock):
        client_mock = Mock(**{
            'get_payment_status.return_value': {
                'paid_btc_amount': Decimal('0.05'),
                'status': 'notified',
            },
            'get_payment_receipt.return_value': 'test_url',
            'host_add_credit.return_value': True,
        })
        qr_gen_mock.return_value = 'image'
        state = {
            'client': client_mock,
            'keypad': Mock(last_key_pressed=None),
            'payment': {
                'uid': 'testUid',
                'fiat_amount': Decimal('1.00'),
                'btc_amount': Decimal('0.05'),
                'exchange_rate': Decimal('20'),
                'payment_uri': 'test',
            },
        }
        ui = Mock()
        next_stage = stages.pay_progress(state, ui)
        self.assertEqual(ui.showScreen.call_args[0][0],
                         'pay_progress')
        self.assertEqual(ui.setText.call_count, 4)
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
        self.assertEqual(qr_gen_mock.call_args[0][0], 'test_url')
        self.assertEqual(state['payment']['qrcode'], 'image')
        self.assertIsNotNone(state['payment']['uid'])
        self.assertEqual(next_stage,
                         settings.STAGES['payment']['pay_receipt'])


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
                'btc_amount': Decimal('0.05'),
                'receipt_url': 'test',
                'qrcode': 'image',
            },
        }
        ui = Mock()
        next_stage = stages.pay_receipt(state, ui)
        self.assertEqual(ui.showScreen.call_args_list[0][0][0],
                         'pay_receipt')
        self.assertEqual(ui.showScreen.call_args_list[1][0][0],
                         'load_indefinite')
        self.assertIn('50.00', ui.setText.call_args_list[0][0][1])
        self.assertEqual(ui.setImage.call_args[0][1],
                         state['payment']['qrcode'])
        self.assertEqual(
            client_mock.start_nfc_server.call_args[1]['message'],
            'test')
        self.assertTrue(client_mock.stop_nfc_server.called)
        self.assertIsNone(state['payment']['uid'])
        self.assertIsNone(state['payment']['fiat_amount'])
        self.assertIsNone(state['payment']['receipt_url'])
        self.assertIsNone(state['payment']['qrcode'])
        self.assertEqual(next_stage,
                         settings.STAGES['idle'])
        self.assertFalse(any(state for state
                             in state['screen_buttons'].values()))

    def test_host_system_payout(self):
        client_mock = Mock(**{
            'host_get_payout.return_value': Decimal('10.0'),
        })
        state = {
            'client': client_mock,
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'preceipt_goback_btn': False,
            },
            'payment': {
                'uid': 'testUid',
                'btc_amount': Decimal('0.05'),
                'receipt_url': 'test',
                'qrcode': 'image',
            },
            'withdrawal': {},
        }
        ui = Mock()
        next_stage = stages.pay_receipt(state, ui)
        self.assertIs(client_mock.stop_nfc_server.called, True)
        self.assertIsNone(state['payment']['uid'])
        self.assertEqual(state['withdrawal']['fiat_amount'],
                         Decimal('10.0'))
        self.assertEqual(next_stage,
                         settings.STAGES['withdrawal']['withdraw_loading1'])


class PayCancelStageTestCase(unittest.TestCase):

    def test_return(self):
        state = {
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'pcancel_goback_btn': True,
            },
            'payment': {},
        }
        ui = Mock()
        next_stage = stages.pay_cancel(state, ui)
        self.assertEqual(ui.showScreen.call_args_list[0][0][0],
                         'pay_cancel')
        self.assertEqual(next_stage,
                         settings.STAGES['payment']['pay_amount'])

    def test_host_system_payout(self):
        client_mock = Mock(**{
            'host_get_payout.return_value': Decimal('10.0'),
        })
        state = {
            'client': client_mock,
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'pcancel_goback_btn': False,
            },
            'payment': {},
            'withdrawal': {},
        }
        ui = Mock()
        next_stage = stages.pay_cancel(state, ui)
        self.assertEqual(state['withdrawal']['fiat_amount'],
                         Decimal('10.0'))
        self.assertEqual(next_stage,
                         settings.STAGES['withdrawal']['withdraw_loading1'])


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
                         settings.STAGES['withdrawal']['withdraw_wait'])
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


class WithdrawWaitStageTestCase(unittest.TestCase):

    def test_return(self):
        client_mock = Mock()
        state = {
            'client': client_mock,
            'keypad': Mock(last_key_pressed='backspace'),
            'screen_buttons': {
                'wwait_scan_btn': False,
            },
            'gui_config': {},
            'withdrawal': {
                'fiat_amount': Decimal(0),
            },
        }
        ui = Mock()
        next_stage = stages.withdraw_wait(state, ui)
        self.assertEqual(next_stage,
                         settings.STAGES['idle'])
        self.assertIsNone(state['withdrawal']['fiat_amount'])
        self.assertFalse(any(state for state
                             in state['screen_buttons'].values()))

    def test_proceed(self):
        client_mock = Mock()
        state = {
            'client': client_mock,
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'wwait_scan_btn': True,
            },
            'gui_config': {},
            'withdrawal': {
                'fiat_amount': Decimal('1.12'),
            },
        }
        ui = Mock()
        next_stage = stages.withdraw_wait(state, ui)
        self.assertEqual(ui.showScreen.call_args[0][0], 'withdraw_wait')
        self.assertEqual(ui.setText.call_args_list[0][0][1],
                         u'£1.12')
        self.assertEqual(next_stage,
                         settings.STAGES['withdrawal']['withdraw_scan'])


class WithdrawScanStageTestCase(unittest.TestCase):

    def setUp(self):
        self.address = '1PWVL1fW7Ysomg9rXNsS8ng5ZzURa2p9vE'

    def test_scan(self):
        client_mock = Mock(**{
            'start_qr_scanner.return_value': True,
            'get_scanned_address.return_value': self.address,
            'stop_qr_scanner.return_value': True,
        })
        state = {
            'client': client_mock,
            'keypad': Mock(last_key_pressed=None),
            'gui_config': {},
            'withdrawal': {
                'fiat_amount': Decimal('1.12'),
            },
        }
        ui = Mock()
        next_stage = stages.withdraw_scan(state, ui)
        self.assertEqual(ui.showScreen.call_args[0][0], 'withdraw_scan')
        self.assertTrue(client_mock.start_qr_scanner.called)
        self.assertTrue(client_mock.stop_qr_scanner.called)
        self.assertEqual(next_stage,
                         settings.STAGES['withdrawal']['withdraw_loading1'])
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
            'gui_config': {'default_withdrawal_address': self.address},
            'withdrawal': {
                'fiat_amount': Decimal('1.12'),
            },
        }
        ui = Mock()
        next_stage = stages.withdraw_scan(state, ui)
        self.assertTrue(client_mock.start_qr_scanner.called)
        self.assertTrue(client_mock.stop_qr_scanner.called)
        self.assertEqual(next_stage,
                         settings.STAGES['withdrawal']['withdraw_loading1'])
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
            'gui_config': {},
            'last_activity_timestamp': 0,
            'withdrawal': {
                'fiat_amount': Decimal('1.12'),
            },
        }
        ui = Mock()
        next_stage = stages.withdraw_scan(state, ui)
        self.assertIs(client_mock.cancel_withdrawal.called, False)
        self.assertIsNotNone(state['withdrawal']['fiat_amount'])
        self.assertEqual(next_stage,
                         settings.STAGES['withdrawal']['withdraw_wait'])


class WithdrawLoading1StageTestCase(unittest.TestCase):

    def test_proceed(self):
        client_mock = Mock(**{
            'create_withdrawal_order.return_value': {
                'uid': 'testUid',
                'btc_amount': Decimal('0.5'),
                'tx_fee_btc_amount': Decimal('0.0001'),
            },
        })
        state = {
            'client': client_mock,
            'withdrawal': {'fiat_amount': Decimal('1.00')},
        }
        ui = Mock()
        next_stage = stages.withdraw_loading1(state, ui)
        self.assertEqual(ui.showScreen.call_args[0][0], 'withdraw_loading')
        self.assertIn('1.00', ui.setText.call_args[0][1])
        self.assertEqual(
            client_mock.create_withdrawal_order.call_args[1]['fiat_amount'],
            Decimal('1.00'))
        self.assertEqual(next_stage,
                         settings.STAGES['withdrawal']['withdraw_confirm'])
        self.assertEqual(state['withdrawal']['uid'], 'testUid')
        self.assertEqual(state['withdrawal']['btc_amount'], Decimal('0.5'))
        self.assertEqual(state['withdrawal']['tx_fee_btc_amount'],
                         Decimal('0.0001'))

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
                         settings.STAGES['withdrawal']['withdraw_wait'])

    @patch('xbterminal.gui.stages.time.sleep')
    def test_max_payout_error(self, sleep_mock):
        client_mock = Mock(**{
            'create_withdrawal_order.side_effect': ServerError({
                'device': ['Amount exceeds max payout for current device.'],
            }),
        })
        state = {
            'client': client_mock,
            'withdrawal': {
                'fiat_amount': Decimal('1.00'),
            },
        }
        ui = Mock()
        next_stage = stages.withdraw_loading1(state, ui)
        self.assertEqual(ui.showErrorScreen.call_args[0][0],
                         'MAX_PAYOUT_ERROR')
        self.assertEqual(next_stage,
                         settings.STAGES['withdrawal']['withdraw_wait'])


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
                'tx_fee_btc_amount': Decimal('0.0001'),
                'exchange_rate': Decimal(0),
                'address': '1PWVL1fW7Ysomg9rXNsS8ng5ZzURa2p9vE',
            },
        }
        ui = Mock()
        next_stage = stages.withdraw_confirm(state, ui)
        self.assertEqual(next_stage,
                         settings.STAGES['withdrawal']['withdraw_wait'])
        self.assertIs(client_mock.cancel_withdrawal.called, True)
        self.assertIsNone(state['withdrawal']['uid'])
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
                'tx_fee_btc_amount': Decimal('0.0001'),
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
        self.assertIn('0.10', ui.setText.call_args_list[4][0][1])
        self.assertEqual(ui.setText.call_count, 5)
        self.assertEqual(next_stage,
                         settings.STAGES['withdrawal']['withdraw_loading2'])
        self.assertFalse(any(state for state
                             in state['screen_buttons'].values()))


class WithdrawLoading2StageTestCase(unittest.TestCase):

    @patch('xbterminal.gui.stages.qr.qr_gen')
    def test_proceed(self, qr_gen_mock):
        client_mock = Mock(**{
            'get_withdrawal_status.return_value': 'completed',
            'confirm_withdrawal.return_value': {
                'btc_amount': Decimal('0.41'),
                'exchange_rate': Decimal('202.0'),
            },
            'get_withdrawal_receipt.return_value': 'test_url',
        })
        qr_gen_mock.return_value = 'image'
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
        self.assertEqual(ui.showScreen.call_args[0][0], 'withdraw_loading')
        self.assertIn('400.00', ui.setText.call_args[0][1])
        self.assertEqual(client_mock.get_withdrawal_status.call_count, 1)
        self.assertEqual(
            client_mock.confirm_withdrawal.call_args[1]['uid'],
            'testUid')
        self.assertEqual(qr_gen_mock.call_args[0][0], 'test_url')
        self.assertEqual(state['withdrawal']['qrcode'], 'image')
        self.assertEqual(next_stage,
                         settings.STAGES['withdrawal']['withdraw_receipt'])
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
                'btc_amount': Decimal('0.4'),
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
        self.assertIs(client_mock.cancel_withdrawal.called, False)
        self.assertEqual(next_stage,
                         settings.STAGES['withdrawal']['withdraw_confirm'])
        self.assertIsNotNone(state['withdrawal']['uid'])
        self.assertIsNotNone(state['withdrawal']['address'])
        self.assertIsNotNone(state['withdrawal']['fiat_amount'])


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
                'btc_amount': Decimal('0.05'),
                'receipt_url': 'test',
                'qrcode': 'image',
            },
        }
        ui = Mock()
        next_stage = stages.withdraw_receipt(state, ui)
        self.assertEqual(ui.showScreen.call_args_list[0][0][0],
                         'withdraw_receipt')
        self.assertEqual(ui.showScreen.call_args_list[1][0][0],
                         'load_indefinite')
        self.assertIn('50.00', ui.setText.call_args_list[0][0][1])
        self.assertEqual(ui.setImage.call_args[0][1],
                         state['withdrawal']['qrcode'])
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
