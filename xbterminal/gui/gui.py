# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtGui, QtCore

import xbterminal
from xbterminal.gui import ui as appui
from xbterminal import defaults
from xbterminal.helpers.log import log


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
    main_win.ui.continue_lbl.setText("")
    main_win.ui.currency_lbl.setText(xbterminal.remote_config['MERCHANT_CURRENCY_SIGN_PREFIX'])
    main_win.ui.currency_lbl_2.setText(xbterminal.remote_config['MERCHANT_CURRENCY_SIGN_PREFIX'])

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
