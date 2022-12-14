from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class BSPLibraryMock(object):

    FAIL = -1
    PAYOUT_IDLE = 0x10
    PAYOUT_HOST_PENDING = 0x11
    PAYOUT_HOST_COMPLETE = 0x12
    PAYOUT_INCOMPLETE = 0x14
    PAYOUT_APM_PENDING = 0x13

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

    def _call(self, method_name, *args):
        """
        Wrapper for ITL BSP calls for error handling
        """
        try:
            result = getattr(self._module, method_name)(*args)
        except Exception as error:
            logger.exception(error)
        else:
            if result == self._module.FAIL:
                logger.error('ITL BSP call failed')
            else:
                return result

    def add_credit(self, amount):
        """
        Accepts:
            amount: fiat amount, Decimal
        """
        coins = int(amount * self.factor)
        self._call('add_credit', coins)
        logger.info('credit added to host machine')

    def get_payout_status(self):
        """
        Returns current payout status:
            idle
            pending
            complete
            incomplete
        """
        status = self._call('get_payout_status')
        if status == self._module.PAYOUT_IDLE:
            # Do nothing
            return 'idle'
        elif status == self._module.PAYOUT_HOST_PENDING:
            # Show loader
            return 'pending'
        elif status == self._module.PAYOUT_HOST_COMPLETE:
            # Start withdrawal process
            return 'complete'
        elif status in [self._module.PAYOUT_INCOMPLETE,
                        self._module.PAYOUT_APM_PENDING]:
            # Get withdrawal UID
            return 'incomplete'
        elif status is None:
            pass
        else:
            logger.error('unknown payout status')

    def get_payout_amount(self):
        """
        Returns:
            amount: fiat amount to be paid, Decimal
        """
        coins = self._call('get_payout_amount')
        amount = Decimal(coins) / self.factor
        return amount

    def withdrawal_started(self, uid):
        """
        Accepts:
            uid: withdrawal UID, string
        """
        self._call('withdrawal_started', uid)
        logger.info('withdrawal UID saved to NVRAM')

    def withdrawal_completed(self, uid, amount):
        """
        Accepts:
            uid: withdrawal UID, string
            amount: fiat amount paid, Decimal
        """
        coins = int(amount * self.factor)
        self._call('withdrawal_completed', uid, coins)
        logger.info('withdrawal UID erased from NVRAM')

    def get_withdrawal_uid(self):
        """
        Returns:
            uid: withdrawal UID, string
        """
        uid = self._call('get_withdrawal_uid')
        if uid:
            return uid

    def pay_cash(self, amount):
        """
        Accepts:
            amount: fiat amount, Decimal
        """
        coins = int(amount * self.factor)
        self._call('pay_cash', coins)

    def write_ndef(self, message):
        """
        Writes NDEF message
        Accepts:
            message: string
        """
        self._call('write_ndef', message)
        logger.info('NDEF message written')

    def erase_ndef(self):
        """
        Erases NDEF message
        """
        self._call('erase_ndef')
        logger.info('NDEF message erased')

    def enable_display(self):
        """
        Enables display
        """
        self._call('enable_display')
        self._call('set_backlight_level', self._module.BACKLIGHT_LEVEL6)
        logger.info('display enabled')

    def disable_display(self):
        """
        Disables display
        """
        self._call('disable_display')
        self._call('set_backlight_level', self._module.BACKLIGHT_OFF)
        logger.info('display disabled')

    def beep(self):
        self._call('play_tone', 1000, 1000)
        logger.info('signal played')
