from decimal import Decimal
import unittest
from mock import patch

from xbterminal.helpers.host import HostSystem


class HostSystemTestCase(unittest.TestCase):

    @patch('xbterminal.helpers.host.itl_bsp')
    def test_add_credit(self, itl_bsp_mock):
        host_system = HostSystem()
        host_system.add_credit(Decimal('1.25'))
        self.assertTrue(itl_bsp_mock.add_credit.called)
        self.assertEqual(itl_bsp_mock.add_credit.call_args[0][0], 125)

    @patch('xbterminal.helpers.host.itl_bsp')
    def test_get_payout(self, itl_bsp_mock):
        itl_bsp_mock.get_payout.return_value = 75
        host_system = HostSystem()
        payout = host_system.get_payout()
        self.assertTrue(itl_bsp_mock.get_payout.called)
        self.assertEqual(payout, Decimal('0.75'))
