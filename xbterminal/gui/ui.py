# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/root/XBTerminal/xbterminal/gui/ui.ui'
#
# Created: Mon Jan 13 23:01:50 2014
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
        self.load_percent_scrn = QtGui.QWidget()
        self.load_percent_scrn.setObjectName(_fromUtf8("load_percent_scrn"))
        self.progressBar_percent = QtGui.QProgressBar(self.load_percent_scrn)
        self.progressBar_percent.setGeometry(QtCore.QRect(110, 90, 281, 23))
        self.progressBar_percent.setMaximum(100)
        self.progressBar_percent.setProperty("value", 0)
        self.progressBar_percent.setObjectName(_fromUtf8("progressBar_percent"))
        self.percent_load_lbl = QtGui.QLabel(self.load_percent_scrn)
        self.percent_load_lbl.setGeometry(QtCore.QRect(150, 120, 161, 16))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(12)
        self.percent_load_lbl.setFont(font)
        self.percent_load_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.percent_load_lbl.setObjectName(_fromUtf8("percent_load_lbl"))
        self.stackedWidget.addWidget(self.load_percent_scrn)
        self.pay_nfc_scrn = QtGui.QWidget()
        self.pay_nfc_scrn.setObjectName(_fromUtf8("pay_nfc_scrn"))
        self.nfc_advice_lbl = QtGui.QLabel(self.pay_nfc_scrn)
        self.nfc_advice_lbl.setGeometry(QtCore.QRect(210, 0, 261, 201))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(26)
        font.setBold(True)
        font.setWeight(75)
        self.nfc_advice_lbl.setFont(font)
        self.nfc_advice_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.nfc_advice_lbl.setObjectName(_fromUtf8("nfc_advice_lbl"))
        self.show_qrButton = QtGui.QPushButton(self.pay_nfc_scrn)
        self.show_qrButton.setGeometry(QtCore.QRect(20, 150, 151, 61))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(14)
        self.show_qrButton.setFont(font)
        self.show_qrButton.setObjectName(_fromUtf8("show_qrButton"))
        self.currency_lbl_nfc = QtGui.QLabel(self.pay_nfc_scrn)
        self.currency_lbl_nfc.setGeometry(QtCore.QRect(40, 40, 16, 16))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(16)
        font.setBold(False)
        font.setWeight(50)
        self.currency_lbl_nfc.setFont(font)
        self.currency_lbl_nfc.setObjectName(_fromUtf8("currency_lbl_nfc"))
        self.fiat_amount_nfc = QtGui.QLabel(self.pay_nfc_scrn)
        self.fiat_amount_nfc.setGeometry(QtCore.QRect(40, 40, 101, 16))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(14)
        self.fiat_amount_nfc.setFont(font)
        self.fiat_amount_nfc.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.fiat_amount_nfc.setObjectName(_fromUtf8("fiat_amount_nfc"))
        self.btc_amount_nfc = QtGui.QLabel(self.pay_nfc_scrn)
        self.btc_amount_nfc.setGeometry(QtCore.QRect(40, 70, 101, 16))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(14)
        self.btc_amount_nfc.setFont(font)
        self.btc_amount_nfc.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.btc_amount_nfc.setObjectName(_fromUtf8("btc_amount_nfc"))
        self.btc_lbl_nfc = QtGui.QLabel(self.pay_nfc_scrn)
        self.btc_lbl_nfc.setGeometry(QtCore.QRect(25, 70, 81, 16))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.btc_lbl_nfc.setFont(font)
        self.btc_lbl_nfc.setObjectName(_fromUtf8("btc_lbl_nfc"))
        self.exchange_rate_nfc = QtGui.QLabel(self.pay_nfc_scrn)
        self.exchange_rate_nfc.setGeometry(QtCore.QRect(60, 100, 91, 16))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(14)
        self.exchange_rate_nfc.setFont(font)
        self.exchange_rate_nfc.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.exchange_rate_nfc.setObjectName(_fromUtf8("exchange_rate_nfc"))
        self.exchange_rate_lbl_nfc = QtGui.QLabel(self.pay_nfc_scrn)
        self.exchange_rate_lbl_nfc.setGeometry(QtCore.QRect(15, 100, 51, 16))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(14)
        self.exchange_rate_lbl_nfc.setFont(font)
        self.exchange_rate_lbl_nfc.setObjectName(_fromUtf8("exchange_rate_lbl_nfc"))
        self.stackedWidget.addWidget(self.pay_nfc_scrn)
        self.idle_scrn = QtGui.QWidget()
        self.idle_scrn.setObjectName(_fromUtf8("idle_scrn"))
        self.idle_lbl = QtGui.QLabel(self.idle_scrn)
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
        self.stackedWidget.addWidget(self.idle_scrn)
        self.enter_amount_scrn = QtGui.QWidget()
        self.enter_amount_scrn.setObjectName(_fromUtf8("enter_amount_scrn"))
        self.amount_lbl = QtGui.QLabel(self.enter_amount_scrn)
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
        self.amount_input = QtGui.QLineEdit(self.enter_amount_scrn)
        self.amount_input.setGeometry(QtCore.QRect(100, 70, 321, 51))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(26)
        self.amount_input.setFont(font)
        self.amount_input.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.amount_input.setObjectName(_fromUtf8("amount_input"))
        self.currency_lbl = QtGui.QLabel(self.enter_amount_scrn)
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
        self.error_text_lbl = QtGui.QLabel(self.enter_amount_scrn)
        self.error_text_lbl.setGeometry(QtCore.QRect(100, 130, 321, 20))
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
        self.error_text_lbl.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(14)
        font.setItalic(True)
        self.error_text_lbl.setFont(font)
        self.error_text_lbl.setText(_fromUtf8(""))
        self.error_text_lbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.error_text_lbl.setObjectName(_fromUtf8("error_text_lbl"))
        self.stackedWidget.addWidget(self.enter_amount_scrn)
        self.pay_rates_scrn = QtGui.QWidget()
        self.pay_rates_scrn.setObjectName(_fromUtf8("pay_rates_scrn"))
        self.currency_lbl_rates = QtGui.QLabel(self.pay_rates_scrn)
        self.currency_lbl_rates.setGeometry(QtCore.QRect(120, 20, 31, 61))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(36)
        font.setBold(False)
        font.setWeight(50)
        self.currency_lbl_rates.setFont(font)
        self.currency_lbl_rates.setObjectName(_fromUtf8("currency_lbl_rates"))
        self.fiat_amount = QtGui.QLabel(self.pay_rates_scrn)
        self.fiat_amount.setGeometry(QtCore.QRect(170, 30, 181, 41))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(36)
        self.fiat_amount.setFont(font)
        self.fiat_amount.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.fiat_amount.setObjectName(_fromUtf8("fiat_amount"))
        self.btc_lbl = QtGui.QLabel(self.pay_rates_scrn)
        self.btc_lbl.setGeometry(QtCore.QRect(75, 70, 81, 61))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(36)
        font.setBold(False)
        font.setWeight(50)
        self.btc_lbl.setFont(font)
        self.btc_lbl.setObjectName(_fromUtf8("btc_lbl"))
        self.btc_amount = QtGui.QLabel(self.pay_rates_scrn)
        self.btc_amount.setGeometry(QtCore.QRect(130, 80, 221, 41))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(36)
        self.btc_amount.setFont(font)
        self.btc_amount.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.btc_amount.setObjectName(_fromUtf8("btc_amount"))
        self.exchange_rate_lbl = QtGui.QLabel(self.pay_rates_scrn)
        self.exchange_rate_lbl.setGeometry(QtCore.QRect(20, 130, 151, 41))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(14)
        self.exchange_rate_lbl.setFont(font)
        self.exchange_rate_lbl.setObjectName(_fromUtf8("exchange_rate_lbl"))
        self.advice_lbl = QtGui.QLabel(self.pay_rates_scrn)
        self.advice_lbl.setGeometry(QtCore.QRect(80, 180, 321, 41))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(12)
        self.advice_lbl.setFont(font)
        self.advice_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.advice_lbl.setObjectName(_fromUtf8("advice_lbl"))
        self.exchange_rate_amount = QtGui.QLabel(self.pay_rates_scrn)
        self.exchange_rate_amount.setGeometry(QtCore.QRect(280, 140, 161, 21))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(14)
        self.exchange_rate_amount.setFont(font)
        self.exchange_rate_amount.setObjectName(_fromUtf8("exchange_rate_amount"))
        self.stackedWidget.addWidget(self.pay_rates_scrn)
        self.pay_qr_scrn = QtGui.QWidget()
        self.pay_qr_scrn.setObjectName(_fromUtf8("pay_qr_scrn"))
        self.qr_image = QtGui.QLabel(self.pay_qr_scrn)
        self.qr_image.setGeometry(QtCore.QRect(240, 10, 201, 171))
        self.qr_image.setText(_fromUtf8(""))
        self.qr_image.setScaledContents(True)
        self.qr_image.setObjectName(_fromUtf8("qr_image"))
        self.qr_address_lbl = QtGui.QLabel(self.pay_qr_scrn)
        self.qr_address_lbl.setGeometry(QtCore.QRect(190, 190, 291, 31))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(10)
        self.qr_address_lbl.setFont(font)
        self.qr_address_lbl.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.qr_address_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.qr_address_lbl.setObjectName(_fromUtf8("qr_address_lbl"))
        self.exchange_rate_qr = QtGui.QLabel(self.pay_qr_scrn)
        self.exchange_rate_qr.setGeometry(QtCore.QRect(60, 100, 91, 16))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(14)
        self.exchange_rate_qr.setFont(font)
        self.exchange_rate_qr.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.exchange_rate_qr.setObjectName(_fromUtf8("exchange_rate_qr"))
        self.btc_amount_qr = QtGui.QLabel(self.pay_qr_scrn)
        self.btc_amount_qr.setGeometry(QtCore.QRect(40, 70, 101, 16))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(14)
        self.btc_amount_qr.setFont(font)
        self.btc_amount_qr.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.btc_amount_qr.setObjectName(_fromUtf8("btc_amount_qr"))
        self.btc_lbl_qr = QtGui.QLabel(self.pay_qr_scrn)
        self.btc_lbl_qr.setGeometry(QtCore.QRect(25, 70, 81, 16))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.btc_lbl_qr.setFont(font)
        self.btc_lbl_qr.setObjectName(_fromUtf8("btc_lbl_qr"))
        self.exchange_rate_lbl_qr = QtGui.QLabel(self.pay_qr_scrn)
        self.exchange_rate_lbl_qr.setGeometry(QtCore.QRect(15, 100, 51, 16))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(14)
        self.exchange_rate_lbl_qr.setFont(font)
        self.exchange_rate_lbl_qr.setObjectName(_fromUtf8("exchange_rate_lbl_qr"))
        self.fiat_amount_qr = QtGui.QLabel(self.pay_qr_scrn)
        self.fiat_amount_qr.setGeometry(QtCore.QRect(40, 40, 101, 16))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(14)
        self.fiat_amount_qr.setFont(font)
        self.fiat_amount_qr.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.fiat_amount_qr.setObjectName(_fromUtf8("fiat_amount_qr"))
        self.currency_lbl_qr = QtGui.QLabel(self.pay_qr_scrn)
        self.currency_lbl_qr.setGeometry(QtCore.QRect(40, 40, 16, 16))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(16)
        font.setBold(False)
        font.setWeight(50)
        self.currency_lbl_qr.setFont(font)
        self.currency_lbl_qr.setObjectName(_fromUtf8("currency_lbl_qr"))
        self.send_nfcButton = QtGui.QPushButton(self.pay_qr_scrn)
        self.send_nfcButton.setGeometry(QtCore.QRect(20, 150, 151, 61))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(14)
        self.send_nfcButton.setFont(font)
        self.send_nfcButton.setObjectName(_fromUtf8("send_nfcButton"))
        self.stackedWidget.addWidget(self.pay_qr_scrn)
        self.pay_success_scrn = QtGui.QWidget()
        self.pay_success_scrn.setObjectName(_fromUtf8("pay_success_scrn"))
        self.pay_success_lbl = QtGui.QLabel(self.pay_success_scrn)
        self.pay_success_lbl.setGeometry(QtCore.QRect(100, 10, 271, 191))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(36)
        self.pay_success_lbl.setFont(font)
        self.pay_success_lbl.setWordWrap(True)
        self.pay_success_lbl.setObjectName(_fromUtf8("pay_success_lbl"))
        self.stackedWidget.addWidget(self.pay_success_scrn)
        self.pay_cancel_scrn = QtGui.QWidget()
        self.pay_cancel_scrn.setObjectName(_fromUtf8("pay_cancel_scrn"))
        self.pay_cancel_lbl = QtGui.QLabel(self.pay_cancel_scrn)
        self.pay_cancel_lbl.setGeometry(QtCore.QRect(100, 10, 271, 191))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(36)
        self.pay_cancel_lbl.setFont(font)
        self.pay_cancel_lbl.setWordWrap(True)
        self.pay_cancel_lbl.setObjectName(_fromUtf8("pay_cancel_lbl"))
        self.stackedWidget.addWidget(self.pay_cancel_scrn)
        self.choose_ssid_scrn = QtGui.QWidget()
        self.choose_ssid_scrn.setObjectName(_fromUtf8("choose_ssid_scrn"))
        self.wifi_lbl = QtGui.QLabel(self.choose_ssid_scrn)
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
        self.wifi_listWidget = QtGui.QListWidget(self.choose_ssid_scrn)
        self.wifi_listWidget.setGeometry(QtCore.QRect(30, 40, 421, 151))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.wifi_listWidget.setFont(font)
        self.wifi_listWidget.setObjectName(_fromUtf8("wifi_listWidget"))
        self.stackedWidget.addWidget(self.choose_ssid_scrn)
        self.enter_passkey_scrn = QtGui.QWidget()
        self.enter_passkey_scrn.setObjectName(_fromUtf8("enter_passkey_scrn"))
        self.ssid_lbl = QtGui.QLabel(self.enter_passkey_scrn)
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
        self.ssid_entered_lbl = QtGui.QLabel(self.enter_passkey_scrn)
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
        self.password_input = QtGui.QLineEdit(self.enter_passkey_scrn)
        self.password_input.setGeometry(QtCore.QRect(140, 46, 271, 31))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(12)
        self.password_input.setFont(font)
        self.password_input.setObjectName(_fromUtf8("password_input"))
        self.password_lbl = QtGui.QLabel(self.enter_passkey_scrn)
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
        self.input_hepl_lbl = QtGui.QLabel(self.enter_passkey_scrn)
        self.input_hepl_lbl.setGeometry(QtCore.QRect(100, 80, 321, 31))
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
        self.input_hepl_lbl.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(16)
        self.input_hepl_lbl.setFont(font)
        self.input_hepl_lbl.setObjectName(_fromUtf8("input_hepl_lbl"))
        self.stackedWidget.addWidget(self.enter_passkey_scrn)
        self.load_indefinite_scrn = QtGui.QWidget()
        self.load_indefinite_scrn.setObjectName(_fromUtf8("load_indefinite_scrn"))
        self.indefinite_load_lbl = QtGui.QLabel(self.load_indefinite_scrn)
        self.indefinite_load_lbl.setGeometry(QtCore.QRect(140, 120, 181, 16))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(12)
        self.indefinite_load_lbl.setFont(font)
        self.indefinite_load_lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.indefinite_load_lbl.setObjectName(_fromUtf8("indefinite_load_lbl"))
        self.progressBar_indefinite = QtGui.QProgressBar(self.load_indefinite_scrn)
        self.progressBar_indefinite.setGeometry(QtCore.QRect(110, 90, 281, 23))
        self.progressBar_indefinite.setMaximum(0)
        self.progressBar_indefinite.setProperty("value", -1)
        self.progressBar_indefinite.setObjectName(_fromUtf8("progressBar_indefinite"))
        self.stackedWidget.addWidget(self.load_indefinite_scrn)
        self.logo = QtGui.QLabel(Form)
        self.logo.setGeometry(QtCore.QRect(0, 0, 241, 41))
        self.logo.setText(_fromUtf8(""))
        self.logo.setPixmap(QtGui.QPixmap(_fromUtf8("D:/Personal/Google Drive/Work/XBTerminal/designs/logo_device1.png")))
        self.logo.setObjectName(_fromUtf8("logo"))

        self.retranslateUi(Form)
        self.stackedWidget.setCurrentIndex(10)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.percent_load_lbl.setText(QtGui.QApplication.translate("Form", "loading, please wait", None, QtGui.QApplication.UnicodeUTF8))
        self.nfc_advice_lbl.setText(QtGui.QApplication.translate("Form", "TOUCH NFC\n"
"\n"
" NOW", None, QtGui.QApplication.UnicodeUTF8))
        self.show_qrButton.setText(QtGui.QApplication.translate("Form", "show QR code", None, QtGui.QApplication.UnicodeUTF8))
        self.currency_lbl_nfc.setText(QtGui.QApplication.translate("Form", "£", None, QtGui.QApplication.UnicodeUTF8))
        self.fiat_amount_nfc.setText(QtGui.QApplication.translate("Form", "10.00", None, QtGui.QApplication.UnicodeUTF8))
        self.btc_amount_nfc.setText(QtGui.QApplication.translate("Form", "12.05", None, QtGui.QApplication.UnicodeUTF8))
        self.btc_lbl_nfc.setText(QtGui.QApplication.translate("Form", "m฿", None, QtGui.QApplication.UnicodeUTF8))
        self.exchange_rate_nfc.setText(QtGui.QApplication.translate("Form", "0.845", None, QtGui.QApplication.UnicodeUTF8))
        self.exchange_rate_lbl_nfc.setText(QtGui.QApplication.translate("Form", "rate", None, QtGui.QApplication.UnicodeUTF8))
        self.idle_lbl.setText(QtGui.QApplication.translate("Form", "<html><head/><body><p align=\"center\">press</p><p align=\"center\"><span style=\" font-weight:600;\">any key</span></p><p align=\"center\">to begin</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.amount_lbl.setText(QtGui.QApplication.translate("Form", "amount", None, QtGui.QApplication.UnicodeUTF8))
        self.currency_lbl.setText(QtGui.QApplication.translate("Form", "£", None, QtGui.QApplication.UnicodeUTF8))
        self.currency_lbl_rates.setText(QtGui.QApplication.translate("Form", "£", None, QtGui.QApplication.UnicodeUTF8))
        self.fiat_amount.setText(QtGui.QApplication.translate("Form", "10.00", None, QtGui.QApplication.UnicodeUTF8))
        self.btc_lbl.setText(QtGui.QApplication.translate("Form", "m฿", None, QtGui.QApplication.UnicodeUTF8))
        self.btc_amount.setText(QtGui.QApplication.translate("Form", "12.05", None, QtGui.QApplication.UnicodeUTF8))
        self.exchange_rate_lbl.setText(QtGui.QApplication.translate("Form", "exchange rate", None, QtGui.QApplication.UnicodeUTF8))
        self.advice_lbl.setText(QtGui.QApplication.translate("Form", "press enter to accept payment", None, QtGui.QApplication.UnicodeUTF8))
        self.exchange_rate_amount.setText(QtGui.QApplication.translate("Form", "0.845", None, QtGui.QApplication.UnicodeUTF8))
        self.qr_address_lbl.setText(QtGui.QApplication.translate("Form", "1FCrwY2CsLJgsmbogSunECwCa6WswBBrfz", None, QtGui.QApplication.UnicodeUTF8))
        self.exchange_rate_qr.setText(QtGui.QApplication.translate("Form", "0.845", None, QtGui.QApplication.UnicodeUTF8))
        self.btc_amount_qr.setText(QtGui.QApplication.translate("Form", "12.05", None, QtGui.QApplication.UnicodeUTF8))
        self.btc_lbl_qr.setText(QtGui.QApplication.translate("Form", "m฿", None, QtGui.QApplication.UnicodeUTF8))
        self.exchange_rate_lbl_qr.setText(QtGui.QApplication.translate("Form", "rate", None, QtGui.QApplication.UnicodeUTF8))
        self.fiat_amount_qr.setText(QtGui.QApplication.translate("Form", "10.00", None, QtGui.QApplication.UnicodeUTF8))
        self.currency_lbl_qr.setText(QtGui.QApplication.translate("Form", "£", None, QtGui.QApplication.UnicodeUTF8))
        self.send_nfcButton.setText(QtGui.QApplication.translate("Form", "send NFC", None, QtGui.QApplication.UnicodeUTF8))
        self.pay_success_lbl.setText(QtGui.QApplication.translate("Form", "<html><head/><body><p align=\"center\">Payment</p><p align=\"center\">Successful</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.pay_cancel_lbl.setText(QtGui.QApplication.translate("Form", "<html><head/><body><p align=\"center\">Payment</p><p align=\"center\">Cancelled</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.wifi_lbl.setText(QtGui.QApplication.translate("Form", "available Wi-Fi networks", None, QtGui.QApplication.UnicodeUTF8))
        self.ssid_lbl.setText(QtGui.QApplication.translate("Form", "selected WiFi", None, QtGui.QApplication.UnicodeUTF8))
        self.ssid_entered_lbl.setText(QtGui.QApplication.translate("Form", "65A High Steet", None, QtGui.QApplication.UnicodeUTF8))
        self.password_input.setText(QtGui.QApplication.translate("Form", "asasdad", None, QtGui.QApplication.UnicodeUTF8))
        self.password_lbl.setText(QtGui.QApplication.translate("Form", "password", None, QtGui.QApplication.UnicodeUTF8))
        self.input_hepl_lbl.setText(QtGui.QApplication.translate("Form", "<html><head/><body><p align=\"center\">2 a b c A B C</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.indefinite_load_lbl.setText(QtGui.QApplication.translate("Form", "loading, please wait", None, QtGui.QApplication.UnicodeUTF8))

