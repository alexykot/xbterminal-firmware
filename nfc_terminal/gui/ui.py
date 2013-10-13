# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui.ui'
#
# Created: Sun Oct 13 19:25:45 2013
#      by: PyQt4 UI code generator 4.10
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

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

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(320, 240)
        self.stackedWidget = QtGui.QStackedWidget(Form)
        self.stackedWidget.setGeometry(QtCore.QRect(0, 0, 320, 240))
        self.stackedWidget.setObjectName(_fromUtf8("stackedWidget"))
        self.screen1 = QtGui.QWidget()
        self.screen1.setObjectName(_fromUtf8("screen1"))
        self.idle_lbl = QtGui.QLabel(self.screen1)
        self.idle_lbl.setGeometry(QtCore.QRect(20, 30, 271, 191))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("DejaVu Sans"))
        font.setPointSize(30)
        self.idle_lbl.setFont(font)
        self.idle_lbl.setWordWrap(True)
        self.idle_lbl.setObjectName(_fromUtf8("idle_lbl"))
        self.stackedWidget.addWidget(self.screen1)
        self.screen2 = QtGui.QWidget()
        self.screen2.setObjectName(_fromUtf8("screen2"))
        self.amount = QtGui.QLabel(self.screen2)
        self.amount.setGeometry(QtCore.QRect(20, 60, 291, 51))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("DejaVu Sans"))
        font.setPointSize(30)
        self.amount.setFont(font)
        self.amount.setObjectName(_fromUtf8("amount"))
        self.lineEdit = QtGui.QLineEdit(self.screen2)
        self.lineEdit.setGeometry(QtCore.QRect(30, 130, 261, 51))
        font = QtGui.QFont()
        font.setPointSize(26)
        self.lineEdit.setFont(font)
        self.lineEdit.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.stackedWidget.addWidget(self.screen2)
        self.screen3 = QtGui.QWidget()
        self.screen3.setObjectName(_fromUtf8("screen3"))
        self.stackedWidget.addWidget(self.screen3)
        self.screen4 = QtGui.QWidget()
        self.screen4.setObjectName(_fromUtf8("screen4"))
        self.stackedWidget.addWidget(self.screen4)
        self.screen5 = QtGui.QWidget()
        self.screen5.setObjectName(_fromUtf8("screen5"))
        self.stackedWidget.addWidget(self.screen5)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.idle_lbl.setText(_translate("Form", "<html><head/><body><p align=\"center\">Please press</p><p align=\"center\"><span style=\" font-weight:600;\">ENTER</span></p><p align=\"center\">to begin</p></body></html>", None))
        self.amount.setText(_translate("Form", "Enter Amount", None))

