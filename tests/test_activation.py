import unittest
from mock import patch, Mock

from xbterminal.stages.activation import register_device, is_registered


@patch.dict('xbterminal.helpers.api.xbterminal.runtime',
            remote_server='https://xbterminal.io')
class RegistrationTestCase(unittest.TestCase):

    @patch('xbterminal.stages.activation.configs.read_device_key')
    @patch('xbterminal.stages.activation.configs.read_batch_number')
    @patch('xbterminal.stages.activation.salt.get_public_key_fingerprint')
    @patch('xbterminal.stages.activation.crypto.save_secret_key')
    @patch('xbterminal.stages.activation.api.send_request')
    def test_register_device(self, send_mock, secret_key_mock,
                             salt_finger_mock,
                             batch_number_mock, device_key_mock):
        device_key_mock.return_value = device_key = '0' * 64
        batch_number_mock.return_value = batch_number = '0' * 32
        salt_finger_mock.return_value = salt_fingerprint = 'fingerprint'
        send_mock.return_value = Mock(**{
            'json.return_value': {'activation_code': 'testCode'},
        })
        activation_code = register_device()
        self.assertEqual(activation_code, 'testCode')
        post_data = send_mock.call_args[0][2]
        self.assertEqual(post_data['batch'], batch_number)
        self.assertEqual(post_data['key'], device_key)
        self.assertEqual(post_data['salt_fingerprint'], salt_fingerprint)
        self.assertIn('api_key', post_data)

    @patch('xbterminal.stages.activation.crypto.read_secret_key')
    def test_is_registered(self, secret_key_mock):
        self.assertTrue(is_registered())
        secret_key_mock.side_effect = IOError
        self.assertFalse(is_registered())
