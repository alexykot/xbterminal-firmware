import unittest
from mock import patch, Mock

from xbterminal.gui.gui import Application, GUI
from xbterminal import defaults


class ApplicationTestCase(unittest.TestCase):

    @patch.dict('xbterminal.gui.gui.xbterminal.runtime',
                local_config={})
    def test_init(self):
        application = Application()
        self.assertEqual(application.language, defaults.UI_DEFAULT_LANGUAGE)
        self.assertEqual(len(application._translators.keys()), 3)


class GUITestCase(unittest.TestCase):

    @patch('xbterminal.gui.gui.appui')
    def test_init(self, ui_mock):
        ui_mock.Ui_MainWindow.return_value = Mock(**{
            'main_stackedWidget.currentIndex.return_value': 0,
        })
        application = Mock()
        window = GUI(application)
        self.assertIsNotNone(window.ui)
        self.assertEqual(window._saved_screen, 'load_indefinite')
        self.assertTrue(window.show.called)
