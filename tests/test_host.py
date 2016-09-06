from decimal import Decimal
import unittest

from xbterminal.rpc.utils.host import HostSystem


class HostSystemTestCase(unittest.TestCase):

    def test_cctalk_mock(self):
        host_system = HostSystem(use_mock=True)
        self.assertIsNone(host_system.get_payout())
        host_system.add_credit(Decimal('1.25'))
        host_system.pay_cash(Decimal('1.25'))
        self.assertIsNone(host_system.get_payout())
