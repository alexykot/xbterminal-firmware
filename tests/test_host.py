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
    @patch('xbterminal.rpc.utils.bsp.logger')
    def test_get_payout_status_invalid(self, logger_mock, get_mock):
        get_mock.return_value = 12345
        bsp_interface = BSPLibraryInterface(use_mock=True)
        status = bsp_interface.get_payout_status()
        self.assertIsNone(status)
        self.assertIs(logger_mock.error.called, True)
        self.assertEqual(logger_mock.error.call_args[0][0],
                         'unknown payout status')

    @patch('xbterminal.rpc.utils.bsp.BSPLibraryMock.get_payout_status')
    @patch('xbterminal.rpc.utils.bsp.logger')
    def test_get_payout_status_failed(self, logger_mock, get_mock):
        get_mock.return_value = -1
        bsp_interface = BSPLibraryInterface(use_mock=True)
        status = bsp_interface.get_payout_status()
        self.assertIsNone(status)
        self.assertIs(logger_mock.error.called, True)
        self.assertEqual(logger_mock.error.call_args[0][0],
                         'ITL BSP call failed')

    @patch('xbterminal.rpc.utils.bsp.BSPLibraryMock.get_payout_status')
    @patch('xbterminal.rpc.utils.bsp.logger')
    def test_get_payout_status_error(self, logger_mock, get_mock):
        get_mock.side_effect = ValueError
        bsp_interface = BSPLibraryInterface(use_mock=True)
        status = bsp_interface.get_payout_status()
        self.assertIsNone(status)
        self.assertIs(logger_mock.exception.called, True)

    def test_get_payout_amount(self):
        bsp_interface = BSPLibraryInterface(use_mock=True)
        self.assertEqual(bsp_interface.get_payout_amount(), Decimal(0))

    def test_withdrawal_started(self):
        bsp_interface = BSPLibraryInterface(use_mock=True)
        result = bsp_interface.withdrawal_started('abcdef')
        self.assertIsNone(result)

    def test_withdrawal_completed(self):
        bsp_interface = BSPLibraryInterface(use_mock=True)
        result = bsp_interface.withdrawal_completed('abcdef', 100)
        self.assertIsNone(result)

    def test_get_withdrawal_uid(self):
        bsp_interface = BSPLibraryInterface(use_mock=True)
        result = bsp_interface.get_withdrawal_uid()
        self.assertIsNone(result)

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
