from nfc_terminal import config
from nfc_terminal import gui
from nfc_terminal import keypad
from nfc_terminal import stages
import time

CURRENT_STAGE = None
if CURRENT_STAGE is None:
    CURRENT_STAGE = config.STAGES[0]

def main():
    while True:
        if CURRENT_STAGE == 'standby':
            # obviously GUI dont need to be initalized every time, so some more code will be needed here.
            # this is just fake calls to explain general structure I imply
            gui.initStageGui()
            keypad.checkKeyEntries()
            stages.doWhateverNeededForStandby()
        elif CURRENT_STAGE == 'enter_amount':
            gui.initStageGui()
            keypad.checkKeyEntries()
            stages.doWhateverNeededForThisStage()
        elif CURRENT_STAGE == 'pay_nfc':
            gui.initStageGui()
            keypad.checkKeyEntries()
            stages.doWhateverNeededForThisStage()
        elif CURRENT_STAGE == 'pay_qr':
            gui.initStageGui()
            keypad.checkKeyEntries()
            stages.doWhateverNeededForThisStage()
        elif CURRENT_STAGE == 'payment_successful':
            gui.initStageGui()
            keypad.checkKeyEntries()
            stages.doWhateverNeededForThisStage()
        elif CURRENT_STAGE == 'payment_cancelled':
            gui.initStageGui()
            keypad.checkKeyEntries()
            stages.doWhateverNeededForThisStage()

        time.sleep(0.1)
