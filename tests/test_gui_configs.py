import unittest
from mock import patch, mock_open

from xbterminal.gui.utils.configs import (
    load_gui_config,
    save_gui_config)


class GuiConfigTestCase(unittest.TestCase):

    @patch('xbterminal.gui.utils.configs.os.path.exists')
    @patch('xbterminal.gui.utils.configs.save_gui_config')
    def test_load_config(self, save_config_mock, exists_mock):
        exists_mock.return_value = True
        open_mock = mock_open(read_data='{"ddd": 444}')
        with patch('xbterminal.gui.utils.configs.open',
                   open_mock, create=True):
            gui_config = load_gui_config()

        self.assertEqual(gui_config['ddd'], 444)
        self.assertFalse(save_config_mock.called)

    @patch('xbterminal.gui.utils.configs.os.path.exists')
    @patch('xbterminal.gui.utils.configs.save_gui_config')
    def test_load_config_error(self, save_config_mock, exists_mock):
        exists_mock.return_value = False
        gui_config = load_gui_config()

        self.assertEqual(len(gui_config.keys()), 0)
        self.assertTrue(save_config_mock.called)

    def test_save_config(self):
        open_mock = mock_open()
        with patch('xbterminal.gui.utils.configs.open',
                   open_mock, create=True):
            save_gui_config({'eee': 555})

        self.assertEqual(open_mock().write.call_args[0][0],
                         '{\n  "eee": 555\n}')
