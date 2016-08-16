# -*- coding: utf-8 -*-
from decimal import Decimal
from mock import patch, Mock
import unittest

from xbterminal import defaults
from xbterminal.stages import stages
from xbterminal.exceptions import ServerError


patcher = patch.dict(
    'xbterminal.stages.amounts.state',
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
        run = {
            'remote_config': {
                'status': 'active',
                'language': {'code': 'en'},
                'currency': {'prefix': '$'},
            },
        }
        ui = Mock()
        next_stage = stages.bootup(run, ui)
        self.assertEqual(ui.showScreen.call_args[0][0], 'load_indefinite')
        self.assertEqual(next_stage, defaults.STAGES['idle'])

    def test_registration(self):
        run = {
            'remote_config': {
                'status': 'activation',
                'language': {'code': 'en'},
                'currency': {'prefix': '$'},
            },
        }
        ui = Mock()
        next_stage = stages.bootup(run, ui)
        self.assertEqual(ui.showScreen.call_args[0][0], 'load_indefinite')
        self.assertEqual(next_stage, defaults.STAGES['activate'])


class ActivateStageTestCase(unittest.TestCase):

    def test_proceed(self):
        client_mock = Mock(**{
            'get_activation_code.return_value': 'testCode',
        })
        run = {
            'client': client_mock,
            'remote_config': {
                'remote_server': 'https://xbterminal.io',
                'status': 'active',
            },
        }
        ui = Mock()
        next_stage = stages.activate(run, ui)
        self.assertTrue(client_mock.get_activation_code.called)
        self.assertEqual(ui.showScreen.call_args[0][0], 'activation')
        self.assertEqual(ui.setText.call_args_list[0][0][1],
                         'xbterminal.io')
        self.assertEqual(ui.setText.call_args_list[1][0][1],
                         'testCode')
        self.assertEqual(next_stage, defaults.STAGES['idle'])


class IdleStageTestCase(unittest.TestCase):

    def test_begin_button(self):
        run = {
            'screen_buttons': {'idle_begin_btn': True},
        }
        ui = Mock()
        next_stage = stages.idle(run, ui)
        self.assertEqual(ui.showScreen.call_args[0][0], 'idle')
        self.assertEqual(next_stage,
                         defaults.STAGES['payment']['pay_amount'])
        self.assertFalse(any(state for state
                             in run['screen_buttons'].values()))

    def test_enter_key_input(self):
        keypad = Mock(last_key_pressed='enter')
        run = {
            'keypad': keypad,
            'screen_buttons': {'idle_begin_btn': False},
        }
        ui = Mock()
        next_stage = stages.idle(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['payment']['pay_amount'])

    def test_host_system_payout(self):
        client_mock = Mock(**{
            'host_get_payout.return_value': Decimal('0.15'),
        })
        run = {
            'client': client_mock,
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {'idle_begin_btn': False},
        }
        ui = Mock()
        next_stage = stages.idle(run, ui)
        self.assertTrue(client_mock.host_get_payout.called)
        self.assertEqual(next_stage,
                         defaults.STAGES['selection'])


class SelectionStageTestCase(unittest.TestCase):

    def test_pay_button(self):
        client_mock = Mock(**{
            'host_get_payout.return_value': Decimal('0.15'),
        })
        run = {
            'client': client_mock,
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {'sel_pay_btn': True, 'sel_withdraw_btn': False},
        }
        ui = Mock()
        next_stage = stages.selection(run, ui)
        self.assertTrue(client_mock.host_get_payout.called)
        self.assertEqual(ui.showScreen.call_args[0][0], 'selection')
        self.assertEqual(ui.setText.call_args[0][1], u'£0.15')
        self.assertEqual(next_stage,
                         defaults.STAGES['payment']['pay_amount'])
        self.assertFalse(any(state for state
                             in run['screen_buttons'].values()))

    def test_withdraw_button(self):
        client_mock = Mock(**{
            'host_get_payout.return_value': Decimal('0.50'),
        })
        run = {
            'client': client_mock,
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {'sel_pay_btn': False, 'sel_withdraw_btn': True},
            'withdrawal': {},
        }
        ui = Mock()
        next_stage = stages.selection(run, ui)
        self.assertTrue(client_mock.host_get_payout.called)
        self.assertEqual(next_stage,
                         defaults.STAGES['withdrawal']['withdraw_loading1'])
        self.assertFalse(any(state for state
                             in run['screen_buttons'].values()))
        self.assertEqual(run['withdrawal']['fiat_amount'], Decimal('0.5'))


class PaymentAmountStageTestCase(unittest.TestCase):

    def test_option_1(self):
        client_mock = Mock(**{
            'host_get_payout.return_value': Decimal('0.33'),
        })
        run = {
            'client': client_mock,
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'pamount_opt1_btn': True,
                'pamount_opt2_btn': False,
                'pamount_opt3_btn': False,
                'pamount_opt4_btn': False,
                'pamount_cancel_btn': False,
            },
            'payment': {},
        }
        ui = Mock()
        next_stage = stages.pay_amount(run, ui)
        self.assertEqual(ui.showScreen.call_args[0][0], 'pay_amount')
        self.assertEqual(ui.setText.call_args_list[0][0][1], u'\xa30.33')
        self.assertEqual(next_stage,
                         defaults.STAGES['payment']['pay_confirm'])
        self.assertFalse(any(state for state
                             in run['screen_buttons'].values()))
        self.assertEqual(run['payment']['fiat_amount'], Decimal('1.00'))

    def test_option_2(self):
        client_mock = Mock(**{
            'host_get_payout.return_value': Decimal('0.33'),
        })
        run = {
            'client': client_mock,
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'pamount_opt1_btn': False,
                'pamount_opt2_btn': True,
                'pamount_opt3_btn': False,
                'pamount_opt4_btn': False,
                'pamount_cancel_btn': False,
            },
            'payment': {},
        }
        ui = Mock()
        next_stage = stages.pay_amount(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['payment']['pay_confirm'])
        self.assertFalse(any(state for state
                             in run['screen_buttons'].values()))
        self.assertEqual(run['payment']['fiat_amount'], Decimal('2.50'))

    def test_option_3(self):
        client_mock = Mock(**{
            'host_get_payout.return_value': Decimal('0.33'),
        })
        run = {
            'client': client_mock,
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'pamount_opt1_btn': False,
                'pamount_opt2_btn': False,
                'pamount_opt3_btn': True,
                'pamount_opt4_btn': False,
                'pamount_cancel_btn': False,
            },
            'payment': {},
        }
        ui = Mock()
        next_stage = stages.pay_amount(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['payment']['pay_confirm'])
        self.assertFalse(any(state for state
                             in run['screen_buttons'].values()))
        self.assertEqual(run['payment']['fiat_amount'], Decimal('10.00'))

    def test_option_4(self):
        client_mock = Mock(**{
            'host_get_payout.return_value': Decimal('0.33'),
        })
        run = {
            'client': client_mock,
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'pamount_opt1_btn': False,
                'pamount_opt2_btn': False,
                'pamount_opt3_btn': False,
                'pamount_opt4_btn': True,
                'pamount_cancel_btn': False,
            },
            'payment': {},
        }
        ui = Mock()
        next_stage = stages.pay_amount(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['payment']['pay_confirm'])
        self.assertFalse(any(state for state
                             in run['screen_buttons'].values()))
        self.assertEqual(run['payment']['fiat_amount'], Decimal('0.00'))

    def test_return(self):
        client_mock = Mock(**{
            'host_get_payout.return_value': Decimal('0.33'),
        })
        run = {
            'client': client_mock,
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'pamount_opt1_btn': False,
                'pamount_opt2_btn': False,
                'pamount_opt3_btn': False,
                'pamount_opt4_btn': False,
                'pamount_cancel_btn': True,
            },
            'payment': {},
        }
        ui = Mock()
        next_stage = stages.pay_amount(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['idle'])
        self.assertFalse(any(state for state
                             in run['screen_buttons'].values()))


class PayConfirmStageTestCase(unittest.TestCase):

    def test_decrement(self):
        client_mock = Mock(**{
            'host_get_payout.return_value': Decimal('0.33'),
        })
        run = {
            'client': client_mock,
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'pconfirm_decr_btn': True,
                'pconfirm_incr_btn': False,
                'pconfirm_confirm_btn': True,
                'pconfirm_goback_btn': False,
            },
            'payment': {'fiat_amount': Decimal('0.50')},
        }
        ui = Mock()
        next_stage = stages.pay_confirm(run, ui)
        self.assertEqual(ui.showScreen.call_args[0][0], 'pay_confirm')
        self.assertTrue(client_mock.host_get_payout.called)
        self.assertEqual(ui.setText.call_args_list[0][0][1], u'\xa30.33')
        self.assertEqual(ui.setText.call_args_list[1][0][1], u'\xa30.50')
        self.assertEqual(ui.setText.call_args_list[2][0][1], u'\xa30.45')
        self.assertEqual(next_stage,
                         defaults.STAGES['payment']['pay_loading'])
        self.assertEqual(run['payment']['fiat_amount'], Decimal('0.45'))
        self.assertFalse(any(state for state
                             in run['screen_buttons'].values()))

    def test_increment(self):
        client_mock = Mock(**{
            'host_get_payout.return_value': Decimal('0.50'),
        })
        run = {
            'client': client_mock,
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'pconfirm_decr_btn': False,
                'pconfirm_incr_btn': True,
                'pconfirm_confirm_btn': True,
                'pconfirm_goback_btn': False,
            },
            'payment': {'fiat_amount': Decimal('0.50')},
        }
        ui = Mock()
        next_stage = stages.pay_confirm(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['payment']['pay_loading'])
        self.assertEqual(run['payment']['fiat_amount'], Decimal('0.55'))
        self.assertFalse(any(state for state
                             in run['screen_buttons'].values()))

    def test_return(self):
        client_mock = Mock(**{
            'host_get_payout.return_value': Decimal('0.33'),
        })
        run = {
            'client': client_mock,
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'pconfirm_decr_btn': False,
                'pconfirm_incr_btn': False,
                'pconfirm_confirm_btn': False,
                'pconfirm_goback_btn': True,
            },
            'payment': {'fiat_amount': Decimal('0.00')},
        }
        ui = Mock()
        next_stage = stages.pay_confirm(run, ui)
        self.assertEqual(ui.setText.call_args_list[0][0][1], u'\xa30.33')
        self.assertEqual(next_stage,
                         defaults.STAGES['payment']['pay_amount'])
        self.assertFalse(any(state for state
                             in run['screen_buttons'].values()))


class PayLoadingStageTestCase(unittest.TestCase):

    def test_no_amount(self):
        run = {
            'payment': {
                'fiat_amount': None,
            },
        }
        ui = Mock()
        next_stage = stages.pay_loading(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['payment']['pay_amount'])

    def test_proceed(self):
        client_mock = Mock(**{
            'create_payment_order.return_value': {
                'uid': 'testUid',
                'payment_uri': 'test',
            },
        })
        run = {
            'client': client_mock,
            'payment': {
                'fiat_amount': Decimal('1.00'),
            },
        }
        ui = Mock()
        next_stage = stages.pay_loading(run, ui)
        self.assertEqual(ui.showScreen.call_args[0][0],
                         'load_indefinite')
        self.assertEqual(run['payment']['uid'], 'testUid')
        self.assertEqual(
            client_mock.create_payment_order.call_args[1]['fiat_amount'],
            Decimal('1.00'))
        self.assertEqual(next_stage,
                         defaults.STAGES['payment']['pay_info'])

    def test_server_error(self):
        client_mock = Mock(**{
            'create_payment_order.side_effect': ServerError,
        })
        run = {
            'client': client_mock,
            'payment': {
                'fiat_amount': Decimal('1.00'),
            },
        }
        ui = Mock()
        next_stage = stages.pay_loading(run, ui)
        self.assertIsNone(run['payment']['fiat_amount'])
        self.assertEqual(next_stage,
                         defaults.STAGES['idle'])


class PayInfoStageTestCase(unittest.TestCase):

    def test_cancel(self):
        client_mock = Mock(**{
            'cancel_payment.return_value': True,
        })
        run = {
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
        next_stage = stages.pay_info(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['payment']['pay_amount'])
        self.assertEqual(client_mock.cancel_payment.call_args[1]['uid'],
                         'testUid')
        self.assertIsNone(run['payment']['uid'])
        self.assertIsNone(run['payment']['fiat_amount'])
        self.assertIsNone(run['payment']['btc_amount'])
        self.assertIsNone(run['payment']['exchange_rate'])
        self.assertIsNone(run['payment']['payment_uri'])
        self.assertFalse(any(state for state
                             in run['screen_buttons'].values()))

    @patch('xbterminal.stages.stages.qr.qr_gen')
    def test_pay(self, qr_gen_mock):
        run = {
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
        next_stage = stages.pay_info(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['payment']['pay_wait'])
        self.assertEqual(ui.showScreen.call_args[0][0], 'pay_info')
        self.assertEqual(ui.setText.call_args_list[0][0][1], u'\xa31.03')
        self.assertTrue(qr_gen_mock.call_args[0][0], 'test')
        self.assertFalse(any(state for state
                             in run['screen_buttons'].values()))


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
        run = {
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
        next_stage = stages.pay_wait(run, ui)
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
        self.assertIsNone(run['payment']['fiat_amount'])
        self.assertIsNone(run['payment']['payment_uri'])
        self.assertEqual(next_stage,
                         defaults.STAGES['payment']['pay_amount'])
        self.assertFalse(any(state for state
                             in run['screen_buttons'].values()))

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
        run = {
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
        next_stage = stages.pay_wait(run, ui)
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
        self.assertEqual(run['payment']['receipt_url'], 'test_url')
        self.assertIsNotNone(run['payment']['uid'])
        self.assertEqual(next_stage,
                         defaults.STAGES['payment']['pay_success'])


class PaySuccessStageTestCase(unittest.TestCase):

    def test_no(self):
        run = {
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
        next_stage = stages.pay_success(run, ui)
        self.assertEqual(ui.showScreen.call_args_list[0][0][0],
                         'pay_success')
        self.assertEqual(ui.showScreen.call_args_list[1][0][0],
                         'load_indefinite')
        self.assertIsNone(run['payment']['uid'])
        self.assertIsNone(run['payment']['fiat_amount'])
        self.assertEqual(next_stage,
                         defaults.STAGES['idle'])
        self.assertFalse(any(state for state
                             in run['screen_buttons'].values()))

    @patch('xbterminal.stages.stages.qr.qr_gen')
    def test_yes(self, qr_gen_mock):
        run = {
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
        next_stage = stages.pay_success(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['payment']['pay_receipt'])
        self.assertIsNotNone(run['payment']['uid'])
        self.assertIsNotNone(run['payment']['receipt_url'])
        self.assertEqual(qr_gen_mock.call_args[0][0], 'test')
        self.assertFalse(any(state for state
                         in run['screen_buttons'].values()))


class PayReceiptStageTestCase(unittest.TestCase):

    def test_goback(self):
        client_mock = Mock(**{
            'start_nfc_server.return_value': True,
        })
        run = {
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
        next_stage = stages.pay_receipt(run, ui)
        self.assertEqual(ui.showScreen.call_args_list[0][0][0],
                         'pay_receipt')
        self.assertEqual(ui.showScreen.call_args_list[1][0][0],
                         'load_indefinite')
        self.assertEqual(
            client_mock.start_nfc_server.call_args[1]['message'],
            'test')
        self.assertTrue(client_mock.stop_nfc_server.called)
        self.assertIsNone(run['payment']['uid'])
        self.assertIsNone(run['payment']['fiat_amount'])
        self.assertIsNone(run['payment']['receipt_url'])
        self.assertEqual(next_stage,
                         defaults.STAGES['idle'])
        self.assertFalse(any(state for state
                             in run['screen_buttons'].values()))


class WithdrawLoading1StageTestCase(unittest.TestCase):

    def test_proceed(self):
        client_mock = Mock(**{
            'create_withdrawal_order.return_value': {
                'uid': 'testUid',
                'btc_amount': Decimal('0.5'),
            },
        })
        run = {
            'client': client_mock,
            'withdrawal': {'fiat_amount': Decimal('1.00')},
        }
        ui = Mock()
        next_stage = stages.withdraw_loading1(run, ui)
        self.assertEqual(
            client_mock.create_withdrawal_order.call_args[1]['fiat_amount'],
            Decimal('1.00'))
        self.assertEqual(next_stage,
                         defaults.STAGES['withdrawal']['withdraw_scan'])
        self.assertEqual(run['withdrawal']['uid'], 'testUid')
        self.assertEqual(run['withdrawal']['btc_amount'], Decimal('0.5'))

    def test_server_error(self):
        client_mock = Mock(**{
            'create_withdrawal_order.side_effect': ServerError,
        })
        run = {
            'client': client_mock,
            'withdrawal': {
                'fiat_amount': Decimal('1.00'),
            },
        }
        ui = Mock()
        next_stage = stages.withdraw_loading1(run, ui)
        self.assertIsNone(run['withdrawal']['fiat_amount'])
        self.assertEqual(next_stage,
                         defaults.STAGES['idle'])


class WithdrawScanStageTestCase(unittest.TestCase):

    def setUp(self):
        self.address = '1PWVL1fW7Ysomg9rXNsS8ng5ZzURa2p9vE'

    def test_return(self):
        client_mock = Mock(**{
            'start_qr_scanner.return_value': True,
            'get_scanned_address.return_value': None,
            'stop_qr_scanner.return_value': True,
        })
        run = {
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
        next_stage = stages.withdraw_scan(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['selection'])
        self.assertTrue(client_mock.start_qr_scanner.called)
        self.assertTrue(client_mock.stop_qr_scanner.called)
        self.assertTrue(client_mock.cancel_withdrawal.call_args[1]['uid'],
                        'testUid')
        self.assertIsNone(run['withdrawal']['uid'])
        self.assertIsNotNone(run['withdrawal']['fiat_amount'])
        self.assertFalse(any(state for state
                             in run['screen_buttons'].values()))

    def test_proceed(self):
        client_mock = Mock(**{
            'start_qr_scanner.return_value': True,
            'get_scanned_address.return_value': self.address,
            'stop_qr_scanner.return_value': True,
        })
        run = {
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
        next_stage = stages.withdraw_scan(run, ui)
        self.assertEqual(ui.showScreen.call_args[0][0], 'withdraw_scan')
        self.assertEqual(ui.setText.call_args_list[0][0][1],
                         u'£1.12')
        self.assertEqual(ui.setText.call_args_list[2][0][1],
                         u'1 BTC = £155.43')
        self.assertTrue(client_mock.start_qr_scanner.called)
        self.assertTrue(client_mock.stop_qr_scanner.called)
        self.assertEqual(next_stage,
                         defaults.STAGES['withdrawal']['withdraw_confirm'])
        self.assertIsNotNone(run['withdrawal']['address'])

    def test_default_address(self):
        client_mock = Mock(**{
            'start_qr_scanner.return_value': True,
            'get_scanned_address.return_value': None,
            'stop_qr_scanner.return_value': True,
        })
        run = {
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
        next_stage = stages.withdraw_scan(run, ui)
        self.assertTrue(client_mock.start_qr_scanner.called)
        self.assertTrue(client_mock.stop_qr_scanner.called)
        self.assertEqual(next_stage,
                         defaults.STAGES['withdrawal']['withdraw_confirm'])
        self.assertEqual(run['withdrawal']['address'], self.address)


class WithdrawConfirmStageTestCase(unittest.TestCase):

    def test_return(self):
        client_mock = Mock(**{
            'cancel_withdrawal.return_value': True,
        })
        run = {
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
        next_stage = stages.withdraw_confirm(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['idle'])
        self.assertEqual(
            client_mock.cancel_withdrawal.call_args[1]['uid'],
            'testUid')
        self.assertIsNone(run['withdrawal']['uid'])
        self.assertIsNone(run['withdrawal']['address'])
        self.assertIsNone(run['withdrawal']['fiat_amount'])
        self.assertFalse(any(state for state
                             in run['screen_buttons'].values()))

    def test_proceed(self):
        run = {
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
        next_stage = stages.withdraw_confirm(run, ui)
        self.assertEqual(ui.showScreen.call_args[0][0], 'withdraw_confirm')
        self.assertEqual(ui.setText.call_args_list[0][0][1],
                         '1PWVL1fW7Ysomg9rXNsS8ng5ZzURa2p9vE')
        self.assertEqual(ui.setText.call_args_list[1][0][1],
                         u'£5.12')
        self.assertEqual(ui.setText.call_args_list[3][0][1],
                         u'1 BTC = £553.12')
        self.assertEqual(next_stage,
                         defaults.STAGES['withdrawal']['withdraw_loading2'])
        self.assertFalse(any(state for state
                             in run['screen_buttons'].values()))


class WithdrawLoading2StageTestCase(unittest.TestCase):

    def test_proceed(self):
        client_mock = Mock(**{
            'get_withdrawal_status.side_effect': ['new', 'completed'],
            'confirm_withdrawal.return_value': {
                'btc_amount': Decimal('0.41'),
                'exchange_rate': Decimal('202.0'),
            },
            'get_withdrawal_receipt.return_value': 'test_url',
            'host_withdraw.return_value': True,
        })
        run = {
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
        next_stage = stages.withdraw_loading2(run, ui)
        self.assertEqual(
            client_mock.confirm_withdrawal.call_args[1]['uid'],
            'testUid')
        self.assertEqual(
            client_mock.host_withdraw.call_args[1]['fiat_amount'],
            Decimal('0.50'))
        self.assertEqual(next_stage,
                         defaults.STAGES['withdrawal']['withdraw_success'])
        self.assertEqual(run['withdrawal']['btc_amount'], Decimal('0.41'))
        self.assertEqual(run['withdrawal']['exchange_rate'], Decimal('202.0'))
        self.assertEqual(run['withdrawal']['receipt_url'], 'test_url')

    def test_server_error(self):
        client_mock = Mock(**{
            'get_withdrawal_status.return_value': 'new',
            'confirm_withdrawal.side_effect': ServerError,
        })
        run = {
            'client': client_mock,
            'withdrawal': {
                'uid': 'testUid',
                'address': '1PWVL1fW7Ysomg9rXNsS8ng5ZzURa2p9vE',
            },
        }
        ui = Mock()
        next_stage = stages.withdraw_loading2(run, ui)
        self.assertEqual(
            client_mock.confirm_withdrawal.call_args[1]['uid'],
            'testUid')
        self.assertFalse(client_mock.cancel_withdrawal.called)
        self.assertEqual(next_stage,
                         defaults.STAGES['idle'])
        self.assertIsNone(run['withdrawal']['uid'])
        self.assertIsNone(run['withdrawal']['address'])


class WithdrawSuccessStageTestCase(unittest.TestCase):

    def test_no(self):
        run = {
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
        next_stage = stages.withdraw_success(run, ui)
        self.assertEqual(ui.showScreen.call_args_list[0][0][0],
                         'withdraw_success')
        self.assertEqual(ui.showScreen.call_args_list[1][0][0],
                         'load_indefinite')
        self.assertIsNone(run['withdrawal']['uid'])
        self.assertIsNone(run['withdrawal']['fiat_amount'])
        self.assertEqual(next_stage,
                         defaults.STAGES['idle'])
        self.assertFalse(any(state for state
                             in run['screen_buttons'].values()))

    @patch('xbterminal.stages.stages.qr.qr_gen')
    def test_yes(self, qr_gen_mock):
        run = {
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
        next_stage = stages.withdraw_success(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['withdrawal']['withdraw_receipt'])
        self.assertIsNotNone(run['withdrawal']['receipt_url'])
        self.assertEqual(qr_gen_mock.call_args[0][0], 'test')
        self.assertFalse(any(state for state
                         in run['screen_buttons'].values()))


class WithdrawReceiptStageTestCase(unittest.TestCase):

    def test_goback(self):
        client_mock = Mock(**{
            'start_nfc_server.return_value': True,
            'stop_nfc_server.return_value': True,
        })
        run = {
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
        next_stage = stages.withdraw_receipt(run, ui)
        self.assertEqual(ui.showScreen.call_args_list[0][0][0],
                         'withdraw_receipt')
        self.assertEqual(ui.showScreen.call_args_list[1][0][0],
                         'load_indefinite')
        self.assertEqual(
            client_mock.start_nfc_server.call_args[1]['message'],
            'test')
        self.assertTrue(client_mock.stop_nfc_server.called)
        self.assertIsNone(run['withdrawal']['uid'])
        self.assertIsNone(run['withdrawal']['fiat_amount'])
        self.assertEqual(next_stage,
                         defaults.STAGES['idle'])
        self.assertFalse(any(state for state
                             in run['screen_buttons'].values()))
