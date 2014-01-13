#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
from decimal import Decimal
import random
import time
import sys
import os
from PyQt4 import QtGui, QtCore

import gui_test
import gui_test.defaults as defaults
from gui_test.gui import gui


global current_screen
current_screen = 0

def main():

    wifi_list = {1: "wifi_1", 2: "wifi_2", 3: "wifi_3"}

    wifi_update = True

    progress = 0

    # Setup GUI and local variables
    gui_test.gui.runtime = {}
    gui_test.gui.runtime['app'], gui_test.gui.runtime['main_win'] = gui.initGUI()
    ui = gui_test.gui.runtime['main_win'].ui


    gui_test.runtime = {}
    run = gui_test.runtime
    run['CURRENT_SCREEN'] = "wait_scn"
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

        run['CURRENT_SCREEN'] = ui.stackedWidget.currentIndex() + 1

        if run['CURRENT_STAGE'] == 'application_halt':
            sys.exit()

        #if wifi_update == True:
        #    ui.stackedWidget.setCurrentIndex(1)
        #    for i in wifi_list.values():
        #        ui.listWidget.addItem(i)
        #    wifi_update = False

        #if ui.cancel_btn.connect.clicked() == True:
        #    ui.stackedWidget.currentIndex(0)


        #ui.listWidget.setCurrentRow()

        progress = progress + 1
        ui.progressBar.setValue(progress)

        if ui.listWidget.currentItem() != None:
            run['wifi'] = "WiFi - {}".format(ui.listWidget.currentItem().text())
            ui.wifi_lbl.setText(run['wifi'])

        time.sleep(0.1)


main()