from decimal import Decimal
import unittest
from mock import patch

from xbterminal.rpc.utils.bsp import BSPLibraryInterface


class BSPLibraryInterfaceTestCase(unittest.TestCase):

    @patch('xbterminal.rpc.utils.bsp.logger')
    @patch('xbterminal.rpc.utils.bsp.BSPLibraryMock.initialize')
    @patch('xbterminal.rpc.utils.bsp.BSPLibraryMock.enable_display')
    def test_init(self, enable_display_mock, initialize_mock, logger_mock):
        bsp_interface = BSPLibraryInterface(use_mock=True)
        self.assertEqual(logger_mock.info.call_args_list[0][0][0],
                         'ITL hardware v0.0.0')
        self.assertEqual(logger_mock.info.call_args_list[1][0][0],
                         'ITL BSP library v0.0.0')
        self.assertIsNotNone(bsp_interface._module)
        self.assertIs(initialize_mock.called, True)
        self.assertIs(enable_display_mock.called, True)

    def test_get_payout_status(self):
        bsp_interface = BSPLibraryInterface(use_mock=True)
        status = bsp_interface.get_payout_status()
        self.assertEqual(status, 'idle')

    @patch('xbterminal.rpc.utils.bsp.BSPLibraryMock.get_payout_status')
    def test_get_payout_status_invalid(self, get_mock):
        get_mock.return_value = 12345
        bsp_interface = BSPLibraryInterface(use_mock=True)
        status = bsp_interface.get_payout_status()
        self.assertIsNone(status)

    def test_get_payout(self):
        bsp_interface = BSPLibraryInterface(use_mock=True)
        self.assertEqual(bsp_interface.get_payout(), Decimal(0))

    def test_nfc(self):
        bsp_interface = BSPLibraryInterface(use_mock=True)
        self.assertIsNone(bsp_interface.write_ndef('test'))
        self.assertIsNone(bsp_interface.erase_ndef())

    def test_display(self):
        bsp_interface = BSPLibraryInterface(use_mock=True)
        self.assertIsNone(bsp_interface.disable_display())
        self.assertIsNone(bsp_interface.enable_display())

    @patch('xbterminal.rpc.utils.bsp.BSPLibraryMock.play_tone')
    def test_beep(self, play_mock):
        bsp_interface = BSPLibraryInterface(use_mock=True)
        self.assertIsNone(bsp_interface.beep())
        self.assertIs(play_mock.called, True)
        self.assertEqual(play_mock.call_args[0], (1000, 1000))
