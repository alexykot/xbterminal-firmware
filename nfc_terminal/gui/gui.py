'''
Class to initiate GUI, at the moment i can only seem to perform
actions on the GUI if its done like this
'''

from PyQt4 import QtGui, QtCore
from nfc_terminal.gui import ui as appui

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
        self.initUI()
        #self.signals_slots()
        #self.keypad_detect()

    def initUI(self):

        self.Form = self
        self.ui = appui.Ui_Form()
        self.ui.setupUi(self.Form)
        self.Form.show()

        ''' Runtime GUI changes '''
        #self.ui.listWidget.setVisible(False)


    ''' QT Keypress Events '''
    def keyPressEvent(self, k):

        if k.key() == QtCore.Qt.Key_Escape:
            self.close()

        if k.key() == QtCore.Qt.Key_Return:
            self.ui.stackedWidget.setCurrentIndex(1)

    def signals_slots(self):
        QtCore.QObject.connect(self.ui.listWidget, QtCore.SIGNAL(_fromUtf8("currentRowChanged(int)")),
                               self.ui.stackedWidget.setCurrentIndex)
