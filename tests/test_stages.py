# -*- coding: utf-8 -*-
from decimal import Decimal
from mock import patch, Mock
import time
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

    @patch('xbterminal.stages.stages.time.sleep')
    @patch('xbterminal.stages.stages.xbterminal.helpers.'
           'clock.get_internet_time')
    @patch('xbterminal.stages.stages.xbterminal.helpers.'
           'configs.save_local_config')
    @patch('xbterminal.stages.stages.xbterminal.stages.'
           'activation.is_registered')
    @patch('xbterminal.stages.stages.xbterminal.helpers.host.HostSystem')
    @patch('xbterminal.stages.stages.xbterminal.helpers.bt.BluetoothServer')
    @patch('xbterminal.stages.stages.xbterminal.helpers.nfcpy.NFCServer')
    @patch('xbterminal.stages.stages.xbterminal.helpers.camera.QRScanner')
    def test_bootup(self, qr_scanner_mock, nfc_server_mock, bt_server_mock,
                    host_system_mock, is_registered_mock,
                    save_local_config_mock,
                    get_time_mock, sleep_mock):
        run = {
            'init': {'remote_config': True},
            'local_config': {},
            'remote_config': {
                'status': 'active',
                'bitcoin_network': 'mainnet',
            },
        }
        ui = Mock()
        get_time_mock.return_value = time.time()
        is_registered_mock.return_value = True
        host_system_mock.return_value = 'host_system'
        bt_server_mock.return_value = 'bt_server'
        nfc_server_mock.return_value = 'nfc_server'
        qr_scanner_mock.return_value = 'qr_scanner'
        next_stage = stages.bootup(run, ui)

        self.assertEqual(ui.showScreen.call_args[0][0], 'load_indefinite')
        self.assertTrue(run['init']['clock_synchronized'])
        self.assertTrue(run['init']['registration'])
        self.assertIn('last_started', run['local_config'])
        self.assertTrue(save_local_config_mock.called)
        self.assertEqual(run['host_system'], 'host_system')
        self.assertEqual(run['bluetooth_server'], 'bt_server')
        self.assertEqual(run['nfc_server'], 'nfc_server')
        self.assertEqual(run['qr_scanner'], 'qr_scanner')
        self.assertEqual(next_stage, defaults.STAGES['idle'])

    @patch('xbterminal.stages.stages.time.sleep')
    @patch('xbterminal.stages.stages.xbterminal.helpers.'
           'clock.get_internet_time')
    @patch('xbterminal.stages.stages.xbterminal.helpers.'
           'configs.save_local_config')
    @patch('xbterminal.stages.stages.xbterminal.stages.'
           'activation.is_registered')
    @patch('xbterminal.stages.stages.xbterminal.stages.'
           'activation.register_device')
    @patch('xbterminal.stages.stages.xbterminal.helpers.host.HostSystem')
    @patch('xbterminal.stages.stages.xbterminal.helpers.bt.BluetoothServer')
    @patch('xbterminal.stages.stages.xbterminal.helpers.nfcpy.NFCServer')
    @patch('xbterminal.stages.stages.xbterminal.helpers.camera.QRScanner')
    def test_registration(self, qr_scanner_mock, nfc_server_mock,
                          bt_server_mock, host_system_mock,
                          register_device_mock, is_registered_mock,
                          save_local_config_mock, get_time_mock, sleep_mock):
        run = {
            'init': {'remote_config': True},
            'local_config': {},
            'remote_config': {
                'status': 'activation',
                'bitcoin_network': 'mainnet',
            },
        }
        ui = Mock()
        get_time_mock.return_value = time.time()
        is_registered_mock.return_value = False
        register_device_mock.return_value = 'testCode'
        host_system_mock.return_value = 'host_system'
        bt_server_mock.return_value = 'bt_server'
        nfc_server_mock.return_value = 'nfc_server'
        qr_scanner_mock.return_value = 'qr_scanner'
        next_stage = stages.bootup(run, ui)

        self.assertEqual(ui.showScreen.call_args[0][0], 'load_indefinite')
        self.assertEqual(run['local_config']['activation_code'], 'testCode')
        self.assertTrue(run['init']['registration'])
        self.assertEqual(run['host_system'], 'host_system')
        self.assertEqual(run['bluetooth_server'], 'bt_server')
        self.assertEqual(run['nfc_server'], 'nfc_server')
        self.assertEqual(run['qr_scanner'], 'qr_scanner')
        self.assertEqual(next_stage, defaults.STAGES['activate'])


class ActivateStageTestCase(unittest.TestCase):

    def test_proceed(self):
        run = {
            'local_config': {'activation_code': 'testCode'},
            'remote_config': {'status': 'active'},
            'remote_server': 'https://xbterminal.io',
        }
        ui = Mock()
        next_stage = stages.activate(run, ui)
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
        run = {
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {'idle_begin_btn': False},
            'host_system': Mock(**{
                'get_payout.return_value': Decimal('0.15'),
            }),
        }
        ui = Mock()
        next_stage = stages.idle(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['selection'])


class SelectionStageTestCase(unittest.TestCase):

    def test_pay_button(self):
        run = {
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {'sel_pay_btn': True, 'sel_withdraw_btn': False},
            'host_system': Mock(**{
                'get_payout.return_value': Decimal('0.15'),
            }),
        }
        ui = Mock()
        next_stage = stages.selection(run, ui)
        self.assertEqual(ui.showScreen.call_args[0][0], 'selection')
        self.assertEqual(ui.setText.call_args[0][1], u'£0.15')
        self.assertEqual(next_stage,
                         defaults.STAGES['payment']['pay_amount'])
        self.assertFalse(any(state for state
                             in run['screen_buttons'].values()))

    def test_withdraw_button(self):
        run = {
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {'sel_pay_btn': False, 'sel_withdraw_btn': True},
            'host_system': Mock(**{
                'get_payout.return_value': Decimal('0.50'),
            }),
            'withdrawal': {},
        }
        ui = Mock()
        next_stage = stages.selection(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['withdrawal']['withdraw_loading1'])
        self.assertFalse(any(state for state
                             in run['screen_buttons'].values()))
        self.assertEqual(run['withdrawal']['fiat_amount'], Decimal('0.5'))


class PaymentAmountStageTestCase(unittest.TestCase):

    def test_option_1(self):
        run = {
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'pamount_opt1_btn': True,
                'pamount_opt2_btn': False,
                'pamount_opt3_btn': False,
                'pamount_opt4_btn': False,
                'pamount_cancel_btn': False,
            },
            'payment': {},
            'host_system': Mock(**{
                'get_payout.return_value': Decimal('0.33'),
            }),
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
        run = {
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'pamount_opt1_btn': False,
                'pamount_opt2_btn': True,
                'pamount_opt3_btn': False,
                'pamount_opt4_btn': False,
                'pamount_cancel_btn': False,
            },
            'payment': {},
            'host_system': Mock(**{
                'get_payout.return_value': Decimal('0.33'),
            }),
        }
        ui = Mock()
        next_stage = stages.pay_amount(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['payment']['pay_confirm'])
        self.assertFalse(any(state for state
                             in run['screen_buttons'].values()))
        self.assertEqual(run['payment']['fiat_amount'], Decimal('2.50'))

    def test_option_3(self):
        run = {
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'pamount_opt1_btn': False,
                'pamount_opt2_btn': False,
                'pamount_opt3_btn': True,
                'pamount_opt4_btn': False,
                'pamount_cancel_btn': False,
            },
            'payment': {},
            'host_system': Mock(**{
                'get_payout.return_value': Decimal('0.33'),
            }),
        }
        ui = Mock()
        next_stage = stages.pay_amount(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['payment']['pay_confirm'])
        self.assertFalse(any(state for state
                             in run['screen_buttons'].values()))
        self.assertEqual(run['payment']['fiat_amount'], Decimal('10.00'))

    def test_option_4(self):
        run = {
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'pamount_opt1_btn': False,
                'pamount_opt2_btn': False,
                'pamount_opt3_btn': False,
                'pamount_opt4_btn': True,
                'pamount_cancel_btn': False,
            },
            'payment': {},
            'host_system': Mock(**{
                'get_payout.return_value': Decimal('0.33'),
            }),
        }
        ui = Mock()
        next_stage = stages.pay_amount(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['payment']['pay_confirm'])
        self.assertFalse(any(state for state
                             in run['screen_buttons'].values()))
        self.assertEqual(run['payment']['fiat_amount'], Decimal('0.00'))

    def test_return(self):
        run = {
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'pamount_opt1_btn': False,
                'pamount_opt2_btn': False,
                'pamount_opt3_btn': False,
                'pamount_opt4_btn': False,
                'pamount_cancel_btn': True,
            },
            'payment': {},
            'host_system': Mock(**{
                'get_payout.return_value': Decimal('0.33'),
            }),
        }
        ui = Mock()
        next_stage = stages.pay_amount(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['idle'])
        self.assertFalse(any(state for state
                             in run['screen_buttons'].values()))


class PayConfirmStageTestCase(unittest.TestCase):

    def test_decrement(self):
        run = {
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'pconfirm_decr_btn': True,
                'pconfirm_incr_btn': False,
                'pconfirm_confirm_btn': True,
                'pconfirm_goback_btn': False,
            },
            'payment': {'fiat_amount': Decimal('0.50')},
            'host_system': Mock(**{
                'get_payout.return_value': Decimal('0.33'),
            }),
        }
        ui = Mock()
        next_stage = stages.pay_confirm(run, ui)
        self.assertEqual(ui.showScreen.call_args[0][0], 'pay_confirm')
        self.assertEqual(ui.setText.call_args_list[0][0][1], u'\xa30.33')
        self.assertEqual(ui.setText.call_args_list[1][0][1], u'\xa30.50')
        self.assertEqual(ui.setText.call_args_list[2][0][1], u'\xa30.45')
        self.assertEqual(next_stage,
                         defaults.STAGES['payment']['pay_loading'])
        self.assertEqual(run['payment']['fiat_amount'], Decimal('0.45'))
        self.assertFalse(any(state for state
                             in run['screen_buttons'].values()))

    def test_increment(self):
        run = {
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'pconfirm_decr_btn': False,
                'pconfirm_incr_btn': True,
                'pconfirm_confirm_btn': True,
                'pconfirm_goback_btn': False,
            },
            'payment': {'fiat_amount': Decimal('0.50')},
            'host_system': Mock(**{
                'get_payout.return_value': Decimal('0.50'),
            }),
        }
        ui = Mock()
        next_stage = stages.pay_confirm(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['payment']['pay_loading'])
        self.assertEqual(run['payment']['fiat_amount'], Decimal('0.55'))
        self.assertFalse(any(state for state
                             in run['screen_buttons'].values()))

    def test_return(self):
        run = {
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'pconfirm_decr_btn': False,
                'pconfirm_incr_btn': False,
                'pconfirm_confirm_btn': False,
                'pconfirm_goback_btn': True,
            },
            'payment': {'fiat_amount': Decimal('0.00')},
            'host_system': Mock(**{
                'get_payout.return_value': Decimal('0.33'),
            }),
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
            'device_key': 'testKey',
            'payment': {
                'fiat_amount': None,
            },
        }
        ui = Mock()
        next_stage = stages.pay_loading(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['payment']['pay_amount'])

    @patch('xbterminal.stages.payment.Payment.create_order')
    def test_proceed(self, create_order_mock):
        create_order_mock.return_value = Mock(payment_uri='test')
        run = {
            'device_key': 'testKey',
            'payment': {
                'fiat_amount': Decimal('1.00'),
            },
            'bluetooth_server': Mock(mac_address='00:00:00:00:00:00'),
        }
        ui = Mock()
        next_stage = stages.pay_loading(run, ui)
        self.assertEqual(ui.showScreen.call_args[0][0],
                         'load_indefinite')
        self.assertIsNotNone(run['payment']['order'])
        self.assertEqual(create_order_mock.call_args[0][0], 'testKey')
        self.assertEqual(next_stage,
                         defaults.STAGES['payment']['pay_info'])

    @patch('xbterminal.stages.payment.Payment.create_order')
    def test_server_error(self, create_order_mock):
        create_order_mock.side_effect = ServerError
        run = {
            'device_key': 'testKey',
            'payment': {
                'fiat_amount': Decimal('1.00'),
            },
            'bluetooth_server': Mock(mac_address='00:00:00:00:00:00'),
        }
        ui = Mock()
        next_stage = stages.pay_loading(run, ui)
        self.assertIsNone(run['payment']['fiat_amount'])
        self.assertEqual(next_stage,
                         defaults.STAGES['idle'])


class PayInfoStageTestCase(unittest.TestCase):

    def test_cancel(self):
        order_mock = Mock(**{
            'btc_amount': Decimal('0.123'),
            'exchange_rate': Decimal('234.55'),
            'payment_uri': 'test',
        })
        run = {
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'pinfo_cancel_btn': True,
                'pinfo_pay_btn': False,
            },
            'payment': {
                'fiat_amount': Decimal('1.03'),
                'order': order_mock,
            },
        }
        ui = Mock()
        next_stage = stages.pay_info(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['payment']['pay_amount'])
        self.assertTrue(order_mock.cancel.called)
        self.assertIsNone(run['payment']['fiat_amount'])
        self.assertIsNone(run['payment']['order'])
        self.assertFalse(any(state for state
                             in run['screen_buttons'].values()))

    def test_pay(self):
        order_mock = Mock(**{
            'btc_amount': Decimal(0),
            'exchange_rate': Decimal(0),
            'payment_uri': 'test',
        })
        run = {
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'pinfo_cancel_btn': False,
                'pinfo_pay_btn': True,
            },
            'payment': {
                'fiat_amount': Decimal('1.03'),
                'order': order_mock,
            },
        }
        ui = Mock()
        next_stage = stages.pay_info(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['payment']['pay_wait'])
        self.assertEqual(ui.showScreen.call_args[0][0], 'pay_info')
        self.assertEqual(ui.setText.call_args_list[0][0][1], u'\xa31.03')
        self.assertIsNotNone(run['payment']['qr_image_path'])
        self.assertFalse(any(state for state
                             in run['screen_buttons'].values()))


class PayWaitStageTestCase(unittest.TestCase):

    def test_cancel(self):
        order_mock = Mock(**{
            'btc_amount': Decimal(0),
            'exchange_rate': Decimal(0),
            'payment_uri': 'test',
        })
        host_system_mock = Mock()
        bluetooth_server_mock = Mock()
        nfc_server_mock = Mock(**{'is_active.return_value': False})
        run = {
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'pwait_cancel_btn': True,
            },
            'host_system': host_system_mock,
            'bluetooth_server': bluetooth_server_mock,
            'nfc_server': nfc_server_mock,
            'payment': {
                'fiat_amount': Decimal('1.00'),
                'order': order_mock,
                'qr_image_path': 'test',
            },
        }
        ui = Mock()
        next_stage = stages.pay_wait(run, ui)
        self.assertTrue(bluetooth_server_mock.start.called)
        self.assertTrue(bluetooth_server_mock.stop.called)
        self.assertFalse(host_system_mock.add_credit.called)
        self.assertFalse(nfc_server_mock.start.called)
        self.assertTrue(nfc_server_mock.stop.called)

        self.assertTrue(order_mock.cancel.called)
        self.assertIsNone(run['payment']['fiat_amount'])
        self.assertIsNone(run['payment']['order'])
        self.assertEqual(next_stage,
                         defaults.STAGES['payment']['pay_amount'])
        self.assertFalse(any(state for state
                             in run['screen_buttons'].values()))

    def test_success(self):
        order_mock = Mock(**{
            'btc_amount': Decimal(0),
            'exchange_rate': Decimal(0),
            'payment_uri': 'test',
            'check.return_value': 'notified',
            'receipt_url': 'test_url',
        })
        host_system_mock = Mock()
        bluetooth_server_mock = Mock()
        nfc_server_mock = Mock(**{'is_active.return_value': False})
        run = {
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'pwait_cancel_btn': False,
            },
            'host_system': host_system_mock,
            'bluetooth_server': bluetooth_server_mock,
            'nfc_server': nfc_server_mock,
            'payment': {
                'fiat_amount': Decimal('1.00'),
                'order': order_mock,
                'qr_image_path': 'test',
            },
        }
        ui = Mock()
        next_stage = stages.pay_wait(run, ui)
        self.assertEqual(ui.showScreen.call_args[0][0],
                         'pay_wait')
        self.assertTrue(bluetooth_server_mock.start.called)
        self.assertTrue(bluetooth_server_mock.stop.called)
        self.assertTrue(host_system_mock.add_credit.called)
        self.assertEqual(host_system_mock.add_credit.call_args[0][0],
                         Decimal('1.00'))
        self.assertTrue(nfc_server_mock.start.called)
        self.assertTrue(nfc_server_mock.stop.called)
        self.assertEqual(run['payment']['receipt_url'], 'test_url')
        self.assertIsNotNone(run['payment']['order'])
        self.assertEqual(next_stage,
                         defaults.STAGES['payment']['pay_success'])


class PaySuccessStageTestCase(unittest.TestCase):

    def test_no(self):
        order_mock = Mock(btc_amount=Decimal('0.12345678'))
        run = {
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'psuccess_no_btn': True,
                'psuccess_yes_btn': False,
            },
            'payment': {
                'fiat_amount': Decimal('1.00'),
                'order': order_mock,
                'receipt_url': 'test',
            },
        }
        ui = Mock()
        next_stage = stages.pay_success(run, ui)
        self.assertEqual(ui.showScreen.call_args_list[0][0][0],
                         'pay_success')
        self.assertEqual(ui.showScreen.call_args_list[1][0][0],
                         'load_indefinite')
        self.assertIsNone(run['payment']['order'])
        self.assertIsNone(run['payment']['fiat_amount'])
        self.assertEqual(next_stage,
                         defaults.STAGES['idle'])
        self.assertFalse(any(state for state
                             in run['screen_buttons'].values()))

    def test_yes(self):
        order_mock = Mock(btc_amount=Decimal('0.12345678'))
        run = {
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'psuccess_no_btn': False,
                'psuccess_yes_btn': True,
            },
            'payment': {
                'fiat_amount': Decimal('1.00'),
                'order': order_mock,
                'receipt_url': 'test',
            },
        }
        ui = Mock()
        next_stage = stages.pay_success(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['payment']['pay_receipt'])
        self.assertIsNotNone(run['payment']['qr_image_path'])
        self.assertIsNotNone(run['payment']['order'])
        self.assertIsNotNone(run['payment']['receipt_url'])
        self.assertFalse(any(state for state
                         in run['screen_buttons'].values()))


class PayReceiptStageTestCase(unittest.TestCase):

    def test_goback(self):
        nfc_server_mock = Mock(**{'is_active.return_value': False})
        run = {
            'keypad': Mock(last_key_pressed=None),
            'nfc_server': nfc_server_mock,
            'screen_buttons': {
                'preceipt_goback_btn': True,
            },
            'payment': {
                'receipt_url': 'test',
                'qr_image_path': 'test',
            },
        }
        ui = Mock()
        next_stage = stages.pay_receipt(run, ui)
        self.assertEqual(ui.showScreen.call_args_list[0][0][0],
                         'pay_receipt')
        self.assertEqual(ui.showScreen.call_args_list[1][0][0],
                         'load_indefinite')
        self.assertTrue(nfc_server_mock.start.called)
        self.assertTrue(nfc_server_mock.stop.called)
        self.assertIsNone(run['payment']['order'])
        self.assertIsNone(run['payment']['fiat_amount'])
        self.assertEqual(next_stage,
                         defaults.STAGES['idle'])
        self.assertFalse(any(state for state
                             in run['screen_buttons'].values()))


class WithdrawLoading1StageTestCase(unittest.TestCase):

    @patch('xbterminal.stages.withdrawal.Withdrawal.create_order')
    def test_proceed(self, create_order_mock):
        run = {
            'device_key': 'testKey',
            'withdrawal': {'fiat_amount': Decimal('1.00')},
        }
        ui = Mock()
        create_order_mock.return_value = 'test_order'
        next_stage = stages.withdraw_loading1(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['withdrawal']['withdraw_scan'])
        self.assertEqual(run['withdrawal']['order'], 'test_order')
        self.assertEqual(create_order_mock.call_args[0][0], 'testKey')

    @patch('xbterminal.stages.withdrawal.Withdrawal.create_order')
    def test_server_error(self, create_order_mock):
        run = {
            'device_key': 'testKey',
            'withdrawal': {
                'fiat_amount': Decimal('1.00'),
            },
        }
        ui = Mock()
        create_order_mock.side_effect = ServerError
        next_stage = stages.withdraw_loading1(run, ui)
        self.assertIsNone(run['withdrawal']['fiat_amount'])
        self.assertEqual(next_stage,
                         defaults.STAGES['idle'])


class WithdrawScanStageTestCase(unittest.TestCase):

    def setUp(self):
        self.address = '1PWVL1fW7Ysomg9rXNsS8ng5ZzURa2p9vE'

    def test_return(self):
        order_mock = Mock(btc_amount=Decimal(0), exchange_rate=Decimal(0))
        run = {
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'wscan_goback_btn': True,
            },
            'qr_scanner': Mock(**{'get_data.return_value': None}),
            'local_config': {},
            'withdrawal': {
                'fiat_amount': Decimal(0),
                'order': order_mock,
            },
        }
        ui = Mock()
        next_stage = stages.withdraw_scan(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['selection'])
        self.assertTrue(order_mock.cancel.called)
        self.assertIsNone(run['withdrawal']['order'])
        self.assertIsNotNone(run['withdrawal']['fiat_amount'])
        self.assertFalse(any(state for state
                             in run['screen_buttons'].values()))

    def test_proceed(self):
        order_mock = Mock(btc_amount=Decimal('0.22354655'),
                          exchange_rate=Decimal('155.434'))
        run = {
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'wscan_goback_btn': False,
            },
            'qr_scanner': Mock(**{'get_data.return_value': self.address}),
            'local_config': {},
            'withdrawal': {
                'fiat_amount': Decimal('1.12'),
                'order': order_mock,
            },
        }
        ui = Mock()
        next_stage = stages.withdraw_scan(run, ui)
        self.assertEqual(ui.showScreen.call_args[0][0], 'withdraw_scan')
        self.assertEqual(ui.setText.call_args_list[0][0][1],
                         u'£1.12')
        self.assertEqual(ui.setText.call_args_list[2][0][1],
                         u'1 BTC = £155.43')
        self.assertEqual(next_stage,
                         defaults.STAGES['withdrawal']['withdraw_confirm'])
        self.assertIsNotNone(run['withdrawal']['address'])

    def test_default_address(self):
        order_mock = Mock(btc_amount=Decimal('0.22354655'),
                          exchange_rate=Decimal('155.434'))
        run = {
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'wscan_goback_btn': False,
            },
            'qr_scanner': Mock(**{'get_data.return_value': None}),
            'local_config': {'default_withdrawal_address': self.address},
            'withdrawal': {
                'fiat_amount': Decimal('1.12'),
                'order': order_mock,
            },
        }
        ui = Mock()
        next_stage = stages.withdraw_scan(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['withdrawal']['withdraw_confirm'])
        self.assertEqual(run['withdrawal']['address'], self.address)


class WithdrawConfirmStageTestCase(unittest.TestCase):

    def test_return(self):
        order_mock = Mock(btc_amount=Decimal(0), exchange_rate=Decimal(0))
        run = {
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'wconfirm_confirm_btn': False,
                'wconfirm_cancel_btn': True,
            },
            'withdrawal': {
                'fiat_amount': Decimal(0),
                'order': order_mock,
                'address': '1PWVL1fW7Ysomg9rXNsS8ng5ZzURa2p9vE',
            },
        }
        ui = Mock()
        next_stage = stages.withdraw_confirm(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['idle'])
        self.assertTrue(order_mock.cancel.called)
        self.assertIsNone(run['withdrawal']['order'])
        self.assertIsNone(run['withdrawal']['address'])
        self.assertIsNone(run['withdrawal']['fiat_amount'])
        self.assertFalse(any(state for state
                             in run['screen_buttons'].values()))

    def test_proceed(self):
        order_mock = Mock(btc_amount=Decimal('0.34434334'),
                          exchange_rate=Decimal('553.12'))
        run = {
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'wconfirm_confirm_btn': True,
                'wconfirm_cancel_btn': False,
            },
            'withdrawal': {
                'fiat_amount': Decimal('5.12'),
                'order': order_mock,
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
        order_mock = Mock(**{
            'btc_amount': Decimal(0),
            'exchange_rate': Decimal(0),
            'check.return_value': 'completed',
            'receipt_url': 'test_url',
            'confirmed': False,
        })
        host_system_mock = Mock()
        run = {
            'withdrawal': {
                'fiat_amount': Decimal('0.50'),
                'address': '1PWVL1fW7Ysomg9rXNsS8ng5ZzURa2p9vE',
                'order': order_mock,
            },
            'host_system': host_system_mock,
        }
        ui = Mock()
        next_stage = stages.withdraw_loading2(run, ui)
        self.assertTrue(order_mock.confirm.called)
        self.assertTrue(host_system_mock.withdraw.called)
        self.assertEqual(next_stage,
                         defaults.STAGES['withdrawal']['withdraw_success'])
        self.assertEqual(run['withdrawal']['receipt_url'], 'test_url')

    def test_server_error(self):
        order_mock = Mock(**{
            'confirm.side_effect': ServerError,
            'confirmed': False,
        })
        run = {
            'withdrawal': {
                'address': '1PWVL1fW7Ysomg9rXNsS8ng5ZzURa2p9vE',
                'order': order_mock,
            },
        }
        ui = Mock()
        next_stage = stages.withdraw_loading2(run, ui)
        self.assertTrue(order_mock.confirm.called)
        self.assertEqual(next_stage,
                         defaults.STAGES['idle'])
        self.assertIsNone(run['withdrawal']['address'])


class WithdrawSuccessStageTestCase(unittest.TestCase):

    def test_no(self):
        order_mock = Mock(btc_amount=Decimal('0.12345678'))
        run = {
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'wsuccess_no_btn': True,
                'wsuccess_yes_btn': False,
            },
            'withdrawal': {
                'fiat_amount': Decimal('1.00'),
                'order': order_mock,
                'receipt_url': 'test',
            },
        }
        ui = Mock()
        next_stage = stages.withdraw_success(run, ui)
        self.assertEqual(ui.showScreen.call_args_list[0][0][0],
                         'withdraw_success')
        self.assertEqual(ui.showScreen.call_args_list[1][0][0],
                         'load_indefinite')
        self.assertIsNone(run['withdrawal']['order'])
        self.assertIsNone(run['withdrawal']['fiat_amount'])
        self.assertEqual(next_stage,
                         defaults.STAGES['idle'])
        self.assertFalse(any(state for state
                             in run['screen_buttons'].values()))

    def test_yes(self):
        order_mock = Mock(btc_amount=Decimal('0.12345678'))
        run = {
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {
                'wsuccess_no_btn': False,
                'wsuccess_yes_btn': True,
            },
            'withdrawal': {
                'fiat_amount': Decimal('1.00'),
                'order': order_mock,
                'receipt_url': 'test',
            },
        }
        ui = Mock()
        next_stage = stages.withdraw_success(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['withdrawal']['withdraw_receipt'])
        self.assertIsNotNone(run['withdrawal']['qr_image_path'])
        self.assertIsNotNone(run['withdrawal']['order'])
        self.assertIsNotNone(run['withdrawal']['receipt_url'])
        self.assertFalse(any(state for state
                         in run['screen_buttons'].values()))


class WithdrawReceiptStageTestCase(unittest.TestCase):

    def test_goback(self):
        nfc_server_mock = Mock(**{'is_active.return_value': False})
        run = {
            'keypad': Mock(last_key_pressed=None),
            'nfc_server': nfc_server_mock,
            'screen_buttons': {
                'wreceipt_goback_btn': True,
            },
            'withdrawal': {
                'fiat_amount': Decimal('1.00'),
                'receipt_url': 'test',
                'qr_image_path': 'test',
            },
        }
        ui = Mock()
        next_stage = stages.withdraw_receipt(run, ui)
        self.assertEqual(ui.showScreen.call_args_list[0][0][0],
                         'withdraw_receipt')
        self.assertEqual(ui.showScreen.call_args_list[1][0][0],
                         'load_indefinite')
        self.assertTrue(nfc_server_mock.start.called)
        self.assertTrue(nfc_server_mock.stop.called)
        self.assertIsNone(run['withdrawal']['order'])
        self.assertIsNone(run['withdrawal']['fiat_amount'])
        self.assertEqual(next_stage,
                         defaults.STAGES['idle'])
        self.assertFalse(any(state for state
                             in run['screen_buttons'].values()))
