import unittest

from xbterminal.gui.gui import Application
from xbterminal import defaults


class ApplicationTestCase(unittest.TestCase):

    def test_init(self):
        application = Application()
        self.assertEqual(application.language, defaults.UI_DEFAULT_LANGUAGE)
        self.assertEqual(len(application._translators.keys()), 3)
