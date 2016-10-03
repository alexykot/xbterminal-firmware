from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

PAYOUT_STATUS_IDLE = 0x10
PAYOUT_STATUS_PENDING = 0x11
PAYOUT_STATUS_COMPLETE = 0x12

APM_STATUS_IDLE = 0x20
APM_STATUS_ACTIVE = 0x21
APM_STATUS_OUTOFSERVICE = 0x22


class CCTalkMock(object):

    def initialize(self):
        pass

    def get_apm_status(self):
        return APM_STATUS_ACTIVE

    def add_credit(self, amount):
        pass

    def get_payout_status(self):
        return PAYOUT_STATUS_IDLE

    def get_payout(self):
        return 0

    def pay_cash(self, amount):
        pass

    def write_ndef(self, message):
        pass

    def erase_ndef(self):
        pass


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
        self._module.initialize()
        assert self._module.get_apm_status() == APM_STATUS_ACTIVE
        logger.info('host communication - init done')

    def add_credit(self, amount):
        """
        Accepts:
            amount: fiat amount, Decimal
        """
        coins = int(amount * self.factor)
        self._module.add_credit(coins)

    def get_payout(self):
        """
        Returns:
            amount: Decimal
        """
        status = self._module.get_payout_status()
        if status == PAYOUT_STATUS_IDLE:
            return None
        elif status == PAYOUT_STATUS_PENDING:
            logger.debug('host communication - payout pending')
            return None
        elif status == PAYOUT_STATUS_COMPLETE:
            logger.debug('host communication - payout completed')
            coins = self._module.get_payout()
            amount = Decimal(coins) / self.factor
            return amount
        else:
            raise AssertionError

    def pay_cash(self, amount):
        """
        Accepts:
            amount: fiat amount, Decimal
        """
        coins = int(amount * self.factor)
        self._module.pay_cash(coins)

    def write_ndef(self, message):
        """
        Writes NDEF message
        Accepts:
            message: string
        """
        self._module.write_ndef(message)

    def erase_ndef(self):
        """
        Erases NDEF message
        """
        self._module.erase_ndef()
