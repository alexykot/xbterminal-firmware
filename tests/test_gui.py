import unittest
from mock import patch, Mock

from xbterminal.gui.gui import Application, GUI
from xbterminal import defaults


class GUITestCase(unittest.TestCase):

    @patch.dict('xbterminal.gui.gui.state')
    @patch('xbterminal.gui.gui.configs.load_gui_config')
    def test_init_application(self, load_config_mock):
        load_config_mock.return_value = {'show_cursor': True}
        with patch.dict('xbterminal.gui.gui.state', {}):
            application = Application()
        self.assertTrue(load_config_mock.called)
        self.assertEqual(application.language, defaults.UI_DEFAULT_LANGUAGE)
        self.assertEqual(len(application._translators.keys()), 3)

    @patch('xbterminal.gui.gui.Application')
    @patch('xbterminal.gui.gui.appui')
    def test_init_gui(self, ui_mock, app_cls_mock):
        app_cls_mock.return_value = app_mock = Mock()
        ui_mock.Ui_MainWindow.return_value = Mock(**{
            'main_stackedWidget.currentIndex.return_value': 0,
        })
        state = {'gui_config': {}}
        with patch.dict('xbterminal.gui.gui.state', state):
            window = GUI()
        self.assertEqual(window._application, app_mock)
        self.assertIsNotNone(window.ui)
        self.assertEqual(window._saved_screen, 'load_indefinite')
        self.assertTrue(window.show.called)
