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
from nfc_terminal.helpers import qr
from nfc_terminal.helpers import uri

try:
    from nfc_terminal.keypad import keypad
except ImportError:
    pass


def main():

    # Setup GUI and local variables
    nfc_terminal.gui.runtime = {}
    nfc_terminal.gui.runtime['app'], nfc_terminal.gui.runtime['main_win'] = gui.initGUI()
    ui = nfc_terminal.gui.runtime['main_win'].ui

    # Load configs
    nfc_terminal.helpers.configs.load_config()

    #init runtime data
    nfc_terminal.runtime = {}
    run = nfc_terminal.runtime
    run['CURRENT_STAGE'] = defaults.STAGES[0]
    run['text_entered'] = defaults.DISPLAY_DEFAULT_VALUE
    run['amount_to_pay_fiat'] = None
    run['amount_to_pay_btc'] = None
    run['key_pressed'] = None
    run['current_text_piece'] = 'decimal'

    try:
        kp = keypad.keypad(columnCount=4)
    except NameError:
        pass

    write_msg_log("STAGE: Initialisation", 'DEBUG')

    while True:
        # At beginning of each loop push events
        try:
            nfc_terminal.gui.runtime['app'].sendPostedEvents()
            nfc_terminal.gui.runtime['app'].processEvents()
        except NameError:
            pass

        run['key_pressed'] = None
        try:
            run['key_pressed'] = kp.getKey()
            if run['key_pressed'] is not None:
                write_msg_log("KEYPAD: Key pressed - {}".format(run['key_pressed']), 'DEBUG')
                time.sleep(0.2)
        except NameError:
            pass

        if run['CURRENT_STAGE'] == 'standby':

            if run['key_pressed'] == "D":
                ui.stackedWidget.setCurrentIndex(1)
                run['CURRENT_STAGE'] = 'enter_amount'
                ui.amount_text.setText("0.00")
                continue

        elif run['CURRENT_STAGE'] == 'enter_amount':

            if (isinstance(run['key_pressed'], (int, long))
                or run['key_pressed'] == "."
                or run['key_pressed'] == "A"
                or run['key_pressed'] == "B"):

                ui.amount_text.setStyleSheet('background: #FFF')

                run['text_entered'] = stages.processKeyInput(run['key_pressed'])
                #run['text_entered'] = stages.processAmountKeyInput(run['text_entered'], run['key_pressed'])
                ui.amount_text.setText(run['text_entered'])

            elif run['key_pressed'] is "D":
                run['amount_to_pay_fiat'] = stages.amountInputToDecimal(run['text_entered'])
                if run['amount_to_pay_fiat'] > 0:
                    ui.stackedWidget.setCurrentIndex(2)
                    run['CURRENT_STAGE'] = 'pay_nfc'
                else:
                    ui.amount_text.setStyleSheet('background: #B33A3A')
                    ui.continue_lbl.setText("error: no amount entered")
                    pass
                continue

        elif run['CURRENT_STAGE'] == 'pay_nfc' or run['CURRENT_STAGE'] == 'pay_qr':
            if run['amount_to_pay_fiat'] is None:
                ui.stackedWidget.setCurrentIndex(1)
                run['CURRENT_STAGE'] = 'enter_amount'
                continue

            if run['amount_to_pay_btc'] is None:
                our_fee_btc_amount, instantfiat_btc_amount, merchants_btc_fiat_amount = stages.getBtcSharesAmounts(run['amount_to_pay_fiat'])

                run['amount_to_pay_btc'] = our_fee_btc_amount + instantfiat_btc_amount + merchants_btc_fiat_amount
                run['rate_btc'] = run['amount_to_pay_fiat'] / run['amount_to_pay_btc']

                run.transactions_addresses = {}
                (run.transactions_addresses['local'],
                 run.transactions_addresses['instantfiat'],
                 run.transactions_addresses['merchant'],
                 run.transactions_addresses['fee']) = stages.getTransactionAddresses(instantfiat_btc_amount,
                                                                                     merchants_btc_fiat_amount,
                                                                                     our_fee_btc_amount)
                run['transaction_bitcoin_uri'] = stages.getBitcoinURI(run.transactions_addresses['local'],
                                                                      run['amount_to_pay_btc'], )
                #init NFC here

                ui.fiat_amount.setText(stages.amountDecimalToOutput(run['amount_to_pay_fiat']))
                ui.btc_amount.setText(str(run['amount_to_pay_btc']))
                ui.exchange_rate.setText(stages.amountDecimalToOutput(run['rate_btc']))

            if run['key_pressed'] == "A":

                run['amount_to_pay_btc'] = None
                run['rate_btc'] = None
                run.transactions_addresses = None
                run['CURRENT_STAGE'] = 'enter_amount'
                run['text_entered'] = stages.processAmountKeyInput("", 'B')

                ui.amount_text.setText("0.00")
                ui.fiat_amount.setText("0")
                ui.btc_amount.setText("0")
                ui.exchange_rate.setText("0")
                ui.stackedWidget.setCurrentIndex(1)
                ui.continue_lbl.setText("")
                continue

            if run['CURRENT_STAGE'] == 'pay_nfc':
                if run['key_pressed'] == "#":
                    run['CURRENT_STAGE'] = 'pay_qr'
                    continue

            if run['CURRENT_STAGE'] == 'pay_qr':
                f = qr.current_dir() + "/nfc_terminal/images/" + "qrcode.png"
                qr.ensure_dir(f)
                qr.qr_gen(uri.formatUri(run['amount_to_pay_btc'])).save(f)
                ui.stackedWidget.setCurrentIndex(3)
                ui.qr_address_lbl.setText(run.transactions_addresses['local'])
                ui.qr_image.setPixmap(QtGui.QPixmap('/home/pi/app/nfc_terminal/images/qrcode.png'))

            if stages.checkTransactionDone(run.transactions_addresses['local'], run['amount_to_pay_btc']):
                run['CURRENT_STAGE'] = 'payment_successful'
                continue

        elif run['CURRENT_STAGE'] == 'payment_successful':
            pass
        elif run['CURRENT_STAGE'] == 'payment_cancelled':
            pass
        elif run['CURRENT_STAGE'] == 'application_halt':
            sys.exit()

        time.sleep(0.05)
