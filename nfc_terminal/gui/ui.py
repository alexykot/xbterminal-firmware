# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui.ui'
#
# Created: Mon Oct 14 14:29:22 2013
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
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("DejaVu Sans"))
        self.stackedWidget.setFont(font)
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
        self.amount_lbl = QtGui.QLabel(self.screen2)
        self.amount_lbl.setGeometry(QtCore.QRect(20, 60, 291, 51))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("DejaVu Sans"))
        font.setPointSize(30)
        self.amount_lbl.setFont(font)
        self.amount_lbl.setObjectName(_fromUtf8("amount_lbl"))
        self.amount_text = QtGui.QLineEdit(self.screen2)
        self.amount_text.setGeometry(QtCore.QRect(60, 130, 231, 51))
        font = QtGui.QFont()
        font.setPointSize(26)
        self.amount_text.setFont(font)
        self.amount_text.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.amount_text.setObjectName(_fromUtf8("amount_text"))
        self.continue_lbl = QtGui.QLabel(self.screen2)
        self.continue_lbl.setGeometry(QtCore.QRect(110, 180, 181, 20))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("DejaVu Sans"))
        self.continue_lbl.setFont(font)
        self.continue_lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.continue_lbl.setObjectName(_fromUtf8("continue_lbl"))
        self.gbp_lbl = QtGui.QLabel(self.screen2)
        self.gbp_lbl.setGeometry(QtCore.QRect(30, 130, 31, 61))
        self.gbp_lbl.setObjectName(_fromUtf8("gbp_lbl"))
        self.stackedWidget.addWidget(self.screen2)
        self.screen3 = QtGui.QWidget()
        self.screen3.setObjectName(_fromUtf8("screen3"))
        self.gbp_lbl_2 = QtGui.QLabel(self.screen3)
        self.gbp_lbl_2.setGeometry(QtCore.QRect(10, 20, 31, 61))
        self.gbp_lbl_2.setObjectName(_fromUtf8("gbp_lbl_2"))
        self.label = QtGui.QLabel(self.screen3)
        self.label.setGeometry(QtCore.QRect(50, 30, 131, 41))
        font = QtGui.QFont()
        font.setPointSize(30)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.gbp_lbl_3 = QtGui.QLabel(self.screen3)
        self.gbp_lbl_3.setGeometry(QtCore.QRect(10, 60, 31, 61))
        self.gbp_lbl_3.setObjectName(_fromUtf8("gbp_lbl_3"))
        self.label_2 = QtGui.QLabel(self.screen3)
        self.label_2.setGeometry(QtCore.QRect(50, 70, 131, 41))
        font = QtGui.QFont()
        font.setPointSize(30)
        self.label_2.setFont(font)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.stackedWidget.addWidget(self.screen3)
        self.screen4 = QtGui.QWidget()
        self.screen4.setObjectName(_fromUtf8("screen4"))
        self.stackedWidget.addWidget(self.screen4)
        self.screen5 = QtGui.QWidget()
        self.screen5.setObjectName(_fromUtf8("screen5"))
        self.idle_lbl_2 = QtGui.QLabel(self.screen5)
        self.idle_lbl_2.setGeometry(QtCore.QRect(20, 30, 271, 191))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("DejaVu Sans"))
        font.setPointSize(30)
        self.idle_lbl_2.setFont(font)
        self.idle_lbl_2.setWordWrap(True)
        self.idle_lbl_2.setObjectName(_fromUtf8("idle_lbl_2"))
        self.stackedWidget.addWidget(self.screen5)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.idle_lbl.setText(_translate("Form", "<html><head/><body><p align=\"center\">Please press</p><p align=\"center\"><span style=\" font-weight:600;\">ENTER</span></p><p align=\"center\">to begin</p></body></html>", None))
        self.amount_lbl.setText(_translate("Form", "Enter Amount", None))
        self.continue_lbl.setText(_translate("Form", "press enter to continue", None))
        self.gbp_lbl.setText(_translate("Form", "<html><head/><body><p><span style=\" font-size:36pt; font-weight:600;\">£</span></p></body></html>", None))
        self.gbp_lbl_2.setText(_translate("Form", "<html><head/><body><p><span style=\" font-size:36pt; font-weight:600;\">£</span></p></body></html>", None))
        self.label.setText(_translate("Form", "0", None))
        self.gbp_lbl_3.setText(_translate("Form", "<html><head/><body><p><span style=\" font-size:36pt; font-weight:600;\">฿</span></p></body></html>", None))
        self.label_2.setText(_translate("Form", "0", None))
        self.idle_lbl_2.setText(_translate("Form", "<html><head/><body><p align=\"center\">Payment</p><p align=\"center\">Successful</p></body></html>", None))

