import unittest

from mock import patch, Mock

from xbterminal.main import main


class MainTestCase(unittest.TestCase):

    @patch('xbterminal.main.logging.config.dictConfig')
    @patch('xbterminal.main.init_step_1')
    @patch('xbterminal.main.GUI')
    @patch('xbterminal.main.configs.load_remote_config')
    def test_main(self, load_remote_config_mock,
                  gui_mock, init_mock, log_config_mock):
        watcher_mock = Mock(**{'get_errors.return_value': None})
        load_remote_config_mock.return_value = {
            'language': {'code': 'en'},
            'currency': {'prefix': '$'},
        }
        keypad_mock = Mock(last_activity_timestamp=0)
        state = {
            'watcher': watcher_mock,
            'keypad': keypad_mock,
            'init': {'registration': True},
            'remote_config_last_update': 0,
            'last_activity_timestamp': 0,
            'CURRENT_STAGE': 'application_halt',
        }
        with patch.dict('xbterminal.main.state', **state):
            main()
        self.assertTrue(log_config_mock.called)
        self.assertTrue(init_mock.called)
        self.assertTrue(gui_mock.called)
        self.assertTrue(watcher_mock.get_errors.called)
        self.assertTrue(load_remote_config_mock.called)
        self.assertTrue(keypad_mock.getKey.called)
