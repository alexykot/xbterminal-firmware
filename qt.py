__author__ = 'tux'

import sys
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
        self.show()

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


def main():

    filename = "/home/tux/coding/nfc/image.png"

    app = QtGui.QApplication(sys.argv)
    ex = Application()

    #ex.qr_gen().save(filename)

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()