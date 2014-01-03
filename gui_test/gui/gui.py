# -*- coding: utf-8 -*-
import sys
from PyQt4 import QtGui, QtCore

import gui_test
from gui_test.gui import ui as appui


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
    main_win = GUI()
    main_win.ui.continue_lbl.setText("")

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
        global gui_test

        if k.key() == QtCore.Qt.Key_Escape:
            self.close()

        if k.key() == QtCore.Qt.Key_Return:
            self.ui.stackedWidget.setCurrentIndex(gui_test.runtime['CURRENT_SCREEN'])

    def closeEvent(self, QCloseEvent):
        global gui_test

        gui_test.runtime['CURRENT_STAGE'] = 'application_halt'

