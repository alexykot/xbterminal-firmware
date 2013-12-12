# -*- coding: utf-8 -*-
from decimal import Decimal
import time
import sys
import os
from PyQt4 import QtGui, QtCore

import gui_test
import gui_test.defaults as defaults
from gui_test.gui import gui

def main():

    wifi_list = {1: "wifi_1", 2: "wifi_2", 3: "wifi_3"}

    wifi_update = True

    # Setup GUI and local variables
    gui_test.gui.runtime = {}
    gui_test.gui.runtime['app'], gui_test.gui.runtime['main_win'] = gui.initGUI()
    ui = gui_test.gui.runtime['main_win'].ui


    gui_test.runtime = {}
    run = gui_test.runtime
    run['CURRENT_STAGE'] = defaults.STAGES[0]
    run['amount_to_pay_fiat'] = None
    run['amount_to_pay_btc'] = None
    run['key_pressed'] = None
    run['last_activity_timestamp'] = None
    run['current_text_piece'] = 'decimal'
    run['display_value_unformatted'] = ''
    run['display_value_formatted'] = ''
    run['wifi'] = 'WiFi'


    while True:
        # At beginning of each loop push events
        try:
            gui_test.gui.runtime['app'].sendPostedEvents()
            gui_test.gui.runtime['app'].processEvents()
        except NameError:
            pass

        if run['CURRENT_STAGE'] == 'application_halt':
            sys.exit()

        if wifi_update == True:
            ui.stackedWidget.setCurrentIndex(6)
            for i in wifi_list.values():
                ui.listWidget.addItem(i)
            wifi_update = False

        if ui.listWidget.currentItem() != None:
            run['wifi'] = "WiFi - {}".format(ui.listWidget.currentItem().text())
            ui.wifi_lbl.setText(run['wifi'])

        time.sleep(0.1)


main()