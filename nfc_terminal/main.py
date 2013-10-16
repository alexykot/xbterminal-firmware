# -*- coding: utf-8 -*-
from decimal import Decimal
import time
import sys
from PyQt4 import QtGui, QtCore

import nfc_terminal
from nfc_terminal import defaults
from nfc_terminal.gui import gui
from nfc_terminal import stages
from nfc_terminal.helpers.configs import load_config
from nfc_terminal.helpers.log import write_msg_log
try:
    from nfc_terminal.keypad import keypad
except ImportError:
    pass


def main():

    # Load configs
    nfc_terminal.helpers.configs.load_config()

    #init runtime data
    nfc_terminal.runtime = {}
    nfc_terminal.runtime['CURRENT_STAGE'] = defaults.STAGES[0]
    nfc_terminal.runtime['text_entered'] = defaults.OUTPUT_DEFAULT_VALUE
    nfc_terminal.runtime['amount_to_pay_fiat'] = None
    nfc_terminal.runtime['amount_to_pay_btc'] = None
    nfc_terminal.runtime['key_pressed'] = None
    nfc_terminal.runtime['current_text_piece'] = 'decimal'

    try:
        kp = keypad.keypad(columnCount=4)
    except NameError:
        pass

    write_msg_log("STAGE: Initialisation", 'DEBUG')

    nfc_terminal.gui.runtime = {}
    nfc_terminal.gui.runtime['app'], nfc_terminal.gui.runtime['main_win'] = gui.initGUI()
    ui = nfc_terminal.gui.runtime['main_win'].ui

    while True:
        # At beginning of each loop push events
        try:
            nfc_terminal.gui.runtime['app'].sendPostedEvents()
            nfc_terminal.gui.runtime['app'].processEvents()
        except NameError:
            pass

        nfc_terminal.runtime['key_pressed'] = None
        try:
            nfc_terminal.runtime['key_pressed'] = kp.getKey()
            if nfc_terminal.runtime['key_pressed'] is not None:
                write_msg_log("KEYPAD: Key pressed - {}".format(nfc_terminal.runtime['key_pressed']), 'DEBUG')
                time.sleep(0.2)
        except NameError:
            pass

        if nfc_terminal.runtime['CURRENT_STAGE'] == 'standby':

            if nfc_terminal.runtime['key_pressed'] == "D":
                ui.stackedWidget.setCurrentIndex(1)
                nfc_terminal.runtime['CURRENT_STAGE'] = 'enter_amount'
                ui.amount_text.setText(nfc_terminal.runtime['text_entered'])
                continue

        elif nfc_terminal.runtime['CURRENT_STAGE'] == 'enter_amount':

            if (isinstance(nfc_terminal.runtime['key_pressed'], (int, long))
                or nfc_terminal.runtime['key_pressed'] == "."
                or nfc_terminal.runtime['key_pressed'] == "A"
                or nfc_terminal.runtime['key_pressed'] == "B"):

                ui.amount_text.setStyleSheet('background: #FFF')

                nfc_terminal.runtime['text_entered'] = stages.processAmountKeyInput(nfc_terminal.runtime['text_entered'], nfc_terminal.runtime['key_pressed'])
                ui.amount_text.setText(nfc_terminal.runtime['text_entered'])
            elif nfc_terminal.runtime['key_pressed'] is "D":
                nfc_terminal.runtime['amount_to_pay_fiat'] = stages.amountInputToDecimal(nfc_terminal.runtime['text_entered'])
                if nfc_terminal.runtime['amount_to_pay_fiat'] > 0:
                    ui.stackedWidget.setCurrentIndex(2)
                    nfc_terminal.runtime['CURRENT_STAGE'] = 'pay_nfc'
                else:
                    ui.amount_text.setStyleSheet('background: #B33A3A')
                    ui.continue_lbl.setText("error: no amount entered")
                    pass
                continue

        elif nfc_terminal.runtime['CURRENT_STAGE'] == 'pay_nfc' or nfc_terminal.runtime['CURRENT_STAGE'] == 'pay_qr':
            if nfc_terminal.runtime['amount_to_pay_fiat'] is None:
                ui.stackedWidget.setCurrentIndex(1)
                nfc_terminal.runtime['CURRENT_STAGE'] = 'enter_amount'
                continue

            if nfc_terminal.runtime['amount_to_pay_btc'] is None:
                our_fee_btc_amount, instantfiat_btc_amount, merchants_btc_fiat_amount = stages.getBtcSharesAmounts(nfc_terminal.runtime['amount_to_pay_fiat'])

                nfc_terminal.runtime['amount_to_pay_btc'] = our_fee_btc_amount + instantfiat_btc_amount + merchants_btc_fiat_amount
                nfc_terminal.runtime['rate_btc'] = nfc_terminal.runtime['amount_to_pay_fiat'] / nfc_terminal.runtime['amount_to_pay_btc']

                nfc_terminal.runtime['transaction_address'] = stages.getTransactionAddress(nfc_terminal.runtime['amount_to_pay_btc'])

                ui.fiat_amount.setText(stages.amountDecimalToOutput(nfc_terminal.runtime['amount_to_pay_fiat']))
                ui.btc_amount.setText(str(nfc_terminal.runtime['amount_to_pay_btc']))
                ui.exchange_rate.setText(stages.amountDecimalToOutput(nfc_terminal.runtime['rate_btc']))

            if nfc_terminal.runtime['key_pressed'] == "A":

                nfc_terminal.runtime['amount_to_pay_btc'] = None
                nfc_terminal.runtime['rate_btc'] = None
                nfc_terminal.runtime['transaction_address'] = None
                nfc_terminal.runtime['CURRENT_STAGE'] = 'enter_amount'
                nfc_terminal.runtime['text_entered'] = ""

                ui.amount_text.setText("0.00")
                ui.fiat_amount.setText("0")
                ui.btc_amount.setText("0")
                ui.exchange_rate.setText("0")
                ui.stackedWidget.setCurrentIndex(1)
                ui.continue_lbl.setText("")
                continue

            if nfc_terminal.runtime['CURRENT_STAGE'] == 'pay_nfc':
                if nfc_terminal.runtime['key_pressed'] == "#":
                    nfc_terminal.runtime['CURRENT_STAGE'] = 'pay_qr'
                    continue

            if nfc_terminal.runtime['CURRENT_STAGE'] == 'pay_qr':
                #draw QR here
                pass

            if stages.checkTransactionDone(nfc_terminal.runtime['transaction_address'], nfc_terminal.runtime['amount_to_pay_btc']):
                nfc_terminal.runtime['CURRENT_STAGE'] = 'payment_successful'
                continue

        elif nfc_terminal.runtime['CURRENT_STAGE'] == 'payment_successful':
            pass
        elif nfc_terminal.runtime['CURRENT_STAGE'] == 'payment_cancelled':
            pass
        elif nfc_terminal.runtime['CURRENT_STAGE'] == 'application_halt':
            sys.exit()

        time.sleep(0.05)
