import unittest
from mock import patch

from xbterminal.gui.keypad import Keypad


class KeyPadTestCase(unittest.TestCase):

    def test_init(self):
        keypad = Keypad()
        self.assertIsNone(keypad.last_key_pressed)
        self.assertEqual(keypad.last_activity_timestamp, 0)

    @patch('xbterminal.gui.keypad.Keypad._get_key')
    def test_get_key(self, get_key_mock):
        get_key_mock.return_value = 'enter'
        keypad = Keypad()
        keypad.get_key()
        self.assertEqual(keypad.last_key_pressed, 'enter')
        self.assertGreater(keypad.last_activity_timestamp, 0)
