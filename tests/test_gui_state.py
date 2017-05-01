import unittest

from xbterminal.gui.state import get_initial_gui_state
from xbterminal.gui import settings


class InitTestCase(unittest.TestCase):

    def get_initial_gui_state(self):
        state = get_initial_gui_state()
        self.assertIsNone(state['client'])
        self.assertEqual(state['gui_config'], {})
        self.assertEqual(state['remote_config'], {})
        self.assertEqual(state['remote_config_last_update'], 0)
        self.assertGreater(state['last_activity_timestamp'], 0)
        self.assertIsNone(state['keypad'])
        self.assertEqual(len(state['keyboard_events']), 1)
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
        self.assertIs(state['is_suspended'], False)
        self.assertEqual(state['CURRENT_STAGE'], settings.STAGES['bootup'])
        self.assertEqual(state['errors'], set())
        self.assertIsNone(state['payment']['uid'])
        self.assertIsNone(state['payment']['fiat_amount'])
        self.assertIsNone(state['payment']['btc_amount'])
        self.assertIsNone(state['payment']['exchange_rate'])
        self.assertIsNone(state['payment']['payment_uri'])
        self.assertIsNone(state['payment']['receipt_url'])
        self.assertIsNone(state['withdrawal']['uid'])
        self.assertIsNone(state['withdrawal']['fiat_amount'])
        self.assertIsNone(state['withdrawal']['btc_amount'])
        self.assertIsNone(state['withdrawal']['exchange_rate'])
        self.assertIsNone(state['withdrawal']['address'])
        self.assertIsNone(state['withdrawal']['receipt_url'])
