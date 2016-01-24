from decimal import Decimal
from mock import patch, Mock
import time
import unittest

from xbterminal import defaults
from xbterminal.stages import stages
from xbterminal.exceptions import ServerError


patcher = patch.dict(
    'xbterminal.stages.amounts.xbterminal.runtime',
    remote_config={
        'language': {
            'code': 'en',
            'thousands_split': ',',
            'fractional_split': '.',
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
        }
        ui = Mock()
        next_stage = stages.activate(run, ui)
        self.assertEqual(next_stage, defaults.STAGES['idle'])


class IdleStageTestCase(unittest.TestCase):

    def test_begin_button(self):
        run = {
            'screen_buttons': {'begin': True},
            'payment': {},
        }
        ui = Mock()
        next_stage = stages.idle(run, ui)
        self.assertEqual(ui.showScreen.call_args[0][0], 'idle')
        self.assertEqual(next_stage,
                         defaults.STAGES['payment']['pay_amount'])
        self.assertEqual(run['payment']['fiat_amount'], 0)

    def test_enter_key_input(self):
        keypad = Mock(last_key_pressed='enter')
        run = {
            'keypad': keypad,
            'screen_buttons': {'begin': False},
            'payment': {},
        }
        ui = Mock()
        next_stage = stages.idle(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['payment']['pay_amount'])
        self.assertEqual(run['payment']['fiat_amount'], 0)

    def test_alt_key_input(self):
        keypad = Mock(last_key_pressed='alt')
        run = {
            'keypad': keypad,
            'screen_buttons': {'begin': False},
            'withdrawal': {},
        }
        ui = Mock()
        next_stage = stages.idle(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['selection'])
        self.assertEqual(run['withdrawal']['fiat_amount'], Decimal('0.25'))

    def test_host_system_payout(self):
        run = {
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {'begin': False},
            'host_system': Mock(**{
                'get_payout.return_value': Decimal('0.15'),
            }),
            'withdrawal': {},
        }
        ui = Mock()
        next_stage = stages.idle(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['selection'])
        self.assertEqual(run['withdrawal']['fiat_amount'], Decimal('0.15'))


class SelectionStageTestCase(unittest.TestCase):

    def test_pay_button(self):
        run = {
            'screen_buttons': {'pay': True, 'withdraw': False},
            'payment': {},
            'withdrawal': {'fiat_amount': Decimal('0.5')},
        }
        ui = Mock()
        next_stage = stages.selection(run, ui)
        self.assertEqual(ui.showScreen.call_args[0][0], 'selection')
        self.assertEqual(ui.setText.call_args[0][1], '0.50')
        self.assertEqual(next_stage,
                         defaults.STAGES['payment']['pay_amount'])
        self.assertEqual(run['payment']['fiat_amount'], 0)

    def test_withdraw_button(self):
        run = {
            'screen_buttons': {'pay': False, 'withdraw': True},
            'withdrawal': {'fiat_amount': Decimal('0.5')},
        }
        ui = Mock()
        next_stage = stages.selection(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['withdrawal']['withdraw_amount'])
        self.assertEqual(run['withdrawal']['fiat_amount'], Decimal('0.5'))

    def test_assertion_error(self):
        run = {
            'screen_buttons': {'pay': False, 'withdraw': False},
            'withdrawal': {'fiat_amount': Decimal(0)},
        }
        ui = Mock()
        with self.assertRaises(AssertionError):
            stages.selection(run, ui)


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

    @patch('xbterminal.stages.payment.Payment.create_order')
    def test_proceed(self, create_order_mock):
        create_order_mock.return_value = Mock(payment_uri='test')
        run = {
            'payment': {
                'fiat_amount': Decimal('1.00'),
            },
            'bluetooth_server': Mock(mac_address='00:00:00:00:00:00'),
        }
        ui = Mock()
        next_stage = stages.pay_loading(run, ui)
        self.assertEqual(ui.showScreen.call_args[0][0],
                         'load_indefinite')
        self.assertIsNotNone(run['payment']['qr_image_path'])
        self.assertIsNotNone(run['payment']['order'])
        self.assertEqual(next_stage,
                         defaults.STAGES['payment']['pay_wait'])

    @patch('xbterminal.stages.payment.Payment.create_order')
    def test_server_error(self, create_order_mock):
        create_order_mock.side_effect = ServerError
        run = {
            'payment': {
                'fiat_amount': Decimal('1.00'),
            },
            'bluetooth_server': Mock(mac_address='00:00:00:00:00:00'),
        }
        ui = Mock()
        next_stage = stages.pay_loading(run, ui)
        self.assertEqual(run['payment']['fiat_amount'], Decimal(0))
        self.assertEqual(next_stage,
                         defaults.STAGES['idle'])


class PayWaitStageTestCase(unittest.TestCase):

    def test_return(self):
        order_mock = Mock(**{
            'btc_amount': Decimal(0),
            'exchange_rate': Decimal(0),
            'payment_uri': 'test',
        })
        host_system_mock = Mock()
        bluetooth_server_mock = Mock()
        nfc_server_mock = Mock(**{'is_active.return_value': False})
        run = {
            'keypad': Mock(last_key_pressed='backspace'),
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
        self.assertEqual(run['payment']['fiat_amount'], Decimal('1.00'))
        self.assertEqual(next_stage,
                         defaults.STAGES['payment']['pay_amount'])

    def test_success(self):
        order_mock = Mock(**{
            'btc_amount': Decimal(0),
            'exchange_rate': Decimal(0),
            'payment_uri': 'test',
            'check.return_value': 'test',
        })
        host_system_mock = Mock()
        bluetooth_server_mock = Mock()
        nfc_server_mock = Mock(**{'is_active.return_value': False})
        run = {
            'keypad': Mock(last_key_pressed=None),
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
        self.assertEqual(ui.showScreen.call_args_list[0][0][0],
                         'pay_wait')
        self.assertEqual(ui.showScreen.call_args_list[1][0][0],
                         'load_indefinite')
        self.assertTrue(bluetooth_server_mock.start.called)
        self.assertTrue(bluetooth_server_mock.stop.called)
        self.assertTrue(host_system_mock.add_credit.called)
        self.assertEqual(host_system_mock.add_credit.call_args[0][0],
                         Decimal('1.00'))
        self.assertTrue(nfc_server_mock.start.called)
        self.assertTrue(nfc_server_mock.stop.called)
        self.assertEqual(run['payment']['receipt_url'], 'test')
        self.assertIsNone(run['payment']['order'])
        self.assertEqual(next_stage,
                         defaults.STAGES['payment']['pay_success'])


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

    @patch('xbterminal.stages.withdrawal.Withdrawal.create_order')
    def test_proceed(self, create_order_mock):
        run = {
            'withdrawal': {'fiat_amount': Decimal('1.00')},
        }
        ui = Mock()
        create_order_mock.return_value = 'test_order'
        next_stage = stages.withdraw_loading1(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['withdrawal']['withdraw_scan'])
        self.assertEqual(run['withdrawal']['order'], 'test_order')

    @patch('xbterminal.stages.withdrawal.Withdrawal.create_order')
    def test_server_error(self, create_order_mock):
        run = {
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
            'keypad': Mock(last_key_pressed='backspace'),
            'qr_scanner': Mock(**{'get_data.return_value': None}),
            'withdrawal': {
                'fiat_amount': Decimal(0),
                'order': order_mock,
            },
        }
        ui = Mock()
        next_stage = stages.withdraw_scan(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['withdrawal']['withdraw_amount'])
        self.assertIsNone(run['withdrawal']['order'])
        self.assertIsNotNone(run['withdrawal']['fiat_amount'])

    def test_proceed(self):
        order_mock = Mock(btc_amount=Decimal(0), exchange_rate=Decimal(0))
        run = {
            'keypad': Mock(last_key_pressed=None),
            'qr_scanner': Mock(**{'get_data.return_value': self.address}),
            'withdrawal': {
                'fiat_amount': Decimal(0),
                'order': order_mock,
            },
        }
        ui = Mock()
        next_stage = stages.withdraw_scan(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['withdrawal']['withdraw_confirm'])
        self.assertIsNotNone(run['withdrawal']['address'])


class WithdrawConfirmStageTestCase(unittest.TestCase):

    def test_return(self):
        order_mock = Mock(btc_amount=Decimal(0), exchange_rate=Decimal(0))
        run = {
            'keypad': Mock(last_key_pressed='backspace'),
            'screen_buttons': {'confirm_withdrawal': False},
            'withdrawal': {
                'fiat_amount': Decimal(0),
                'order': order_mock,
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
        order_mock = Mock(btc_amount=Decimal(0), exchange_rate=Decimal(0))
        run = {
            'keypad': Mock(last_key_pressed=None),
            'screen_buttons': {'confirm_withdrawal': True},
            'withdrawal': {
                'fiat_amount': Decimal(0),
                'order': order_mock,
                'address': '1PWVL1fW7Ysomg9rXNsS8ng5ZzURa2p9vE',
            },
        }
        ui = Mock()
        next_stage = stages.withdraw_confirm(run, ui)
        self.assertEqual(next_stage,
                         defaults.STAGES['withdrawal']['withdraw_loading2'])


class WithdrawLoading2StageTestCase(unittest.TestCase):

    def test_proceed(self):
        order_mock = Mock(**{
            'btc_amount': Decimal(0),
            'exchange_rate': Decimal(0),
            'check.return_value': 'test_url',
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
                         defaults.STAGES['withdrawal']['withdraw_success'])
        self.assertEqual(run['withdrawal']['receipt_url'], 'test_url')
        self.assertIsNotNone(run['withdrawal']['qr_image_path'])


class WithdrawSuccessStageTestCase(unittest.TestCase):

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
