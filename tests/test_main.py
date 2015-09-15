import unittest

from xbterminal.main import get_initial_state
from xbterminal import defaults


class InitialStateTestCase(unittest.TestCase):

    def test_initial_state(self):
        state = get_initial_state()
        self.assertFalse(state['init']['clock_synchronized'])
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
        self.assertFalse(state['screen_buttons']['skip_wifi'])
        self.assertFalse(state['screen_buttons']['pay'])
        self.assertFalse(state['screen_buttons']['withdraw'])
        self.assertFalse(state['screen_buttons']['confirm_withdrawal'])
        self.assertIsNone(state['device_key'])
        self.assertIsNone(state['batch_number'])
        self.assertEqual(len(state['local_config'].keys()), 0)
        self.assertIsNone(state['remote_server'])
        self.assertEqual(len(state['remote_config'].keys()), 0)
        self.assertIsNone(state['last_activity_timestamp'])
        self.assertIsNone(state['keypad'])
        self.assertEqual(len(state['keyboard_events']), 0)
        self.assertIsNone(state['bluetooth_server'])
        self.assertIsNone(state['nfc_server'])
        self.assertIsNone(state['qr_scanner'])
