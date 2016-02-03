from decimal import Decimal
import unittest

from xbterminal.helpers.host import HostSystem


class HostSystemTestCase(unittest.TestCase):

    def test_cctalk(self):
        host_system = HostSystem(use_mock=True)
        host_system.add_credit(Decimal('1.25'))
        self.assertEqual(host_system._module.balance, 125)
        self.assertEqual(host_system.get_payout(), Decimal('1.25'))
        host_system.withdraw(Decimal('1.25'))
        self.assertEqual(host_system.get_payout(), Decimal(0))
