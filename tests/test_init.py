import time
import unittest

from mock import patch, Mock

from xbterminal.rpc.state import get_initial_rpc_state
from xbterminal.rpc.init import init_step_1, init_step_2


class InitTestCase(unittest.TestCase):

    def test_initial_rpc_state(self):
        state = get_initial_rpc_state()
        self.assertFalse(state['init']['clock_synchronized'])
        self.assertFalse(state['init']['registration'])
        self.assertFalse(state['init']['remote_config'])
        self.assertIsNone(state['device_key'])
        self.assertEqual(len(state['rpc_config'].keys()), 0)
        self.assertIsNone(state['remote_server'])
        self.assertEqual(len(state['remote_config'].keys()), 0)
        self.assertIsNone(state['bsp_interface'])
        self.assertIsNone(state['bluetooth_server'])
        self.assertIsNone(state['qr_scanner'])
        self.assertEqual(state['payments'], {})
        self.assertEqual(state['withdrawals'], {})

    @patch('xbterminal.rpc.init.configs.read_device_key')
    @patch('xbterminal.rpc.init.configs.load_rpc_config')
    @patch('xbterminal.rpc.init.Watcher')
    @patch('xbterminal.rpc.init.BluetoothServer')
    @patch('xbterminal.rpc.init.QRScanner')
    def test_init_step_1(self, scanner_cls_mock, bt_cls_mock,
                         watcher_cls_mock, load_mock, read_mock):
        read_mock.return_value = 'test-key'
        load_mock.return_value = {
            'remote_server': 'prod',
            'use_bsp_mock': True,
        }
        watcher_cls_mock.return_value = watcher_mock = Mock()
        bt_cls_mock.return_value = 'bluetooth'
        scanner_cls_mock.return_value = 'scanner'

        state = {}
        init_step_1(state)
        self.assertEqual(state['device_key'], 'test-key')
        self.assertIn('rpc_config', state)
        self.assertEqual(state['remote_server'], 'https://xbterminal.io')
        self.assertEqual(state['watcher'], watcher_mock)
        self.assertEqual(state['bsp_interface'].__class__.__name__,
                         'BSPLibraryInterface')
        self.assertEqual(state['bluetooth_server'], 'bluetooth')
        self.assertEqual(state['qr_scanner'], 'scanner')

    @patch('xbterminal.rpc.init.clock.get_internet_time')
    @patch('xbterminal.rpc.utils.configs.save_rpc_config')
    @patch('xbterminal.rpc.activation.is_registered')
    @patch('xbterminal.rpc.utils.configs.load_remote_config')
    def test_init_step_2(self, load_remote_config_mock, is_registered_mock,
                         save_rpc_config_mock, get_time_mock):
        get_time_mock.return_value = time.time()
        is_registered_mock.return_value = True
        load_remote_config_mock.return_value = {
            'status': 'active',
            'coin': {'name': 'BTC'},
        }

        state = {
            'init': {},
            'rpc_config': {},
        }
        init_step_2(state)
        self.assertTrue(state['init']['clock_synchronized'])
        self.assertIn('last_started', state['rpc_config'])
        self.assertTrue(save_rpc_config_mock.called)
        self.assertTrue(state['init']['registration'])
        self.assertTrue(state['init']['remote_config'])
        self.assertGreater(state['remote_config_last_update'], 0)
        self.assertEqual(state['remote_config']['status'], 'active')

    @patch('xbterminal.rpc.init.clock.get_internet_time')
    @patch('xbterminal.rpc.utils.configs.save_rpc_config')
    @patch('xbterminal.rpc.activation.is_registered')
    @patch('xbterminal.rpc.activation.register_device')
    @patch('xbterminal.rpc.utils.configs.load_remote_config')
    def test_init_step_2_registration(self, load_remote_config_mock,
                                      register_device_mock,
                                      is_registered_mock,
                                      save_rpc_config_mock,
                                      get_time_mock):
        get_time_mock.return_value = time.time()
        is_registered_mock.return_value = False
        register_device_mock.return_value = 'testCode'
        load_remote_config_mock.return_value = {
            'status': 'activation',
            'coin': None,
        }

        state = {
            'init': {},
            'rpc_config': {},
        }
        init_step_2(state)
        self.assertTrue(state['init']['registration'])
        self.assertEqual(state['rpc_config']['activation_code'], 'testCode')
        self.assertTrue(state['init']['remote_config'])
        self.assertGreater(state['remote_config_last_update'], 0)
        self.assertEqual(state['remote_config']['status'], 'activation')
