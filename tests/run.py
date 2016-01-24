import logging
import mock
import sys
import unittest

sys.modules['PyQt4'] = mock.Mock(**{'QtGui.QApplication': object})
sys.modules['dbus'] = mock.Mock()
sys.modules['nfc'] = mock.Mock()
sys.modules['nfc.snep'] = mock.Mock()
sys.modules['nfc.llcp'] = mock.Mock()
sys.modules['cv2'] = mock.Mock()
sys.modules['zbar'] = mock.Mock()
sys.modules['bluetooth'] = mock.Mock()

logging.basicConfig(level=logging.CRITICAL)

loader = unittest.TestLoader()
tests = loader.discover('.')
testRunner = unittest.runner.TextTestRunner()


def main():
    result = testRunner.run(tests)
    if result.errors or result.failures:
        sys.exit(1)


if __name__ == '__main__':
    main()
