import logging
import mock
import sys
import unittest
import mocks

sys.modules['PyQt4'] = mock.Mock(**{
    'QtGui.QApplication': mocks.QApplication,
    'QtGui.QMainWindow': mocks.QMainWindow,
})
sys.modules['dbus'] = mock.Mock()
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
