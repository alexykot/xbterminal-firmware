import time
import sys
from PyQt4 import QtGui, QtCore

import nfc_terminal
from nfc_terminal import defaults
from nfc_terminal.gui import gui
from nfc_terminal import stages
from nfc_terminal.helpers.configs import load_config
from nfc_terminal.helpers.log import write_msg_log
try:
    from nfc_terminal.keypad import keypad
except ImportError:
    pass


def main():

    write_msg_log("STAGE: Initialisation", 'DEBUG')

    CURRENT_STAGE = None
    if CURRENT_STAGE is None:
        CURRENT_STAGE = defaults.STAGES[0]

    nfc_terminal.helpers.configs.load_config()

    try:
        kp = keypad.keypad(columnCount=4)
    except NameError:
        pass


    while True:
        if CURRENT_STAGE == 'standby':
            write_msg_log("STAGE: {}".format(CURRENT_STAGE), 'DEBUG')

            gui_initialized = False
            current_screen = None
            if gui_initialized is False:
                write_msg_log("STAGE: {} - Trying to launch GUI".format(CURRENT_STAGE), 'DEBUG')
                app = QtGui.QApplication(sys.argv)
                main_win = gui.GUI()
                write_msg_log("STAGE: {} - GUI Loaded".format(CURRENT_STAGE), 'DEBUG')
                gui_initialized = True
                current_screen = main_win.ui.stackedWidget.currentIndex()
                main_win.ui.listWidget.setVisible(False)
                sys.exit(app.exec_())
                #main.ui.listWidget.setVisible(False)

            write_msg_log("Current Screen - {}".format(current_screen), 'DEBUG')

            if gui_initialized is True and current_screen == 1:
                CURRENT_STAGE = 'enter_amount'
                continue

            key_code = kp.getKey()
            if key_code is not None:
                 CURRENT_STAGE = 'enter_amount'
                 continue
        elif CURRENT_STAGE == 'enter_amount':
            write_msg_log("STAGE: {}".format(CURRENT_STAGE), 'DEBUG')
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
