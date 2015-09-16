import unittest
from mock import patch, mock_open

from xbterminal.stages.activation import (
    read_device_key,
    generate_device_key)
from xbterminal.exceptions import DeviceKeyMissingError


class DeviceKeyTestCase(unittest.TestCase):

    @patch('xbterminal.stages.activation.os.path.exists')
    def test_read_device_key(self, exists_mock):
        exists_mock.return_value = True
        open_mock = mock_open(read_data='testKey')
        with patch('xbterminal.stages.activation.open',
                   open_mock, create=True):
            device_key = read_device_key()

        self.assertEqual(device_key, 'testKey')

    @patch('xbterminal.helpers.configs.os.path.exists')
    def test_read_device_key_error(self, exists_mock):
        exists_mock.return_value = False
        with self.assertRaises(DeviceKeyMissingError):
            read_device_key()

    def test_generate_device_key(self):
        open_mock = mock_open()
        with patch('xbterminal.stages.activation.open',
                   open_mock, create=True):
            device_key = generate_device_key()

        self.assertTrue(open_mock().write.called)
        self.assertEqual(len(device_key), 64)
