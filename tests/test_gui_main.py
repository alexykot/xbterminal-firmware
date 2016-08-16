import unittest

from mock import patch, Mock

from xbterminal.main_gui import main


class MainTestCase(unittest.TestCase):

    @patch('xbterminal.main_gui.logging.config.dictConfig')
    @patch('xbterminal.main_gui.JSONRPCClient')
    @patch('xbterminal.main_gui.GUI')
    def test_main(self, gui_mock, client_cls_mock, log_config_mock):
        client_cls_mock.return_value = client_mock = Mock(**{
            'get_connection_status.return_value': 'online',
            'get_device_config.return_value': {
                'language': {'code': 'en'},
                'currency': {'prefix': '$'},
            },
        })
        gui_mock.return_value = main_window_mock = Mock()
        keypad_mock = Mock(last_activity_timestamp=0)
        state = {
            'keypad': keypad_mock,
            'init': {'registration': True},
            'remote_config_last_update': 0,
            'last_activity_timestamp': 0,
            'CURRENT_STAGE': 'application_halt',
        }
        with patch.dict('xbterminal.main_gui.state', **state):
            main()
        self.assertTrue(log_config_mock.called)
        self.assertTrue(client_mock.get_connection_status.called)
        self.assertTrue(client_mock.get_device_config.called)
        self.assertTrue(keypad_mock.get_key.called)
        self.assertTrue(main_window_mock.processEvents.called)
        self.assertTrue(main_window_mock.close.called)
