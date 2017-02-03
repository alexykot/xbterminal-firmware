import unittest

from xbterminal.gui.utils.qr import qr_gen


class QRGeneratorTestCase(unittest.TestCase):

    def test_qr_gen(self):
        data = 'some-test-url'
        result = qr_gen(data)
        self.assertIs(isinstance(result, bytes), True)
