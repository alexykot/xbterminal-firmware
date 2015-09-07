import unittest
from mock import patch, Mock

from xbterminal.helpers.configs import load_remote_config
from xbterminal.exceptions import ConfigLoadError


@patch.dict('xbterminal.helpers.configs.xbterminal.runtime',
            device_key='test',
            remote_server='https://xbterminal.io')
class RemoteConfigTestCase(unittest.TestCase):

    @patch('xbterminal.helpers.configs.requests.get')
    @patch('xbterminal.helpers.configs.load_remote_config_cache')
    @patch('xbterminal.helpers.configs.save_remote_config_cache')
    @patch('xbterminal.helpers.configs.xbterminal')
    def test_load_config(self, xbterminal_mock,
                         save_cache_mock, load_cache_mock, get_url_mock):
        get_url_mock.return_value = Mock(**{
            'json.return_value': {'aaa': 111},
        })
        load_remote_config()
        self.assertEqual(xbterminal_mock.remote_config['aaa'], 111)
        self.assertFalse(load_cache_mock.called)
        self.assertTrue(save_cache_mock.called)

    @patch('xbterminal.helpers.configs.requests.get')
    @patch('xbterminal.helpers.configs.load_remote_config_cache')
    @patch('xbterminal.helpers.configs.save_remote_config_cache')
    @patch('xbterminal.helpers.configs.xbterminal')
    def test_cache(self, xbterminal_mock,
                   save_cache_mock, load_cache_mock, get_url_mock):
        get_url_mock.side_effect = ValueError
        load_cache_mock.return_value = {'aaa': 111}
        load_remote_config()
        self.assertEqual(xbterminal_mock.remote_config['aaa'], 111)
        self.assertTrue(load_cache_mock.called)
        self.assertFalse(save_cache_mock.called)

    @patch('xbterminal.helpers.configs.requests.get')
    @patch('xbterminal.helpers.configs.load_remote_config_cache')
    @patch('xbterminal.helpers.configs.save_remote_config_cache')
    @patch('xbterminal.helpers.configs.xbterminal')
    def test_error(self, xbterminal_mock,
                   save_cache_mock, load_cache_mock, get_url_mock):
        get_url_mock.side_effect = ValueError
        load_cache_mock.side_effect = IOError
        with self.assertRaises(ConfigLoadError):
            load_remote_config()
