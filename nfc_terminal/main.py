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

    # Load configs
    nfc_terminal.helpers.configs.load_config()

    # Function global variables
    time_const = time.time()
    gui_initialized = False
    current_screen = None
    if defaults.CURRENT_STAGE is None:
        defaults.CURRENT_STAGE = defaults.STAGES[0]
    CURRENT_KEY = None

    try:
        kp = keypad.keypad(columnCount=4)
    except NameError:
        pass

    write_msg_log("STAGE: Initialisation", 'DEBUG')

    while True:

        time_current = time.time()
        time_diff = time_current - time_const

        # At beginning of each loop push events
        try:
            app.sendPostedEvents()
            app.processEvents()
        except NameError:
            pass

        try:
            key_code = kp.getKey()
            if key_code is not None:
                write_msg_log("KEYPAD: Key pressed - {}".format(key_code), 'DEBUG')
                CURRENT_KEY = key_code
        except NameError:
            pass

        # Log what stage we are on and check screen
        if time_diff > 5:
            write_msg_log("STAGE: {}".format(defaults.CURRENT_STAGE), 'DEBUG')
            write_msg_log("Current Screen - {}".format(current_screen), 'DEBUG')
            time_const = time_current

        # Lets setup the GUI before any other stage, then let it loop back to forced event setting
        if gui_initialized is False:

            write_msg_log("STAGE: {} - Trying to launch GUI".format("GUI"), 'DEBUG')
            app = QtGui.QApplication(sys.argv)
            main_win = gui.GUI()
            write_msg_log("STAGE: {} - GUI Loaded".format("GUI"), 'DEBUG')
            gui_initialized = True
            defaults.GUI_STATE = 'active'
            current_screen = main_win.ui.stackedWidget.currentIndex()

            # Other specific GUI changes prior to loading
            #main_win.ui.listWidget.setVisible(False)

        if defaults.CURRENT_STAGE == 'standby':

            if CURRENT_KEY == "D" or defaults.CURRENT_STAGE == 'enter_amount':

                main_win.ui.stackedWidget.setCurrentIndex(1)
                current_screen = main_win.ui.stackedWidget.currentIndex()
                CURRENT_STAGE = 'enter_amount'
                continue

        elif defaults.CURRENT_STAGE == 'enter_amount':

            entered_text = "0"

            main_win.ui.lineEdit.setText(entered_text)

            # gui_initalized = False
            # if not gui_initalized:
            #     app = QtGui.QApplication(sys.argv)
            #     gui = gui.GUI()
            #     gui_initalized = True
            #
            # key_code = kp.getKey()
            # if key_code is not None:
            #     pass
        elif defaults.CURRENT_STAGE == 'pay_nfc':
            pass
            # gui.initStageGui()
            # key_code = keypad.key_detect()
            # stages.doWhateverNeededForThisStage(key_code)
        elif defaults.CURRENT_STAGE == 'pay_qr':
            pass
            # gui.initStageGui()
            # key_code = keypad.key_detect()
            # stages.doWhateverNeededForThisStage(key_code)
        elif defaults.CURRENT_STAGE == 'payment_successful':
            pass
            # gui.initStageGui()
            # key_code = keypad.key_detect()
            # stages.doWhateverNeededForThisStage(key_code)
        elif defaults.CURRENT_STAGE == 'payment_cancelled':
            pass
            # gui.initStageGui()
            # key_code = keypad.key_detect()
            # stages.doWhateverNeededForThisStage(key_code)

        if defaults.GUI_STATE == 'inactive':
            sys.exit()

        time.sleep(0.05)
