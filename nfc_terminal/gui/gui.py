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
