import logging
import mock
import sys
import unittest

sys.modules['PyQt4'] = mock.Mock()
sys.modules['dbus'] = mock.Mock()
sys.modules['nfc'] = mock.Mock()
sys.modules['nfc.snep'] = mock.Mock()
sys.modules['nfc.llcp'] = mock.Mock()
sys.modules['cv2'] = mock.Mock()
sys.modules['zbar'] = mock.Mock()

logging.basicConfig(level=logging.ERROR)

loader = unittest.TestLoader()
tests = loader.discover('.')

testRunner = unittest.runner.TextTestRunner()
testRunner.run(tests)
