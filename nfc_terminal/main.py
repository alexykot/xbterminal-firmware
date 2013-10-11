import time
import sys
from PyQt4 import QtGui, QtCore

from nfc_terminal import defaults
from nfc_terminal import gui
from nfc_terminal import keypad
from nfc_terminal import stages
from nfc_terminal import helpers
from nfc_terminal.helpers.log import write_msg_log


CURRENT_STAGE = None
if CURRENT_STAGE is None:
    CURRENT_STAGE = defaults.STAGES[0]

def main():
    helpers.load_config()
    kp = keypad.keypad.keypad(columnCount=4)

    while True:
        if CURRENT_STAGE == 'standby':
            gui_initalized = False
            if not gui_initalized:
                app = QtGui.QApplication(sys.argv)
                gui = gui.GUI()
                gui_initalized = True

            key_code = kp.getKey()
            if key_code is not None:
                CURRENT_STAGE = 'enter_amount'
                continue

        elif CURRENT_STAGE == 'enter_amount':
            gui_initalized = False
            if not gui_initalized:
                app = QtGui.QApplication(sys.argv)
                gui = gui.GUI()
                gui_initalized = True

            key_code = kp.getKey()
            if key_code is not None:
                pass
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

        time.sleep(0.01)
