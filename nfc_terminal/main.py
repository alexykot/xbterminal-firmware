import time
import sys
from PyQt4 import QtGui, QtCore

import nfc_terminal
from nfc_terminal import defaults
from nfc_terminal import gui
from nfc_terminal.keypad import keypad
from nfc_terminal import stages
from nfc_terminal.helpers.configs import load_config
from nfc_terminal.helpers.log import write_msg_log


CURRENT_STAGE = None
if CURRENT_STAGE is None:
    CURRENT_STAGE = defaults.STAGES[0]

def main():
    nfc_terminal.helpers.configs.load_config()
    kp = keypad.keypad(columnCount=4)

    while True:
        if CURRENT_STAGE == 'standby':
            pass
            # gui_initalized = False
            # if not gui_initalized:
            #     app = QtGui.QApplication(sys.argv)
            #     gui = gui.GUI()
            #     gui_initalized = True
            #
            # key_code = kp.getKey()
            # if key_code is not None:
            #     CURRENT_STAGE = 'enter_amount'
            #     continue
        elif CURRENT_STAGE == 'enter_amount':
            pass
            # gui_initalized = False
            # if not gui_initalized:
            #     app = QtGui.QApplication(sys.argv)
            #     gui = gui.GUI()
            #     gui_initalized = True
            #
            # key_code = kp.getKey()
            # if key_code is not None:
            #     pass
        elif CURRENT_STAGE == 'pay_nfc':
            pass
            # gui.initStageGui()
            # key_code = keypad.key_detect()
            # stages.doWhateverNeededForThisStage(key_code)
        elif CURRENT_STAGE == 'pay_qr':
            pass
            # gui.initStageGui()
            # key_code = keypad.key_detect()
            # stages.doWhateverNeededForThisStage(key_code)
        elif CURRENT_STAGE == 'payment_successful':
            pass
            # gui.initStageGui()
            # key_code = keypad.key_detect()
            # stages.doWhateverNeededForThisStage(key_code)
        elif CURRENT_STAGE == 'payment_cancelled':
            pass
            # gui.initStageGui()
            # key_code = keypad.key_detect()
            # stages.doWhateverNeededForThisStage(key_code)

        print CURRENT_STAGE
        time.sleep(1)
