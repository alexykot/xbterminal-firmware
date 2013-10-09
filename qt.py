__author__ = 'tux'

import sys
import os
from PyQt4 import QtGui, QtCore
from PIL import Image
import qrcode
#import keypad


class Application(QtGui.QWidget):

    def __init__(self):
        super(Application, self).__init__()

        self.initUI()

    def initUI(self):

        # Initialise grid
        grid = QtGui.QGridLayout()

        self.title = QtGui.QLabel("Title", self)

        # Set grid positioning of elements
        grid.addWidget(self.title, 0, 2)
        grid.addWidget(QtGui.QLabel('content'), 0, 0)

        self.setLayout(grid)

        self.setGeometry(300, 300, 550, 550)
        self.setWindowTitle('Application')
        self.showFullScreen()

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
    ex = Application()

    ex.qr_gen().save(filename)
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()