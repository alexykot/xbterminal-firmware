# -*- coding: utf-8 -*-
import os
import sys
import time
from collections import deque

from PyQt4 import QtGui, QtCore

import xbterminal
from xbterminal.gui import ui as appui
from xbterminal import defaults

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


# Class to initiate GUI, at the moment i can only seem to perform actions on the GUI if its done like this
class GUI(QtGui.QWidget):
    def __init__(self):
        super(GUI, self).__init__()
        self.initUI()
        self.keys = deque(maxlen=5)

    def initUI(self):
        global xbterminal

        self.Form = self
        self.ui = appui.Ui_Form()
        self.ui.setupUi(self.Form)
        self.Form.show()
        self.ui.logo.setPixmap(QtGui.QPixmap(_fromUtf8(os.path.join(defaults.PROJECT_ABS_PATH, defaults.UI_IMAGES_PATH, 'logo.png'))))
        self.ui.show_qr_btn.clicked.connect(self.qrBntPressEvent)
        self.ui.skip_wifi_btn.clicked.connect(self.skipWiFiBntPressEvent)
        self.ui.testnet_notice.hide()
        self.ui.wrong_passwd_lbl.hide()
        self.ui.connecting_lbl.hide()

        ''' Runtime GUI changes '''
        #self.ui.listWidget.setVisible(False)
        #self.Form.showFullScreen()


    #QT Keypress Events
    def keyPressEvent(self, event):
        global xbterminal

        if event.key() == QtCore.Qt.Key_Escape:
            self.close()

        if event.key() == QtCore.Qt.Key_Return:
            xbterminal.runtime['CURRENT_STAGE'] = 'enter_amount'
            self.ui.main_stackedWidget.setCurrentIndex(6)

        self.keys.append(event.key())

    def closeEvent(self, QCloseEvent):
        global xbterminal
        xbterminal.runtime['CURRENT_STAGE'] = 'application_halt'

    def qrBntPressEvent(self):
        global xbterminal
        xbterminal.runtime['screen_buttons']['qr_button'] = True

    def skipWiFiBntPressEvent(self):
        global xbterminal
        xbterminal.runtime['screen_buttons']['skip_wifi'] = True

    def toggleTestnetNotice(self, show):
        if show:
            self.ui.testnet_notice.show()
        else:
            self.ui.testnet_notice.hide()

    def toggleWifiConnectingState(self, show):
        if show:
            self.ui.connecting_lbl.show()
            self.ui.password_input.setEnabled(False)
            self.ui.password_input.setStyleSheet('background: #BBBBBB')
        else:
            self.ui.connecting_lbl.hide()
            self.ui.password_input.setEnabled(True)
            self.ui.password_input.setStyleSheet('background: #FFFFFF')

    def toggleWifiWrongPasswordState(self, show):
        if show:
            self.ui.wrong_passwd_lbl.show()
            self.ui.password_input.setStyleSheet('background: #B33A3A')
        else:
            self.ui.wrong_passwd_lbl.hide()
            self.ui.password_input.setStyleSheet('background: #FFFFFF')

    def advanceLoadingProgressBar(self, level):
        self.ui.progressBar_percent.setValue(level)
        time.sleep(0.3)

    def currentScreen(self):
        screen_index = self.ui.main_stackedWidget.currentIndex()
        for screen_name, i in defaults.SCREENS.items():
            if i == screen_index:
                return screen_name

    def showScreen(self, screen_name):
        screen_index = defaults.SCREENS[screen_name]
        self.ui.main_stackedWidget.setCurrentIndex(screen_index)

    def setImage(self, widget_name, image_path):
        widget = getattr(self.ui, widget_name)
        widget.setPixmap(QtGui.QPixmap(image_path))


def initGUI():
    application = QtGui.QApplication(sys.argv)
    application.setOverrideCursor(QtGui.QCursor(QtCore.Qt.BlankCursor))

    main_window = GUI()

    return application, main_window


def formatCharSelectHelperHMTL(char_tupl, char_selected = None):
    char_list = []

    for index, char in enumerate(char_tupl):
        if char_selected == char:
            char_list.append("<strong><font color=\"#333333\" size=\"5\">{char_selected}</font></strong>".format(char_selected=char))
        else:
            char_list.append(str(char))

    char_string = ' '.join(char_list)

    return "<html><head/><body><p align=\"center\"><font color=\"#666666\">{char_string}</font></p></body></html>".format(char_string=char_string)
