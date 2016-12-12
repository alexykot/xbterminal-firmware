import unittest
from mock import patch, Mock

from xbterminal.gui.gui import Application, GUI
from xbterminal.gui import settings


class GUITestCase(unittest.TestCase):

    @patch.dict('xbterminal.gui.gui.state')
    @patch('xbterminal.gui.gui.configs.load_gui_config')
    def test_init_application(self, load_config_mock):
        load_config_mock.return_value = {'show_cursor': True}
        with patch.dict('xbterminal.gui.gui.state', {}):
            application = Application()
        self.assertTrue(load_config_mock.called)
        self.assertEqual(application.language, settings.UI_DEFAULT_LANGUAGE)
        self.assertEqual(len(application._translators.keys()), 3)

    @patch('xbterminal.gui.gui.Application')
    @patch('xbterminal.gui.gui.appui')
    def test_init_gui(self, appui_mock, app_cls_mock):
        app_cls_mock.return_value = app_mock = Mock()
        appui_mock.Ui_MainWindow.return_value = Mock(**{
            'main_stackedWidget.currentIndex.return_value': 0,
        })
        state = {'gui_config': {}}
        with patch.dict('xbterminal.gui.gui.state', state):
            window = GUI()
        self.assertEqual(window._application, app_mock)
        self.assertIsNotNone(window.ui)
        self.assertIsNone(window._saved_screen)
        self.assertTrue(window.show.called)

    @patch('xbterminal.gui.gui.Application')
    @patch('xbterminal.gui.gui.appui')
    def test_show_standby_screen(self, appui_mock, app_cls_mock):
        appui_mock.Ui_MainWindow.return_value = ui_mock = Mock(**{
            'main_stackedWidget.currentIndex.return_value':
                settings.SCREENS['idle'],
            'standby_wake_btn.width.return_value': 480,
            'standby_wake_btn.height.return_value': 272,
            'standby_wake_widget.width.return_value': 400,
            'standby_wake_widget.height.return_value': 200,
        })
        window = GUI()
        window.showStandByScreen()
        self.assertTrue(ui_mock.main_stackedWidget.setCurrentIndex.called)
        self.assertTrue(ui_mock.standby_wake_widget.setGeometry.called)
        rect = ui_mock.standby_wake_widget.setGeometry.call_args[0]
        self.assertLess(rect[0], 81)
        self.assertLess(rect[1], 73)
        self.assertEqual(rect[2], 400)
        self.assertEqual(rect[3], 200)

    @patch('xbterminal.gui.gui.Application')
    @patch('xbterminal.gui.gui.appui')
    def test_show_timeout_screen(self, appui_mock, app_cls_mock):
        title_widget_mock = Mock(**{'text.return_value': 'SCREEN'})
        appui_mock.Ui_MainWindow.return_value = ui_mock = Mock(**{
            'main_stackedWidget.currentIndex.return_value': 3,
            'main_stackedWidget.currentWidget.return_value': Mock(**{
                'findChildren.return_value': [title_widget_mock],
            }),
        })
        window = GUI()
        window.showTimeoutScreen()
        self.assertTrue(ui_mock.main_stackedWidget.setCurrentIndex.called)
        self.assertEqual(ui_mock.timeout_desc_lbl.setText.call_args[0][0],
                         'SCREEN')

    @patch('xbterminal.gui.gui.Application')
    @patch('xbterminal.gui.gui.appui')
    @patch.dict('xbterminal.gui.gui.state', {'gui_config': {}})
    def test_error_screen(self, appui_mock, app_cls_mock):
        appui_mock.Ui_MainWindow.return_value = Mock(**{
            'main_stackedWidget.currentIndex.side_effect': [2, 2, 16],
        })
        window = GUI()
        window.showErrorScreen(1)
        self.assertEqual(window._saved_screen, 'idle')
        self.assertEqual(
            window.ui.error_code_val_lbl.setText.call_args[0][0],
            '0001')
        self.assertEqual(
            window.ui.error_message_val_lbl.setText.call_args[0][0],
            'connection error')
        widget_mock = window.ui.main_stackedWidget
        self.assertEqual(widget_mock.setCurrentIndex.call_args[0][0], 16)
        window.hideErrorScreen()
        self.assertEqual(widget_mock.setCurrentIndex.call_args[0][0], 2)
