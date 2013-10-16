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

    app, main_win = gui.initGUI()

    while True:
        # At beginning of each loop push events
        try:
            app.sendPostedEvents()
            app.processEvents()
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
                main_win.ui.stackedWidget.setCurrentIndex(1)
                nfc_terminal.runtime['CURRENT_STAGE'] = 'enter_amount'
                main_win.ui.amount_text.setText(nfc_terminal.runtime['text_entered'])
                continue

        elif nfc_terminal.runtime['CURRENT_STAGE'] == 'enter_amount':

            if (isinstance(nfc_terminal.runtime['key_pressed'], (int, long))
                or nfc_terminal.runtime['key_pressed'] == "."
                or nfc_terminal.runtime['key_pressed'] == "A"
                or nfc_terminal.runtime['key_pressed'] == "B"):
                nfc_terminal.runtime['text_entered'] = stages.processAmountKeyInput(nfc_terminal.runtime['text_entered'], nfc_terminal.runtime['key_pressed'])
                main_win.ui.amount_text.setText(nfc_terminal.runtime['text_entered'])
            elif nfc_terminal.runtime['key_pressed'] is "D":
                nfc_terminal.runtime['amount_to_pay_fiat'] = stages.amountInputToDecimal(nfc_terminal.runtime['text_entered'])
                if nfc_terminal.runtime['amount_to_pay_fiat'] > 0:
                    main_win.ui.stackedWidget.setCurrentIndex(2)
                    nfc_terminal.runtime['CURRENT_STAGE'] = 'pay_nfc'
                else:
                    #show error message here
                    pass
                continue

        elif nfc_terminal.runtime['CURRENT_STAGE'] == 'pay_nfc' or nfc_terminal.runtime['CURRENT_STAGE'] == 'pay_qr':
            if nfc_terminal.runtime['amount_to_pay_fiat'] is None:
                main_win.ui.stackedWidget.setCurrentIndex(1)
                nfc_terminal.runtime['CURRENT_STAGE'] = 'enter_amount'
                continue

            if nfc_terminal.runtime['amount_to_pay_btc'] is None:
                our_fee_btc_amount, instantfiat_btc_amount, merchants_btc_fiat_amount = stages.getBtcSharesAmounts(nfc_terminal.runtime['amount_to_pay_fiat'])

                nfc_terminal.runtime['amount_to_pay_btc'] = our_fee_btc_amount + instantfiat_btc_amount + merchants_btc_fiat_amount
                nfc_terminal.runtime['rate_btc'] = nfc_terminal.runtime['amount_to_pay_fiat'] / nfc_terminal.runtime['amount_to_pay_btc']

                nfc_terminal.runtime['transaction_address'] = stages.getTransactionAddress(nfc_terminal.runtime['amount_to_pay_btc'])

                main_win.ui.fiat_amount.setText(stages.amountDecimalToOutput(nfc_terminal.runtime['amount_to_pay_fiat']))
                main_win.ui.btc_amount.setText(str(nfc_terminal.runtime['amount_to_pay_btc']))
                main_win.ui.exchange_rate.setText(stages.amountDecimalToOutput(nfc_terminal.runtime['rate_btc']))

            if nfc_terminal.runtime['key_pressed'] == "A":
                main_win.ui.stackedWidget.setCurrentIndex(1)
                nfc_terminal.runtime['amount_to_pay_btc'] = None
                nfc_terminal.runtime['rate_btc'] = None
                nfc_terminal.runtime['transaction_address'] = None
                nfc_terminal.runtime['CURRENT_STAGE'] = 'enter_amount'
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
