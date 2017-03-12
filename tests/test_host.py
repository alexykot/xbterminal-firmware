from decimal import Decimal
import unittest
from mock import patch

from xbterminal.rpc.utils.bsp import BSPLibraryInterface


class BSPLibraryInterfaceTestCase(unittest.TestCase):

    @patch('xbterminal.rpc.utils.bsp.logger')
    def test_init(self, logger_mock):
        bsp_interface = BSPLibraryInterface(use_mock=True)
        self.assertEqual(logger_mock.info.call_args_list[0][0][0],
                         'ITL hardware v0.0.0')
        self.assertEqual(logger_mock.info.call_args_list[1][0][0],
                         'ITL BSP library v0.0.0')
        self.assertIsNotNone(bsp_interface._module)

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
