# -*- coding: utf-8 -*-
import os
import sys
from PyQt4 import QtGui, QtCore
import time

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

def initGUI():
    global xbterminal

    app = QtGui.QApplication(sys.argv)
    app.setOverrideCursor(QtGui.QCursor(QtCore.Qt.BlankCursor))

    main_win = GUI()

    return app, main_win

# Class to initiate GUI, at the moment i can only seem to perform actions on the GUI if its done like this
class GUI(QtGui.QWidget):
    def __init__(self):
        super(GUI, self).__init__()
        self.initUI()

    def initUI(self):

        self.Form = self
        self.ui = appui.Ui_Form()
        self.ui.setupUi(self.Form)
        self.Form.show()
        self.ui.logo.setPixmap(QtGui.QPixmap(_fromUtf8(os.path.join(defaults.PROJECT_ABS_PATH, defaults.UI_IMAGES_PATH, 'logo.png'))))
        self.ui.show_qr_btn.clicked.connect(self.qrBntPressEvent)
        self.ui.skip_wifi_btn.clicked.connect(self.skipWiFiBntPressEvent)



        ''' Runtime GUI changes '''
        #self.ui.listWidget.setVisible(False)
        #self.Form.showFullScreen()


    #QT Keypress Events
    def keyPressEvent(self, k):
        global xbterminal

        if k.key() == QtCore.Qt.Key_Escape:
            self.close()

        if k.key() == QtCore.Qt.Key_Return:
            xbterminal.runtime['CURRENT_STAGE'] = 'enter_amount'
            self.ui.stackedWidget.setCurrentIndex(6)

    def closeEvent(self, QCloseEvent):
        global xbterminal
        xbterminal.runtime['CURRENT_STAGE'] = 'application_halt'

    def qrBntPressEvent(self):
        global xbterminal
        xbterminal.runtime['screen_buttons']['qr_button'] = True

    def skipWiFiBntPressEvent(self):
        global xbterminal
        xbterminal.runtime['screen_buttons']['skip_wifi'] = True


def advanceLoadingProgressBar(level):
    global xbterminal

    xbterminal.gui.runtime['main_win'].ui.progressBar_percent.setValue(level)
    time.sleep(0.3)

def formatCharSelectHelperHMTL(char_tupl, char_selected = None):
    char_list = []

    for index, char in enumerate(char_tupl):
        if char_selected == char:
            char_list.append("<strong><font color=\"#333333\" size=\"5\">{char_selected}</font></strong>".format(char_selected=char))
        else:
            char_list.append(str(char))

    char_string = ' '.join(char_list)

    return "<html><head/><body><p align=\"center\"><font color=\"#666666\">{char_string}</font></p></body></html>".format(char_string=char_string)
