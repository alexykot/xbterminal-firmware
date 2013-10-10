import time

from nfc_terminal import defaults
from nfc_terminal import gui
from nfc_terminal import keypad
from nfc_terminal import stages
from nfc_terminal import helpers


CURRENT_STAGE = None
if CURRENT_STAGE is None:
    CURRENT_STAGE = defaults.STAGES[0]

def main():
    helpers.load_config()

    while True:
        if CURRENT_STAGE == 'standby':
            # obviously GUI dont need to be initalized every time, so some more code will be needed here.
            # this is just fake calls to explain general structure I imply
            gui.initStageGui()
            key_code = keypad.key_detect()
            stages.doWhateverNeededForThisStage(key_code)
        elif CURRENT_STAGE == 'enter_amount':
            gui.initStageGui()
            key_code = keypad.key_detect()
            stages.doWhateverNeededForThisStage(key_code)
        elif CURRENT_STAGE == 'pay_nfc':
            gui.initStageGui()
            key_code = keypad.key_detect()
            stages.doWhateverNeededForThisStage(key_code)
        elif CURRENT_STAGE == 'pay_qr':
            gui.initStageGui()
            key_code = keypad.key_detect()
            stages.doWhateverNeededForThisStage(key_code)
        elif CURRENT_STAGE == 'payment_successful':
            gui.initStageGui()
            key_code = keypad.key_detect()
            stages.doWhateverNeededForThisStage(key_code)
        elif CURRENT_STAGE == 'payment_cancelled':
            gui.initStageGui()
            key_code = keypad.key_detect()
            stages.doWhateverNeededForThisStage(key_code)

        time.sleep(0.1)
