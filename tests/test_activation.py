import unittest
from mock import patch, mock_open, Mock

from xbterminal.stages.activation import (
    read_device_key,
    generate_device_key,
    save_device_key,
    register_device)
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

    def test_save_device_key(self):
        open_mock = mock_open()
        with patch('xbterminal.stages.activation.open',
                   open_mock, create=True):
            save_device_key('testKey')

        self.assertTrue(open_mock().write.called)

    def test_generate_device_key(self):
        device_key = generate_device_key()
        self.assertEqual(len(device_key), 64)


@patch.dict('xbterminal.helpers.api.xbterminal.runtime',
            remote_server='https://xbterminal.io')
class RegistrationTestCase(unittest.TestCase):

    @patch('xbterminal.stages.activation.read_batch_number')
    @patch('xbterminal.stages.activation.save_device_key')
    @patch('xbterminal.stages.activation.crypto.save_secret_key')
    @patch('xbterminal.stages.activation.api.send_request')
    def test_register_devie(self, send_mock, secret_key_mock,
                            device_key_mock, batch_number_mock):
        batch_number_mock.return_value = '0' * 32
        send_mock.return_value = Mock(**{
            'json.return_value': {'activation_code': 'testCode'},
        })
        device_key, activation_code = register_device()
        self.assertEqual(len(device_key), 64)
        self.assertEqual(activation_code, 'testCode')
        post_data = send_mock.call_args[0][2]
        self.assertEqual(post_data['batch'], '0' * 32)
        self.assertEqual(post_data['key'], device_key)
        self.assertIn('api_key', post_data)
