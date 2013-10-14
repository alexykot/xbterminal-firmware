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
    nfc_terminal.runtime['entered_text'] = '0.00'
    nfc_terminal.runtime['amount_to_pay_btc'] = None
    nfc_terminal.runtime['key_pressed'] = None

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
                time.sleep(0.1)
        except NameError:
            pass

        if nfc_terminal.runtime['CURRENT_STAGE'] == 'standby':
            if nfc_terminal.runtime['key_pressed'] == "D":
                main_win.ui.stackedWidget.setCurrentIndex(1)
                nfc_terminal.runtime['CURRENT_STAGE'] = 'enter_amount'
                continue
        elif nfc_terminal.runtime['CURRENT_STAGE'] == 'enter_amount':
            if isinstance(nfc_terminal.runtime['key_pressed'], (int, long)) or nfc_terminal.runtime['key_pressed'] == ".":
                if nfc_terminal.runtime['entered_text'] == "0.00":
                    nfc_terminal.runtime['entered_text'] = str(nfc_terminal.runtime['key_pressed'])
                    main_win.ui.continue_lbl.setVisible(True)
                else:
                    nfc_terminal.runtime['entered_text'] += str(nfc_terminal.runtime['key_pressed'])
                main_win.ui.amount_text.setText(nfc_terminal.runtime['entered_text'])
            elif nfc_terminal.runtime['key_pressed'] == "A":
                nfc_terminal.runtime['entered_text'] = nfc_terminal.runtime['entered_text'][:-1]
                main_win.ui.amount_text.setText(nfc_terminal.runtime['entered_text'])
            elif nfc_terminal.runtime['key_pressed'] is "D":
                main_win.ui.stackedWidget.setCurrentIndex(2)
                nfc_terminal.runtime['CURRENT_STAGE'] = 'pay_nfc'
                continue
            elif nfc_terminal.runtime['key_pressed'] is "B":
                nfc_terminal.runtime['entered_text'] = '0.00'
                main_win.ui.amount_text.setText(nfc_terminal.runtime['entered_text'])
        elif nfc_terminal.runtime['CURRENT_STAGE'] == 'pay_nfc' or nfc_terminal.runtime['CURRENT_STAGE'] == 'pay_qr':
            if nfc_terminal.runtime['amount_to_pay_btc'] is None:
                amount_to_pay_fiat = Decimal(nfc_terminal.runtime['entered_text']).quantize(defaults.FIAT_DEC_PLACES)
                our_fee_btc_amount, instantfiat_btc_amount, merchants_btc_fiat_amount = stages.getBtcSharesAmounts(amount_to_pay_fiat)

                nfc_terminal.runtime['amount_to_pay_btc'] = our_fee_btc_amount + instantfiat_btc_amount + merchants_btc_fiat_amount
                nfc_terminal.runtime['rate_btc'] = amount_to_pay_fiat / nfc_terminal.runtime['amount_to_pay_btc']

                nfc_terminal.runtime['transaction_address'] = stages.getTransactionAddress(nfc_terminal.runtime['amount_to_pay_btc'])

                main_win.ui.fiat_amount.setText(amount_to_pay_fiat.quantize('0.00'))
                main_win.ui.btc_amount.setText(nfc_terminal.runtime['amount_to_pay_btc'])
                main_win.ui.exchange_rate.setText(nfc_terminal.runtime['rate_btc'])

            if nfc_terminal.runtime['CURRENT_STAGE'] == 'pay_nfc':
                if nfc_terminal.runtime['key_pressed'] is "#":
                    nfc_terminal.runtime['CURRENT_STAGE'] = 'pay_qr'
                    continue

            if nfc_terminal.runtime['CURRENT_STAGE'] == 'pay_qr':
                #draw QR here
                pass

            stages.checkTransactionDone(nfc_terminal.runtime['transaction_address'], nfc_terminal.runtime['amount_to_pay_btc'])

        elif nfc_terminal.runtime['CURRENT_STAGE'] == 'payment_successful':
            pass
        elif nfc_terminal.runtime['CURRENT_STAGE'] == 'payment_cancelled':
            pass
        elif nfc_terminal.runtime['CURRENT_STAGE'] == 'application_halt':
            sys.exit()

        time.sleep(0.05)
