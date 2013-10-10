#!/usr/bin/python2.7
__author__ = 'tux'

import sys
import os
from PyQt4 import QtGui, QtCore
from PIL import Image
import qrcode
import ui_child as appui
#import keypad


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


def main():

    # Set filename for qr image, and ensure directory exists
    filename = current_dir() + "/img/" + "qrcode.png"
    ensure_dir(filename)

    app = QtGui.QApplication(sys.argv)


if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    Form = QtGui.QWidget()
    ui = appui.Ui_Custom_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())

    #main()