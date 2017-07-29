from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class BSPLibraryMock(object):

    FAIL = -1
    PAYOUT_IDLE = 0x10
    PAYOUT_HOST_PENDING = 0x11
    PAYOUT_HOST_COMPLETE = 0x12
    PAYOUT_INCOMPLETE = 0x14

    APM_IDLE = 0x20
    APM_ACTIVE = 0x21
    APM_OUTOFSERVICE = 0x22

    BACKLIGHT_OFF = 0
    BACKLIGHT_LEVEL6 = 6

    def get_hw_version(self):
        return 0, 0, 0

    def get_lib_version(self):
        return 0, 0, 0

    def initialize(self):
        pass

    def get_apm_status(self):
        return self.APM_ACTIVE

    def add_credit(self, amount):
        pass

    def get_payout_status(self):
        return self.PAYOUT_IDLE

    def get_payout_amount(self):
        return 0

    def withdrawal_started(self, uid):
        pass

    def withdrawal_completed(self, uid, amount):
        pass

    def get_withdrawal_uid(self):
        return None

    def pay_cash(self, amount):
        pass

    def write_ndef(self, message):
        pass

    def erase_ndef(self):
        pass

    def enable_display(self):
        pass

    def disable_display(self):
        pass

    def set_backlight_level(self, level):
        pass

    def play_tone(self, freq, duration):
        pass


class BSPLibraryInterface(object):

    factor = 100

    def __init__(self, use_mock=True):
        if use_mock:
            self._module = BSPLibraryMock()
        else:
            import itl_bsp
            self._module = itl_bsp
        hw_version = self._module.get_hw_version()
        logger.info('ITL hardware v{0}.{1}.{2}'.format(*hw_version))
        lib_version = self._module.get_lib_version()
        logger.info('ITL BSP library v{0}.{1}.{2}'.format(*lib_version))
        self._module.initialize()
        self._module.enable_display()
        if self._module.get_apm_status() != self._module.APM_ACTIVE:
            raise RuntimeError
        logger.info('ITL BSP library initialization done')

    def add_credit(self, amount):
        """
        Accepts:
            amount: fiat amount, Decimal
        """
        coins = int(amount * self.factor)
        self._module.add_credit(coins)
        logger.info('credit added to host machine')

    def get_payout_status(self):
        """
        Returns current payout status:
            idle
            pending
            complete
            failed
        """
        status = self._module.get_payout_status()
        if status == self._module.PAYOUT_IDLE:
            # Do nothing
            return 'idle'
        elif status == self._module.PAYOUT_HOST_PENDING:
            # Show loader
            return 'pending'
        elif status == self._module.PAYOUT_HOST_COMPLETE:
            # Start withdrawal process
            return 'complete'
        elif status == self._module.PAYOUT_INCOMPLETE:
            # Get withdrawal UID
            return 'incomplete'
        elif status == self._module.FAIL:
            logger.error('payout error')
            return 'failed'
        else:
            logger.error('unknown payout status')

    def get_payout_amount(self):
        """
        Returns:
            amount: fiat amount to be paid, Decimal
        """
        coins = self._module.get_payout_amount()
        amount = Decimal(coins) / self.factor
        return amount

    def withdrawal_started(self, uid):
        """
        Accepts:
            uid: withdrawal UID, string
        """
        self._module.withdrawal_started(uid)
        logger.info('withdrawal UID saved to NVRAM')

    def withdrawal_completed(self, uid, amount):
        """
        Accepts:
            uid: withdrawal UID, string
            amount: fiat amount paid, Decimal
        """
        coins = int(amount * self.factor)
        self._module.withdrawal_completed(uid, coins)
        logger.info('withdrawal UID erased from NVRAM')

    def get_withdrawal_uid(self):
        """
        Returns:
            uid: withdrawal UID, string
        """
        self._module.get_withdrawal_uid()

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
        logger.info('NDEF message written')

    def erase_ndef(self):
        """
        Erases NDEF message
        """
        self._module.erase_ndef()
        logger.info('NDEF message erased')

    def enable_display(self):
        """
        Enables display
        """
        self._module.enable_display()
        self._module.set_backlight_level(self._module.BACKLIGHT_LEVEL6)
        logger.info('display enabled')

    def disable_display(self):
        """
        Disables display
        """
        self._module.disable_display()
        self._module.set_backlight_level(self._module.BACKLIGHT_OFF)
        logger.info('display disabled')

    def beep(self):
        self._module.play_tone(1000, 1000)
        logger.info('signal played')
