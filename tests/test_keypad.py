import unittest
from mock import patch, Mock

from xbterminal.keypad.keypad import Keypad


@patch.dict('xbterminal.keypad.keypad.xbterminal.runtime',
            local_config={})
class KeyPadTestCase(unittest.TestCase):

    def test_init(self):
        keypad = Keypad()
        self.assertEqual(keypad.driver.__class__.__name__,
                         'KeyboardDriver')
        self.assertIsNone(keypad.last_key_pressed)
        self.assertEqual(keypad.last_activity_timestamp, 0)

    @patch('xbterminal.keypad.drivers.KeyboardDriver')
    def test_get_key(self, driver_cls_mock):
        driver_cls_mock.return_value = Mock(**{
            'getKey.return_value': 'enter',
        })
        keypad = Keypad()
        keypad.getKey()
        self.assertEqual(keypad.last_key_pressed, 'enter')
        self.assertGreater(keypad.last_activity_timestamp, 0)
