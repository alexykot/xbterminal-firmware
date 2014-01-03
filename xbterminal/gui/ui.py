# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui.ui'
#
# Created: Thu Jan  2 09:07:26 2014
#      by: PyQt4 UI code generator 4.10.3
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
        Form.resize(480, 272)
        self.stackedWidget = QtGui.QStackedWidget(Form)
        self.stackedWidget.setGeometry(QtCore.QRect(0, 0, 480, 272))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("DejaVu Sans"))
        self.stackedWidget.setFont(font)
        self.stackedWidget.setObjectName(_fromUtf8("stackedWidget"))

        self.loading_screen = QtGui.QWidget()
        self.loading_screen.setObjectName(_fromUtf8("loading_screen"))
        self.progressBar = QtGui.QProgressBar(self.loading_screen)
        self.progressBar.setGeometry(QtCore.QRect(180, 170, 118, 23))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.label_2 = QtGui.QLabel(self.loading_screen)
        self.label_2.setGeometry(QtCore.QRect(160, 90, 211, 41))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.stackedWidget.addWidget(self.loading_screen)

        self.screen1 = QtGui.QWidget()
        self.screen1.setObjectName(_fromUtf8("screen1"))
        self.idle_lbl = QtGui.QLabel(self.screen1)
        self.idle_lbl.setGeometry(QtCore.QRect(100, 40, 271, 191))
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
        self.amount_lbl.setGeometry(QtCore.QRect(100, 50, 291, 51))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("DejaVu Sans"))
        font.setPointSize(30)
        self.amount_lbl.setFont(font)
        self.amount_lbl.setObjectName(_fromUtf8("amount_lbl"))
        self.amount_text = QtGui.QLineEdit(self.screen2)
        self.amount_text.setGeometry(QtCore.QRect(60, 130, 361, 51))
        font = QtGui.QFont()
        font.setPointSize(26)
        self.amount_text.setFont(font)
        self.amount_text.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.amount_text.setObjectName(_fromUtf8("amount_text"))
        self.amount_text.setCursor(QtGui.QCursor(QtCore.Qt.BlankCursor))
        self.continue_lbl = QtGui.QLabel(self.screen2)
        self.continue_lbl.setGeometry(QtCore.QRect(240, 180, 181, 20))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("DejaVu Sans"))
        self.continue_lbl.setFont(font)
        self.continue_lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.continue_lbl.setObjectName(_fromUtf8("continue_lbl"))
        self.currency_lbl = QtGui.QLabel(self.screen2)
        self.currency_lbl.setGeometry(QtCore.QRect(30, 130, 31, 61))
        font = QtGui.QFont()
        font.setPointSize(36)
        font.setBold(True)
        font.setWeight(75)
        self.currency_lbl.setFont(font)
        self.currency_lbl.setObjectName(_fromUtf8("currency_lbl"))
        self.stackedWidget.addWidget(self.screen2)

        self.screen3 = QtGui.QWidget()
        self.screen3.setObjectName(_fromUtf8("screen3"))
        self.currency_lbl_2 = QtGui.QLabel(self.screen3)
        self.currency_lbl_2.setGeometry(QtCore.QRect(10, 20, 31, 61))
        font = QtGui.QFont()
        font.setPointSize(36)
        font.setBold(True)
        font.setWeight(75)
        self.currency_lbl_2.setFont(font)
        self.currency_lbl_2.setObjectName(_fromUtf8("currency_lbl_2"))
        self.fiat_amount = QtGui.QLabel(self.screen3)
        self.fiat_amount.setGeometry(QtCore.QRect(50, 30, 361, 41))
        font = QtGui.QFont()
        font.setPointSize(30)
        self.fiat_amount.setFont(font)
        self.fiat_amount.setObjectName(_fromUtf8("fiat_amount"))
        self.btc_lbl = QtGui.QLabel(self.screen3)
        self.btc_lbl.setGeometry(QtCore.QRect(10, 60, 31, 61))
        font = QtGui.QFont()
        font.setPointSize(36)
        font.setBold(True)
        font.setWeight(75)
        self.btc_lbl.setFont(font)
        self.btc_lbl.setObjectName(_fromUtf8("btc_lbl"))
        self.btc_amount = QtGui.QLabel(self.screen3)
        self.btc_amount.setGeometry(QtCore.QRect(50, 70, 371, 41))
        font = QtGui.QFont()
        font.setPointSize(30)
        self.btc_amount.setFont(font)
        self.btc_amount.setObjectName(_fromUtf8("btc_amount"))
        self.exchange_rate_lbl = QtGui.QLabel(self.screen3)
        self.exchange_rate_lbl.setGeometry(QtCore.QRect(10, 120, 111, 41))
        self.exchange_rate_lbl.setObjectName(_fromUtf8("exchange_rate_lbl"))
        self.exchange_rate = QtGui.QLabel(self.screen3)
        self.exchange_rate.setGeometry(QtCore.QRect(130, 130, 161, 21))
        self.exchange_rate.setObjectName(_fromUtf8("exchange_rate"))
        self.stackedWidget.addWidget(self.screen3)

        self.screen4 = QtGui.QWidget()
        self.screen4.setObjectName(_fromUtf8("screen4"))
        self.qr_image = QtGui.QLabel(self.screen4)
        self.qr_image.setGeometry(QtCore.QRect(120, 60, 211, 181))
        self.qr_image.setText(_fromUtf8(""))
        self.qr_image.setScaledContents(True)
        self.qr_image.setObjectName(_fromUtf8("qr_image"))
        self.qr_title_lbl = QtGui.QLabel(self.screen4)
        self.qr_title_lbl.setGeometry(QtCore.QRect(100, 10, 301, 20))
        self.qr_title_lbl.setObjectName(_fromUtf8("qr_title_lbl"))
        self.qr_address_lbl = QtGui.QLabel(self.screen4)
        self.qr_address_lbl.setGeometry(QtCore.QRect(10, 30, 451, 20))
        self.qr_address_lbl.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.qr_address_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.qr_address_lbl.setObjectName(_fromUtf8("qr_address_lbl"))
        self.stackedWidget.addWidget(self.screen4)

        self.screen5 = QtGui.QWidget()
        self.screen5.setObjectName(_fromUtf8("screen5"))
        self.idle_lbl_2 = QtGui.QLabel(self.screen5)
        self.idle_lbl_2.setGeometry(QtCore.QRect(100, 40, 271, 191))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("DejaVu Sans"))
        font.setPointSize(30)
        self.idle_lbl_2.setFont(font)
        self.idle_lbl_2.setWordWrap(True)
        self.idle_lbl_2.setObjectName(_fromUtf8("idle_lbl_2"))
        self.stackedWidget.addWidget(self.screen5)

        self.screen6 = QtGui.QWidget()
        self.screen6.setObjectName(_fromUtf8("screen6"))
        self.idle_lbl_3 = QtGui.QLabel(self.screen6)
        self.idle_lbl_3.setGeometry(QtCore.QRect(100, 40, 271, 191))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("DejaVu Sans"))
        font.setPointSize(30)
        self.idle_lbl_3.setFont(font)
        self.idle_lbl_3.setWordWrap(True)
        self.idle_lbl_3.setObjectName(_fromUtf8("idle_lbl_3"))
        self.stackedWidget.addWidget(self.screen6)

        self.screen7 = QtGui.QWidget()
        self.screen7.setObjectName(_fromUtf8("screen7"))
        self.wifi_lbl = QtGui.QLabel(self.screen7)
        self.wifi_lbl.setGeometry(QtCore.QRect(30, 20, 151, 21))
        self.wifi_lbl.setObjectName(_fromUtf8("wifi_lbl"))
        self.listWidget = QtGui.QListWidget(self.screen7)
        self.listWidget.setGeometry(QtCore.QRect(30, 50, 421, 191))
        self.listWidget.setObjectName(_fromUtf8("listWidget"))
        self.stackedWidget.addWidget(self.screen7)

        self.screen8 = QtGui.QWidget()
        self.screen8.setObjectName(_fromUtf8("screen8"))
        self.ssid_lbl = QtGui.QLabel(self.screen8)
        self.ssid_lbl.setGeometry(QtCore.QRect(20, 50, 41, 31))
        self.ssid_lbl.setObjectName(_fromUtf8("ssid_lbl"))
        self.ssid_entered_lbl = QtGui.QLabel(self.screen8)
        self.ssid_entered_lbl.setGeometry(QtCore.QRect(130, 50, 271, 31))
        self.ssid_entered_lbl.setText(_fromUtf8(""))
        self.ssid_entered_lbl.setObjectName(_fromUtf8("ssid_entered_lbl"))
        self.password_enter = QtGui.QLineEdit(self.screen8)
        self.password_enter.setGeometry(QtCore.QRect(130, 96, 271, 31))
        self.password_enter.setObjectName(_fromUtf8("password_enter"))
        self.password_lbl = QtGui.QLabel(self.screen8)
        self.password_lbl.setGeometry(QtCore.QRect(20, 100, 81, 21))
        self.password_lbl.setObjectName(_fromUtf8("password_lbl"))
        self.label = QtGui.QLabel(self.screen8)
        self.label.setGeometry(QtCore.QRect(30, 160, 421, 61))
        self.label.setObjectName(_fromUtf8("label"))
        self.stackedWidget.addWidget(self.screen8)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.label_2.setText(_translate("Form", "Loading Please Wait", None))
        self.idle_lbl.setText(_translate("Form", "<html><head/><body><p align=\"center\">Please press</p><p align=\"center\"><span style=\" font-weight:600;\">ENTER</span></p><p align=\"center\">to begin</p></body></html>", None))
        self.amount_lbl.setText(_translate("Form", "Enter Amount", None))
        self.continue_lbl.setText(_translate("Form", "press enter to continue", None))
        self.currency_lbl.setText(_translate("Form", "£", None))
        self.currency_lbl_2.setText(_translate("Form", "£", None))
        self.fiat_amount.setText(_translate("Form", "0", None))
        self.btc_lbl.setText(_translate("Form", "฿", None))
        self.btc_amount.setText(_translate("Form", "0", None))
        self.exchange_rate_lbl.setText(_translate("Form", "exchange rate", None))
        self.exchange_rate.setText(_translate("Form", "0", None))
        self.qr_title_lbl.setText(_translate("Form", "Scan QR Code to complete payment", None))
        self.qr_address_lbl.setText(_translate("Form", ".", None))
        self.idle_lbl_2.setText(_translate("Form", "<html><head/><body><p align=\"center\">Payment</p><p align=\"center\">Successful</p></body></html>", None))
        self.idle_lbl_3.setText(_translate("Form", "<html><head/><body><p align=\"center\">Payment</p><p align=\"center\">Failed</p></body></html>", None))
        self.wifi_lbl.setText(_translate("Form", "Wi-Fi", None))
        self.ssid_lbl.setText(_translate("Form", "SSID", None))
        self.password_lbl.setText(_translate("Form", "Password", None))
        self.label.setText(_translate("Form", "<html><head/><body><p align=\"center\">2 a b c A B C</p></body></html>", None))


def formatCharSelectHelperHMTL(char_tupl, char_selected = None):
    char_list = []

    for index, char in enumerate(char_tupl):
        if char_selected == char:
            char_list.append("<strong><font color=\"#333333\" size=\"5\">{char_selected}</font></strong>".format(char_selected=char))
        else:
            char_list.append(str(char))

    char_string = ' '.join(char_list)

    return "<html><head/><body><p align=\"center\"><font color=\"#666666\">{char_string}</font></p></body></html>".format(char_string=char_string)
        