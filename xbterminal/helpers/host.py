from decimal import Decimal

try:
    import itl_bsp
except ImportError:
    itl_bsp = None


class HostSystem(object):

    factor = 100

    def add_credit(self, amount):
        """
        Accepts:
            amount: Decimal
        """
        if itl_bsp:
            itl_bsp.add_credit(int(amount * self.factor))

    def get_payout(self):
        """
        Returns:
            amount: Decimal
        """
        if itl_bsp:
            return Decimal(itl_bsp.get_payout()) / self.factor
        else:
            return Decimal(0)
