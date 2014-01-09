#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import sys
import os
import time

include_path = os.path.abspath(os.path.join(__file__, os.pardir))
sys.path.insert(0, include_path)

import xbterminal
import xbterminal.defaults as defaults
import xbterminal.main

xbterminal.defaults.PROJECT_ABS_PATH = include_path
#xbterminal.main.main()

import xbterminal.keypad
import xbterminal.keypad.keypad
import xbterminal.gui
import xbterminal.gui.ui
from xbterminal.gui import gui


global current_screen
current_screen = 0


def main():

    wifi_list = {1: "wifi_1", 2: "wifi_2", 3: "wifi_3"}
    wifi_update = True

    progress = 0

    # Setup GUI and local variables
    gui.runtime = {}
    gui.runtime['app'], gui.runtime['main_win'] = gui.initGUI()
    ui = gui.runtime['main_win'].ui

    xbterminal.gui.runtime = {}
    xbterminal.gui.runtime['app'], xbterminal.gui.runtime['main_win'] = gui.initGUI()
    ui = xbterminal.gui.runtime['main_win'].ui

    wifi_list = {1: "UDG",
                 2: "UDG Guest",
                 3: "65a High Street",
                 4: "asd ASDSAD%^&£ASGSDSD",
                 }

    screen_index = 0
    keypad = xbterminal.keypad.keypad.keypad()

    wifi_init = False
    while True:

        # At beginning of each loop push events
        try:
            xbterminal.gui.runtime['app'].sendPostedEvents()
            xbterminal.gui.runtime['app'].processEvents()
        except NameError:
            pass

        key_pressed = None
        try:
            key_pressed = keypad.getKey()
            if key_pressed is not None:
                if key_pressed == 'escape':

                    exit()
                time.sleep(0.2)
        except NameError:
            pass

        if screen_index == len(defaults.SCREENS):
            screen_index = 0

        if wifi_init == False and screen_index == defaults.SCREENS['choose_ssid']:
            for i in wifi_list.values():
               ui.listWidget.addItem(i)
            wifi_init = True

        if key_pressed is not None:
            if key_pressed == 'enter':
                screen_index = screen_index + 1
            elif  key_pressed == 'backspace':
                screen_index = screen_index - 1
            ui.stackedWidget.setCurrentIndex(screen_index)

        time.sleep(0.1)


main()