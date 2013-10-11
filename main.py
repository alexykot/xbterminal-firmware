#!/usr/bin/python2.7
__author__ = 'tux'

import sys
import os
from PyQt4 import QtGui, QtCore
from PIL import Image
import qrcode
import events
import ui as appui

'''
Have to catch this import for testing GUI when not running on Pi
'''
try:
    import keypad
except ImportError:
    pass

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


'''
Class to initiate GUI, at the moment i can only seem to perform
actions on the GUI if its done like this
'''


class GUI(QtGui.QWidget):

    def __init__(self):
        super(GUI, self).__init__()
        self.initUI()
        self.signals_slots()
        self.keypad_detect()

    def initUI(self):

        self.Form = self
        self.ui = appui.Ui_Form()
        self.ui.setupUi(self.Form)
        self.Form.show()

    def keyPressEvent(self, k):

        if k.key() == QtCore.Qt.Key_Escape:
            self.close()

    def signals_slots(self):
        QtCore.QObject.connect(self.ui.listWidget, QtCore.SIGNAL(_fromUtf8("currentRowChanged(int)")), self.ui.stackedWidget.setCurrentIndex)


'''
def qr_gen(self):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data('Some data')
    qr.make(fit=True)

    img = qr.make_image()
    return img


def keyPressEvent(self, e):

    if e.key() == QtCore.Qt.Key_Escape:
        self.close()


def current_dir():
    dir = os.getcwd() + "/"
    return dir


def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)
'''

def main():
    '''
    # Set filename for qr image, and ensure directory exists
    filename = current_dir() + "/img/" + "qrcode.png"
    ensure_dir(filename)
    '''


if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    gui = GUI()
    sys.exit(app.exec_())

    #main()