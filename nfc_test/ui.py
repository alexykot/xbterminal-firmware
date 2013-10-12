# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui.ui'
#
# Created: Fri Oct 11 14:58:33 2013
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
        self.listWidget = QtGui.QListWidget(Form)
        self.listWidget.setEnabled(True)
        self.listWidget.setGeometry(QtCore.QRect(10, 190, 301, 41))
        self.listWidget.setObjectName(_fromUtf8("listWidget"))
        item = QtGui.QListWidgetItem()
        self.listWidget.addItem(item)
        item = QtGui.QListWidgetItem()
        self.listWidget.addItem(item)
        self.stackedWidget = QtGui.QStackedWidget(Form)
        self.stackedWidget.setGeometry(QtCore.QRect(0, 0, 320, 240))
        self.stackedWidget.setObjectName(_fromUtf8("stackedWidget"))
        self.screen1 = QtGui.QWidget()
        self.screen1.setObjectName(_fromUtf8("screen1"))
        self.idle_lbl = QtGui.QLabel(self.screen1)
        self.idle_lbl.setGeometry(QtCore.QRect(20, 30, 271, 181))
        font = QtGui.QFont()
        font.setPointSize(30)
        self.idle_lbl.setFont(font)
        self.idle_lbl.setWordWrap(True)
        self.idle_lbl.setObjectName(_fromUtf8("idle_lbl"))
        self.stackedWidget.addWidget(self.screen1)
        self.screen2 = QtGui.QWidget()
        self.screen2.setObjectName(_fromUtf8("screen2"))
        self.label_2 = QtGui.QLabel(self.screen2)
        self.label_2.setGeometry(QtCore.QRect(120, 80, 66, 17))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.stackedWidget.addWidget(self.screen2)

        self.retranslateUi(Form)
        #QtCore.QObject.connect(self.listWidget, QtCore.SIGNAL(_fromUtf8("currentRowChanged(int)")), self.stackedWidget.setCurrentIndex)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        __sortingEnabled = self.listWidget.isSortingEnabled()
        self.listWidget.setSortingEnabled(False)
        item = self.listWidget.item(0)
        item.setText(_translate("Form", "Page 1", None))
        item = self.listWidget.item(1)
        item.setText(_translate("Form", "Page 2", None))
        self.listWidget.setSortingEnabled(__sortingEnabled)
        self.idle_lbl.setText(_translate("Form", "Please press ENTER to start", None))
        self.label_2.setText(_translate("Form", "page 2", None))

