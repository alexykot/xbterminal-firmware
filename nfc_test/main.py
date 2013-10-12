#!/usr/bin/python2.7
from nfc_test import gui

__author__ = 'tux'

import sys
from PyQt4 import QtGui, QtCore

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
    gui = gui.GUI()
    sys.exit(app.exec_())

    #main()