import unittest
from mock import patch

from xbterminal.gui.gui import Application
from xbterminal import defaults


class ApplicationTestCase(unittest.TestCase):

    @patch.dict('xbterminal.gui.gui.xbterminal.runtime',
                local_config={})
    def test_init(self):
        application = Application()
        self.assertEqual(application.language, defaults.UI_DEFAULT_LANGUAGE)
        self.assertEqual(len(application._translators.keys()), 3)
