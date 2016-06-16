import unittest

from mock import patch

from xbterminal.state import get_initial_state
from xbterminal import defaults
from xbterminal.main import init


class InitTestCase(unittest.TestCase):

    def test_initial_state(self):
        state = get_initial_state()
        self.assertFalse(state['init']['clock_synchronized'])
        self.assertFalse(state['init']['registration'])
        self.assertFalse(state['init']['remote_config'])
        self.assertEqual(state['init']['remote_config_last_update'], 0)
        self.assertEqual(state['CURRENT_STAGE'], defaults.STAGES['bootup'])
        self.assertIsNone(state['payment']['fiat_amount'])
        self.assertIsNone(state['payment']['order'])
        self.assertIsNone(state['payment']['qr_image_path'])
        self.assertIsNone(state['payment']['receipt_url'])
        self.assertIsNone(state['withdrawal']['fiat_amount'])
        self.assertIsNone(state['withdrawal']['order'])
        self.assertIsNone(state['withdrawal']['address'])
        self.assertIsNone(state['withdrawal']['receipt_url'])
        self.assertIsNone(state['withdrawal']['qr_image_path'])
        self.assertFalse(state['screen_buttons']['idle_begin_btn'])
        self.assertFalse(state['screen_buttons']['sel_pay_btn'])
        self.assertFalse(state['screen_buttons']['sel_withdraw_btn'])
        self.assertFalse(state['screen_buttons']['pamount_opt1_btn'])
        self.assertFalse(state['screen_buttons']['pamount_opt2_btn'])
        self.assertFalse(state['screen_buttons']['pamount_opt3_btn'])
        self.assertFalse(state['screen_buttons']['pamount_opt4_btn'])
        self.assertFalse(state['screen_buttons']['pconfirm_decr_btn'])
        self.assertFalse(state['screen_buttons']['pconfirm_incr_btn'])
        self.assertFalse(state['screen_buttons']['pconfirm_confirm_btn'])
        self.assertFalse(state['screen_buttons']['wconfirm_confirm_btn'])
        self.assertIsNone(state['device_key'])
        self.assertEqual(len(state['local_config'].keys()), 0)
        self.assertIsNone(state['remote_server'])
        self.assertEqual(len(state['remote_config'].keys()), 0)
        self.assertIsNone(state['last_activity_timestamp'])
        self.assertIsNone(state['keypad'])
        self.assertEqual(len(state['keyboard_events']), 0)
        self.assertIsNone(state['host_system'])
        self.assertIsNone(state['bluetooth_server'])
        self.assertIsNone(state['nfc_server'])
        self.assertIsNone(state['qr_scanner'])

    @patch('xbterminal.main.xbterminal.helpers.configs.read_device_key')
    @patch('xbterminal.main.xbterminal.helpers.configs.load_local_config')
    @patch('xbterminal.main.xbterminal.watcher.Watcher')
    def test_init(self, watcher_mock, load_mock, read_mock):
        read_mock.return_value = 'test-key'
        load_mock.return_value = {'remote_server': 'prod'}
        state = {}
        init(state)
        self.assertEqual(state['device_key'], 'test-key')
        self.assertIn('local_config', state)
        self.assertEqual(state['remote_server'], 'https://xbterminal.io')
        self.assertIn('keypad', state)
        self.assertIn('watcher', state)
