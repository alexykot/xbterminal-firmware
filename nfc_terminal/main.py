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

    # enter_amount global variables
    entered_text = "0"
    digits = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

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
                time.sleep(0.1)
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
            main_win.ui.cotinue_lbl.setVisible(False)

        if defaults.CURRENT_STAGE == 'standby':

            if CURRENT_KEY == "D" or defaults.CURRENT_STAGE == 'enter_amount':

                main_win.ui.stackedWidget.setCurrentIndex(1)
                current_screen = main_win.ui.stackedWidget.currentIndex()
                defaults.CURRENT_STAGE = 'enter_amount'
                continue

        elif defaults.CURRENT_STAGE == 'enter_amount':

            if key_code in digits or key_code is ".":
                if entered_text == "0" and key_code is not None:
                    entered_text = str(key_code)
                    main_win.ui.cotinue_lbl.setVisible(True)
                elif entered_text != "0" and key_code is not None:
                    entered_text += str(key_code)

            if key_code == "A":
                write_msg_log("{}".format(entered_text), 'DEBUG')
                backspace = entered_text[:-1]
                write_msg_log("{}".format(backspace), 'DEBUG')
                entered_text = backspace
                write_msg_log("backspace", 'DEBUG')

            main_win.ui.amount_text.setText(entered_text)

            if key_code is "D":
                defaults.CURRENT_STAGE = 'pay_nfc'
                main_win.ui.stackedWidget.setCurrentIndex(2)
                current_screen = main_win.ui.stackedWidget.currentIndex()

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
