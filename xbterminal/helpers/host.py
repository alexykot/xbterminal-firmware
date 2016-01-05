from decimal import Decimal
import logging

try:
    import itl_bsp
except ImportError:
    itl_bsp = None

logger = logging.getLogger(__name__)


class HostSystem(object):

    factor = 100

    def __init__(self, disable=False):
        self._mod = itl_bsp if not disable else None
        if not self._mod:
            logger.info('host communication disabled')

    def add_credit(self, amount):
        """
        Accepts:
            amount: Decimal
        """
        if self._mod:
            self._mod.add_credit(int(amount * self.factor))

    def get_payout(self):
        """
        Returns:
            amount: Decimal
        """
        if self._mod:
            return Decimal(self._mod.get_payout()) / self.factor
        else:
            return Decimal(0)
