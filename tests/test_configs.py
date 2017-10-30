import unittest
from mock import patch, mock_open, Mock

from xbterminal.rpc.utils.configs import (
    read_device_key,
    read_batch_number,
    load_remote_config,
    save_remote_config_cache,
    load_remote_config_cache,
    load_rpc_config,
    save_rpc_config)
from xbterminal.rpc.exceptions import ConfigLoadError


class DeviceKeyTestCase(unittest.TestCase):

    def test_read_device_key(self):
        open_mock = mock_open(read_data='testKey')
        with patch('xbterminal.rpc.utils.configs.open',
                   open_mock, create=True):
            device_key = read_device_key()

        self.assertEqual(device_key, 'testKey')

    def test_read_batch_number(self):
        open_mock = mock_open(read_data='testNumber')
        with patch('xbterminal.rpc.utils.configs.open',
                   open_mock, create=True):
            device_key = read_batch_number()

        self.assertEqual(device_key, 'testNumber')


@patch.dict('xbterminal.rpc.utils.configs.state',
            device_key='test',
            remote_config={})
@patch.dict('xbterminal.rpc.utils.api.state',
            remote_server='https://xbterminal.io')
class RemoteConfigTestCase(unittest.TestCase):

    def setUp(self):
        self.remote_config = {
            'status': 'active',
            'currency': {
                'name': 'GBP',
                'prefix': '\u00a3',
                'postfix': '',
            },
            'coin': 'DASH',
            'language': {
                'code': 'en',
                'fractional_split': '.',
                'thousands_split': ',',
            },
        }

    @patch('xbterminal.rpc.utils.configs.api.send_request')
    @patch('xbterminal.rpc.utils.configs.load_remote_config_cache')
    @patch('xbterminal.rpc.utils.configs.save_remote_config_cache')
    def test_load_config(self, save_cache_mock, load_cache_mock, send_mock):
        send_mock.return_value = Mock(**{
            'json.return_value': self.remote_config.copy(),
        })
        remote_config = load_remote_config()
        self.assertEqual(remote_config['status'], 'active')
        self.assertEqual(remote_config['coin'], {'name': 'DASH'})
        self.assertFalse(load_cache_mock.called)
        self.assertTrue(save_cache_mock.called)
        self.assertEqual(save_cache_mock.call_args[0][0], remote_config)

    @patch('xbterminal.rpc.utils.configs.api.send_request')
    @patch('xbterminal.rpc.utils.configs.load_remote_config_cache')
    @patch('xbterminal.rpc.utils.configs.save_remote_config_cache')
    def test_cache(self, save_cache_mock, load_cache_mock, send_mock):
        send_mock.side_effect = ValueError
        load_cache_mock.return_value = self.remote_config.copy()
        remote_config = load_remote_config()
        self.assertEqual(remote_config['status'], 'active')
        self.assertTrue(load_cache_mock.called)
        self.assertFalse(save_cache_mock.called)

    @patch('xbterminal.rpc.utils.configs.api.send_request')
    @patch('xbterminal.rpc.utils.configs.load_remote_config_cache')
    @patch('xbterminal.rpc.utils.configs.save_remote_config_cache')
    def test_error(self, save_cache_mock, load_cache_mock, send_mock):
        send_mock.side_effect = ValueError
        load_cache_mock.side_effect = IOError
        with self.assertRaises(ConfigLoadError):
            load_remote_config()

    def test_save_remote_config_cache(self):
        open_mock = mock_open()
        with patch('xbterminal.rpc.utils.configs.open',
                   open_mock, create=True):
            save_remote_config_cache({'bbb': 222})

        self.assertEqual(open_mock().write.call_args[0][0],
                         '{"bbb": 222}')

    @patch('xbterminal.rpc.utils.configs.os.path.exists')
    def test_load_remote_config_cache(self, exists_mock):
        exists_mock.return_value = True
        open_mock = mock_open(read_data='{"ccc": 333}')
        with patch('xbterminal.rpc.utils.configs.open',
                   open_mock, create=True):
            config = load_remote_config_cache()

        self.assertEqual(config['ccc'], 333)


class LocalConfigTestCase(unittest.TestCase):

    @patch('xbterminal.rpc.utils.configs.os.path.exists')
    @patch('xbterminal.rpc.utils.configs.save_rpc_config')
    def test_load_config(self, save_config_mock, exists_mock):
        exists_mock.return_value = True
        open_mock = mock_open(read_data='{"ddd": 444}')
        with patch('xbterminal.rpc.utils.configs.open',
                   open_mock, create=True):
            rpc_config = load_rpc_config()

        self.assertEqual(rpc_config['ddd'], 444)
        self.assertFalse(save_config_mock.called)

    @patch('xbterminal.rpc.utils.configs.os.path.exists')
    @patch('xbterminal.rpc.utils.configs.save_rpc_config')
    def test_load_config_error(self, save_config_mock, exists_mock):
        exists_mock.return_value = False
        rpc_config = load_rpc_config()

        self.assertEqual(len(rpc_config.keys()), 0)
        self.assertTrue(save_config_mock.called)

    def test_save_config(self):
        open_mock = mock_open()
        with patch('xbterminal.rpc.utils.configs.open',
                   open_mock, create=True):
            save_rpc_config({'eee': 555})

        self.assertEqual(open_mock().write.call_args[0][0],
                         '{\n  "eee": 555\n}')
