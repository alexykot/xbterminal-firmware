from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class CCTalkMock(object):

    def __init__(self):
        self.balance = 0

    def add_credit(self, amount):
        self.balance += amount

    def withdraw(self, amount):
        assert amount == self.balance
        self.balance -= amount

    def get_payout(self):
        return self.balance


class HostSystem(object):

    factor = 100

    def __init__(self, use_mock=True):
        if use_mock:
            self._module = CCTalkMock()
            logger.info('host communication - using cctalk mock')
        else:
            import itl_bsp
            self._module = itl_bsp
            logger.info('host communication - using ITL BSP lib')

    def add_credit(self, amount):
        """
        Accepts:
            amount: Decimal
        """
        self._module.add_credit(int(amount * self.factor))

    def withdraw(self, amount):
        if hasattr(self._module, 'withdraw'):
            self._module.withdraw(int(amount * self.factor))

    def get_payout(self):
        """
        Returns:
            amount: Decimal
        """
        return Decimal(self._module.get_payout()) / self.factor
