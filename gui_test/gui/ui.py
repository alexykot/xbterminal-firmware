# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/root/XBTerminal/xbterminal/gui/ui.ui'
#
# Created: Thu Jan  9 23:44:28 2014
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(480, 272)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(229, 229, 229))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(230, 230, 230))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(229, 229, 229))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(230, 230, 230))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(230, 230, 230))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(230, 230, 230))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        Form.setPalette(palette)
        Form.setCursor(QtGui.QCursor(QtCore.Qt.BlankCursor))
        self.stackedWidget = QtGui.QStackedWidget(Form)
        self.stackedWidget.setGeometry(QtCore.QRect(0, 40, 480, 231))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(60, 60, 60))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(60, 60, 60))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(106, 104, 100))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(230, 230, 230))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        self.stackedWidget.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("DejaVu Sans"))
        self.stackedWidget.setFont(font)
        self.stackedWidget.setCursor(QtGui.QCursor(QtCore.Qt.BlankCursor))
        self.stackedWidget.setObjectName(_fromUtf8("stackedWidget"))
        self.loading_screen = QtGui.QWidget()
        self.loading_screen.setObjectName(_fromUtf8("loading_screen"))
        self.progressBar = QtGui.QProgressBar(self.loading_screen)
        self.progressBar.setGeometry(QtCore.QRect(110, 90, 281, 23))
        self.progressBar.setMaximum(100)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.label_2 = QtGui.QLabel(self.loading_screen)
        self.label_2.setGeometry(QtCore.QRect(150, 120, 161, 16))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(12)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.stackedWidget.addWidget(self.loading_screen)
        self.nfc_screen = QtGui.QWidget()
        self.nfc_screen.setObjectName(_fromUtf8("nfc_screen"))
        self.advice_lbl_2 = QtGui.QLabel(self.nfc_screen)
        self.advice_lbl_2.setGeometry(QtCore.QRect(210, 0, 261, 201))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(26)
        font.setBold(True)
        font.setWeight(75)
        self.advice_lbl_2.setFont(font)
        self.advice_lbl_2.setAlignment(QtCore.Qt.AlignCenter)
        self.advice_lbl_2.setObjectName(_fromUtf8("advice_lbl_2"))
        self.show_qrButton = QtGui.QPushButton(self.nfc_screen)
        self.show_qrButton.setGeometry(QtCore.QRect(20, 150, 151, 61))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(14)
        self.show_qrButton.setFont(font)
        self.show_qrButton.setObjectName(_fromUtf8("show_qrButton"))
        self.currency_lbl_3 = QtGui.QLabel(self.nfc_screen)
        self.currency_lbl_3.setGeometry(QtCore.QRect(40, 40, 16, 16))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(16)
        font.setBold(False)
        font.setWeight(50)
        self.currency_lbl_3.setFont(font)
        self.currency_lbl_3.setObjectName(_fromUtf8("currency_lbl_3"))
        self.fiat_amount_2 = QtGui.QLabel(self.nfc_screen)
        self.fiat_amount_2.setGeometry(QtCore.QRect(40, 40, 101, 16))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(14)
        self.fiat_amount_2.setFont(font)
        self.fiat_amount_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.fiat_amount_2.setObjectName(_fromUtf8("fiat_amount_2"))
        self.btc_amount_2 = QtGui.QLabel(self.nfc_screen)
        self.btc_amount_2.setGeometry(QtCore.QRect(40, 70, 101, 16))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(14)
        self.btc_amount_2.setFont(font)
        self.btc_amount_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.btc_amount_2.setObjectName(_fromUtf8("btc_amount_2"))
        self.btc_lbl_2 = QtGui.QLabel(self.nfc_screen)
        self.btc_lbl_2.setGeometry(QtCore.QRect(25, 70, 81, 16))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.btc_lbl_2.setFont(font)
        self.btc_lbl_2.setObjectName(_fromUtf8("btc_lbl_2"))
        self.exchange_rate_3 = QtGui.QLabel(self.nfc_screen)
        self.exchange_rate_3.setGeometry(QtCore.QRect(60, 100, 91, 16))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(14)
        self.exchange_rate_3.setFont(font)
        self.exchange_rate_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.exchange_rate_3.setObjectName(_fromUtf8("exchange_rate_3"))
        self.exchange_rate_lbl_2 = QtGui.QLabel(self.nfc_screen)
        self.exchange_rate_lbl_2.setGeometry(QtCore.QRect(15, 100, 51, 16))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(14)
        self.exchange_rate_lbl_2.setFont(font)
        self.exchange_rate_lbl_2.setObjectName(_fromUtf8("exchange_rate_lbl_2"))
        self.stackedWidget.addWidget(self.nfc_screen)
        self.enter_scn = QtGui.QWidget()
        self.enter_scn.setObjectName(_fromUtf8("enter_scn"))
        self.idle_lbl = QtGui.QLabel(self.enter_scn)
        self.idle_lbl.setGeometry(QtCore.QRect(60, 0, 361, 211))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(60, 60, 60))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(60, 60, 60))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(106, 104, 100))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.idle_lbl.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(32)
        self.idle_lbl.setFont(font)
        self.idle_lbl.setWordWrap(True)
        self.idle_lbl.setObjectName(_fromUtf8("idle_lbl"))
        self.stackedWidget.addWidget(self.enter_scn)
        self.amount_scn = QtGui.QWidget()
        self.amount_scn.setObjectName(_fromUtf8("amount_scn"))
        self.amount_lbl = QtGui.QLabel(self.amount_scn)
        self.amount_lbl.setGeometry(QtCore.QRect(100, 20, 331, 51))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(60, 60, 60))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(60, 60, 60))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(106, 104, 100))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.amount_lbl.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(20)
        self.amount_lbl.setFont(font)
        self.amount_lbl.setObjectName(_fromUtf8("amount_lbl"))
        self.amount_text = QtGui.QLineEdit(self.amount_scn)
        self.amount_text.setGeometry(QtCore.QRect(100, 70, 321, 51))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(26)
        self.amount_text.setFont(font)
        self.amount_text.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.amount_text.setObjectName(_fromUtf8("amount_text"))
        self.currency_lbl = QtGui.QLabel(self.amount_scn)
        self.currency_lbl.setGeometry(QtCore.QRect(40, 80, 41, 41))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(60, 60, 60))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(60, 60, 60))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(106, 104, 100))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.currency_lbl.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(36)
        font.setBold(False)
        font.setWeight(50)
        self.currency_lbl.setFont(font)
        self.currency_lbl.setCursor(QtGui.QCursor(QtCore.Qt.BlankCursor))
        self.currency_lbl.setObjectName(_fromUtf8("currency_lbl"))
        self.stackedWidget.addWidget(self.amount_scn)
        self.rate_scn = QtGui.QWidget()
        self.rate_scn.setObjectName(_fromUtf8("rate_scn"))
        self.currency_lbl_2 = QtGui.QLabel(self.rate_scn)
        self.currency_lbl_2.setGeometry(QtCore.QRect(120, 20, 31, 61))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(36)
        font.setBold(False)
        font.setWeight(50)
        self.currency_lbl_2.setFont(font)
        self.currency_lbl_2.setObjectName(_fromUtf8("currency_lbl_2"))
        self.fiat_amount = QtGui.QLabel(self.rate_scn)
        self.fiat_amount.setGeometry(QtCore.QRect(170, 30, 181, 41))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(36)
        self.fiat_amount.setFont(font)
        self.fiat_amount.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.fiat_amount.setObjectName(_fromUtf8("fiat_amount"))
        self.btc_lbl = QtGui.QLabel(self.rate_scn)
        self.btc_lbl.setGeometry(QtCore.QRect(75, 70, 81, 61))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(36)
        font.setBold(False)
        font.setWeight(50)
        self.btc_lbl.setFont(font)
        self.btc_lbl.setObjectName(_fromUtf8("btc_lbl"))
        self.btc_amount = QtGui.QLabel(self.rate_scn)
        self.btc_amount.setGeometry(QtCore.QRect(130, 80, 221, 41))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(36)
        self.btc_amount.setFont(font)
        self.btc_amount.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.btc_amount.setObjectName(_fromUtf8("btc_amount"))
        self.exchange_rate_lbl = QtGui.QLabel(self.rate_scn)
        self.exchange_rate_lbl.setGeometry(QtCore.QRect(20, 130, 151, 41))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(14)
        self.exchange_rate_lbl.setFont(font)
        self.exchange_rate_lbl.setObjectName(_fromUtf8("exchange_rate_lbl"))
        self.advice_lbl = QtGui.QLabel(self.rate_scn)
        self.advice_lbl.setGeometry(QtCore.QRect(80, 180, 321, 41))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(12)
        self.advice_lbl.setFont(font)
        self.advice_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.advice_lbl.setObjectName(_fromUtf8("advice_lbl"))
        self.exchange_rate_2 = QtGui.QLabel(self.rate_scn)
        self.exchange_rate_2.setGeometry(QtCore.QRect(280, 140, 161, 21))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(14)
        self.exchange_rate_2.setFont(font)
        self.exchange_rate_2.setObjectName(_fromUtf8("exchange_rate_2"))
        self.stackedWidget.addWidget(self.rate_scn)
        self.qr_scn = QtGui.QWidget()
        self.qr_scn.setObjectName(_fromUtf8("qr_scn"))
        self.qr_image = QtGui.QLabel(self.qr_scn)
        self.qr_image.setGeometry(QtCore.QRect(240, 10, 201, 171))
        self.qr_image.setText(_fromUtf8(""))
        self.qr_image.setScaledContents(True)
        self.qr_image.setObjectName(_fromUtf8("qr_image"))
        self.qr_address_lbl = QtGui.QLabel(self.qr_scn)
        self.qr_address_lbl.setGeometry(QtCore.QRect(190, 190, 291, 31))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(10)
        self.qr_address_lbl.setFont(font)
        self.qr_address_lbl.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.qr_address_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.qr_address_lbl.setObjectName(_fromUtf8("qr_address_lbl"))
        self.exchange_rate_4 = QtGui.QLabel(self.qr_scn)
        self.exchange_rate_4.setGeometry(QtCore.QRect(60, 100, 91, 16))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(14)
        self.exchange_rate_4.setFont(font)
        self.exchange_rate_4.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.exchange_rate_4.setObjectName(_fromUtf8("exchange_rate_4"))
        self.btc_amount_3 = QtGui.QLabel(self.qr_scn)
        self.btc_amount_3.setGeometry(QtCore.QRect(40, 70, 101, 16))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(14)
        self.btc_amount_3.setFont(font)
        self.btc_amount_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.btc_amount_3.setObjectName(_fromUtf8("btc_amount_3"))
        self.btc_lbl_3 = QtGui.QLabel(self.qr_scn)
        self.btc_lbl_3.setGeometry(QtCore.QRect(25, 70, 81, 16))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.btc_lbl_3.setFont(font)
        self.btc_lbl_3.setObjectName(_fromUtf8("btc_lbl_3"))
        self.exchange_rate_lbl_3 = QtGui.QLabel(self.qr_scn)
        self.exchange_rate_lbl_3.setGeometry(QtCore.QRect(15, 100, 51, 16))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(14)
        self.exchange_rate_lbl_3.setFont(font)
        self.exchange_rate_lbl_3.setObjectName(_fromUtf8("exchange_rate_lbl_3"))
        self.fiat_amount_3 = QtGui.QLabel(self.qr_scn)
        self.fiat_amount_3.setGeometry(QtCore.QRect(40, 40, 101, 16))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(14)
        self.fiat_amount_3.setFont(font)
        self.fiat_amount_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.fiat_amount_3.setObjectName(_fromUtf8("fiat_amount_3"))
        self.currency_lbl_4 = QtGui.QLabel(self.qr_scn)
        self.currency_lbl_4.setGeometry(QtCore.QRect(40, 40, 16, 16))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(16)
        font.setBold(False)
        font.setWeight(50)
        self.currency_lbl_4.setFont(font)
        self.currency_lbl_4.setObjectName(_fromUtf8("currency_lbl_4"))
        self.show_qrButton_2 = QtGui.QPushButton(self.qr_scn)
        self.show_qrButton_2.setGeometry(QtCore.QRect(20, 150, 151, 61))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(14)
        self.show_qrButton_2.setFont(font)
        self.show_qrButton_2.setObjectName(_fromUtf8("show_qrButton_2"))
        self.stackedWidget.addWidget(self.qr_scn)
        self.success_scn = QtGui.QWidget()
        self.success_scn.setObjectName(_fromUtf8("success_scn"))
        self.idle_lbl_2 = QtGui.QLabel(self.success_scn)
        self.idle_lbl_2.setGeometry(QtCore.QRect(100, 10, 271, 191))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(36)
        self.idle_lbl_2.setFont(font)
        self.idle_lbl_2.setWordWrap(True)
        self.idle_lbl_2.setObjectName(_fromUtf8("idle_lbl_2"))
        self.stackedWidget.addWidget(self.success_scn)
        self.failed_scn = QtGui.QWidget()
        self.failed_scn.setObjectName(_fromUtf8("failed_scn"))
        self.idle_lbl_3 = QtGui.QLabel(self.failed_scn)
        self.idle_lbl_3.setGeometry(QtCore.QRect(100, 10, 271, 191))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(36)
        self.idle_lbl_3.setFont(font)
        self.idle_lbl_3.setWordWrap(True)
        self.idle_lbl_3.setObjectName(_fromUtf8("idle_lbl_3"))
        self.stackedWidget.addWidget(self.failed_scn)
        self.wifi_list_scn = QtGui.QWidget()
        self.wifi_list_scn.setObjectName(_fromUtf8("wifi_list_scn"))
        self.wifi_lbl = QtGui.QLabel(self.wifi_list_scn)
        self.wifi_lbl.setGeometry(QtCore.QRect(30, 10, 251, 21))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(59, 59, 59))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(106, 104, 100))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.wifi_lbl.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(14)
        self.wifi_lbl.setFont(font)
        self.wifi_lbl.setObjectName(_fromUtf8("wifi_lbl"))
        self.listWidget = QtGui.QListWidget(self.wifi_list_scn)
        self.listWidget.setGeometry(QtCore.QRect(30, 40, 421, 151))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.listWidget.setFont(font)
        self.listWidget.setObjectName(_fromUtf8("listWidget"))
        self.stackedWidget.addWidget(self.wifi_list_scn)
        self.wifi_pass_scn = QtGui.QWidget()
        self.wifi_pass_scn.setObjectName(_fromUtf8("wifi_pass_scn"))
        self.ssid_lbl = QtGui.QLabel(self.wifi_pass_scn)
        self.ssid_lbl.setGeometry(QtCore.QRect(30, 10, 101, 21))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(60, 60, 60))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(60, 60, 60))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(106, 104, 100))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.ssid_lbl.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(12)
        self.ssid_lbl.setFont(font)
        self.ssid_lbl.setObjectName(_fromUtf8("ssid_lbl"))
        self.ssid_entered_lbl = QtGui.QLabel(self.wifi_pass_scn)
        self.ssid_entered_lbl.setGeometry(QtCore.QRect(140, 10, 281, 21))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(60, 60, 60))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(60, 60, 60))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(106, 104, 100))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.ssid_entered_lbl.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(14)
        self.ssid_entered_lbl.setFont(font)
        self.ssid_entered_lbl.setObjectName(_fromUtf8("ssid_entered_lbl"))
        self.password_enter = QtGui.QLineEdit(self.wifi_pass_scn)
        self.password_enter.setGeometry(QtCore.QRect(140, 46, 271, 31))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(12)
        self.password_enter.setFont(font)
        self.password_enter.setObjectName(_fromUtf8("password_enter"))
        self.password_lbl = QtGui.QLabel(self.wifi_pass_scn)
        self.password_lbl.setGeometry(QtCore.QRect(51, 50, 91, 21))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(60, 60, 60))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(60, 60, 60))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(106, 104, 100))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.password_lbl.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(12)
        self.password_lbl.setFont(font)
        self.password_lbl.setObjectName(_fromUtf8("password_lbl"))
        self.label = QtGui.QLabel(self.wifi_pass_scn)
        self.label.setGeometry(QtCore.QRect(100, 80, 321, 31))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(60, 60, 60))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(60, 60, 60))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(106, 104, 100))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.label.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(16)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.stackedWidget.addWidget(self.wifi_pass_scn)
        self.wait_scn = QtGui.QWidget()
        self.wait_scn.setObjectName(_fromUtf8("wait_scn"))
        self.wait_lbl = QtGui.QLabel(self.wait_scn)
        self.wait_lbl.setGeometry(QtCore.QRect(140, 120, 181, 16))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(12)
        self.wait_lbl.setFont(font)
        self.wait_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.wait_lbl.setObjectName(_fromUtf8("wait_lbl"))
        self.progressBar_2 = QtGui.QProgressBar(self.wait_scn)
        self.progressBar_2.setGeometry(QtCore.QRect(110, 90, 281, 23))
        self.progressBar_2.setMaximum(0)
        self.progressBar_2.setProperty("value", -1)
        self.progressBar_2.setObjectName(_fromUtf8("progressBar_2"))
        self.stackedWidget.addWidget(self.wait_scn)
        self.logo = QtGui.QLabel(Form)
        self.logo.setGeometry(QtCore.QRect(0, 0, 241, 41))
        self.logo.setText(_fromUtf8(""))
        self.logo.setPixmap(QtGui.QPixmap(_fromUtf8("D:/Personal/Google Drive/Work/XBTerminal/designs/logo_device1.png")))
        self.logo.setObjectName(_fromUtf8("logo"))

        self.retranslateUi(Form)
        self.stackedWidget.setCurrentIndex(5)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Form", "please wait", None, QtGui.QApplication.UnicodeUTF8))
        self.advice_lbl_2.setText(QtGui.QApplication.translate("Form", "TOUCH NFC\n"
"\n"
" NOW", None, QtGui.QApplication.UnicodeUTF8))
        self.show_qrButton.setText(QtGui.QApplication.translate("Form", "show QR code", None, QtGui.QApplication.UnicodeUTF8))
        self.currency_lbl_3.setText(QtGui.QApplication.translate("Form", "£", None, QtGui.QApplication.UnicodeUTF8))
        self.fiat_amount_2.setText(QtGui.QApplication.translate("Form", "10.00", None, QtGui.QApplication.UnicodeUTF8))
        self.btc_amount_2.setText(QtGui.QApplication.translate("Form", "12.05", None, QtGui.QApplication.UnicodeUTF8))
        self.btc_lbl_2.setText(QtGui.QApplication.translate("Form", "m฿", None, QtGui.QApplication.UnicodeUTF8))
        self.exchange_rate_3.setText(QtGui.QApplication.translate("Form", "0.845", None, QtGui.QApplication.UnicodeUTF8))
        self.exchange_rate_lbl_2.setText(QtGui.QApplication.translate("Form", "rate", None, QtGui.QApplication.UnicodeUTF8))
        self.idle_lbl.setText(QtGui.QApplication.translate("Form", "<html><head/><body><p align=\"center\">press</p><p align=\"center\"><span style=\" font-weight:600;\">any key</span></p><p align=\"center\">to begin</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.amount_lbl.setText(QtGui.QApplication.translate("Form", "amount", None, QtGui.QApplication.UnicodeUTF8))
        self.currency_lbl.setText(QtGui.QApplication.translate("Form", "£", None, QtGui.QApplication.UnicodeUTF8))
        self.currency_lbl_2.setText(QtGui.QApplication.translate("Form", "£", None, QtGui.QApplication.UnicodeUTF8))
        self.fiat_amount.setText(QtGui.QApplication.translate("Form", "10.00", None, QtGui.QApplication.UnicodeUTF8))
        self.btc_lbl.setText(QtGui.QApplication.translate("Form", "m฿", None, QtGui.QApplication.UnicodeUTF8))
        self.btc_amount.setText(QtGui.QApplication.translate("Form", "12.05", None, QtGui.QApplication.UnicodeUTF8))
        self.exchange_rate_lbl.setText(QtGui.QApplication.translate("Form", "exchange rate", None, QtGui.QApplication.UnicodeUTF8))
        self.advice_lbl.setText(QtGui.QApplication.translate("Form", "press enter to accept payment", None, QtGui.QApplication.UnicodeUTF8))
        self.exchange_rate_2.setText(QtGui.QApplication.translate("Form", "0.845", None, QtGui.QApplication.UnicodeUTF8))
        self.qr_address_lbl.setText(QtGui.QApplication.translate("Form", "1FCrwY2CsLJgsmbogSunECwCa6WswBBrfz", None, QtGui.QApplication.UnicodeUTF8))
        self.exchange_rate_4.setText(QtGui.QApplication.translate("Form", "0.845", None, QtGui.QApplication.UnicodeUTF8))
        self.btc_amount_3.setText(QtGui.QApplication.translate("Form", "12.05", None, QtGui.QApplication.UnicodeUTF8))
        self.btc_lbl_3.setText(QtGui.QApplication.translate("Form", "m฿", None, QtGui.QApplication.UnicodeUTF8))
        self.exchange_rate_lbl_3.setText(QtGui.QApplication.translate("Form", "rate", None, QtGui.QApplication.UnicodeUTF8))
        self.fiat_amount_3.setText(QtGui.QApplication.translate("Form", "10.00", None, QtGui.QApplication.UnicodeUTF8))
        self.currency_lbl_4.setText(QtGui.QApplication.translate("Form", "£", None, QtGui.QApplication.UnicodeUTF8))
        self.show_qrButton_2.setText(QtGui.QApplication.translate("Form", "send NFC", None, QtGui.QApplication.UnicodeUTF8))
        self.idle_lbl_2.setText(QtGui.QApplication.translate("Form", "<html><head/><body><p align=\"center\">Payment</p><p align=\"center\">Successful</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.idle_lbl_3.setText(QtGui.QApplication.translate("Form", "<html><head/><body><p align=\"center\">Payment</p><p align=\"center\">Failed</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.wifi_lbl.setText(QtGui.QApplication.translate("Form", "available Wi-Fi networks", None, QtGui.QApplication.UnicodeUTF8))
        self.ssid_lbl.setText(QtGui.QApplication.translate("Form", "selected WiFi", None, QtGui.QApplication.UnicodeUTF8))
        self.ssid_entered_lbl.setText(QtGui.QApplication.translate("Form", "65A High Steet", None, QtGui.QApplication.UnicodeUTF8))
        self.password_enter.setText(QtGui.QApplication.translate("Form", "asasdad", None, QtGui.QApplication.UnicodeUTF8))
        self.password_lbl.setText(QtGui.QApplication.translate("Form", "password", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Form", "<html><head/><body><p align=\"center\">2 a b c A B C</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.wait_lbl.setText(QtGui.QApplication.translate("Form", "please wait", None, QtGui.QApplication.UnicodeUTF8))
