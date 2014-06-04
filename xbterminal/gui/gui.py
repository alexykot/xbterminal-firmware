# -*- coding: utf-8 -*-
import logging
import os
import sys
import time
from collections import deque

from PyQt4 import QtGui, QtCore

logger = logging.getLogger(__name__)

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


class GUI(QtGui.QWidget):

    def __init__(self):
        super(GUI, self).__init__()
        self.keys = deque(maxlen=5)
        # Initialize UI
        self.ui = appui.Ui_Form()
        self.ui.setupUi(self)
        self.ui.logo.setPixmap(QtGui.QPixmap(_fromUtf8(os.path.join(
            defaults.PROJECT_ABS_PATH,
            defaults.UI_IMAGES_PATH,
            'logo.png'))))
        self.ui.show_qr_btn.clicked.connect(self.qrBtnPressEvent)
        self.ui.skip_wifi_btn.clicked.connect(self.skipWiFiBtnPressEvent)
        self.ui.testnet_notice.hide()
        self.ui.wrong_passwd_lbl.hide()
        self.ui.connecting_lbl.hide()
        self.show()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()
        if event.key() == QtCore.Qt.Key_Return:
            xbterminal.runtime['CURRENT_STAGE'] = 'enter_amount'
            self.ui.main_stackedWidget.setCurrentIndex(6)
        self.keys.append(event.key())

    def closeEvent(self, event):
        xbterminal.runtime['CURRENT_STAGE'] = 'application_halt'

    def qrBtnPressEvent(self):
        xbterminal.runtime['screen_buttons']['qr_button'] = True

    def skipWiFiBtnPressEvent(self):
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

    def wifiListAddItem(self, ssid):
        self.ui.wifi_listWidget.addItem(ssid)

    def wifiListSelectItem(self, index):
        self.ui.wifi_listWidget.setCurrentRow(index)

    def wifiListSaveSelectedItem(self):
        ssid = self.ui.wifi_listWidget.currentItem().text()
        xbterminal.runtime['wifi']['selected_ssid'] = str(ssid)

    def wifiListClear(self):
        self.ui.wifi_listWidget.clear()

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

    def setText(self, widget_name, text):
        widget = getattr(self.ui, widget_name)
        widget.setText(text)

    def setImage(self, widget_name, image_path):
        widget = getattr(self.ui, widget_name)
        widget.setPixmap(QtGui.QPixmap(image_path))

    def setStyle(self, widget_name, css):
        widget = getattr(self.ui, widget_name)
        widget.setStyleSheet(css)

    @QtCore.pyqtSlot(str, tuple)
    def stageWorkerSlot(self, method_name, args):
        getattr(self, str(method_name))(*args)


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
