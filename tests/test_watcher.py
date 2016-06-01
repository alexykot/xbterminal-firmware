import unittest
from mock import patch, Mock
from requests.exceptions import RequestException

from xbterminal.watcher import Watcher


class WatcherTestCase(unittest.TestCase):

    def test_init(self):
        watcher = Watcher()
        self.assertEqual(watcher.period, 2)
        self.assertEqual(watcher.system_stats_timestamp, 0)
        self.assertIsNone(watcher.internet)
        self.assertEqual(watcher.errors, {})

    @patch.dict('xbterminal.watcher.xbterminal.runtime',
                remote_server='http://xbterminal.io')
    @patch('xbterminal.watcher.requests.get')
    def test_check_system_state(self, get_mock):
        watcher = Watcher()
        self.assertIsNone(watcher.internet)
        get_mock.side_effect = [RequestException, None, RequestException]
        watcher.check_system_state()
        self.assertFalse(watcher.internet)
        self.assertEqual(watcher.errors['internet'], 'no internet')
        watcher.check_system_state()
        self.assertTrue(watcher.internet)
        self.assertEqual(watcher.errors, {})
        watcher.check_system_state()
        self.assertFalse(watcher.internet)
        self.assertEqual(watcher.errors['internet'],
                         'internet disconnected')

    @patch('xbterminal.watcher.psutil')
    @patch('xbterminal.watcher.usb.core.find')
    def test_log_system_stats(self, find_mock, psutil_mock):
        psutil_mock.cpu_percent.return_value = 10
        psutil_mock.virtual_memory.return_value = Mock(percent=40)
        psutil_mock.disk_usage.return_value = Mock(percent=25)
        find_mock.return_value = True
        watcher = Watcher()
        watcher.log_system_stats()
        self.assertEqual(find_mock.call_count, 4)
        self.assertGreater(watcher.system_stats_timestamp, 0)
