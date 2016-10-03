from decimal import Decimal
import unittest

from xbterminal.rpc.utils.bsp import BSPLibraryInterface


class BSPLibraryInterfaceTestCase(unittest.TestCase):

    def test_payin_payout(self):
        bsp_interface = BSPLibraryInterface(use_mock=True)
        self.assertIsNone(bsp_interface.get_payout())
        bsp_interface.add_credit(Decimal('1.25'))
        bsp_interface.pay_cash(Decimal('1.25'))
        self.assertIsNone(bsp_interface.get_payout())

    def test_nfc(self):
        bsp_interface = BSPLibraryInterface(use_mock=True)
        self.assertIsNone(bsp_interface.write_ndef('test'))
        self.assertIsNone(bsp_interface.erase_ndef())
