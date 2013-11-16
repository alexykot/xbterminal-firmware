# -*- coding: utf-8 -*-
from decimal import Decimal
import time
import sys
import os
from PyQt4 import QtGui, QtCore

import xbterminal
import xbterminal.bitcoinaverage
import xbterminal.instantfiat
from xbterminal import defaults
from xbterminal import blockchain
from xbterminal.gui import gui
from xbterminal import stages
from xbterminal import helpers
import xbterminal.helpers.nfcpy
import xbterminal.helpers.qr
import xbterminal.helpers.configs
from xbterminal.helpers.log import write_msg_log

try:
    from xbterminal.keypad import keypad
except ImportError:
    pass

def main():

    # Setup GUI and local variables
    xbterminal.gui.runtime = {}
    xbterminal.gui.runtime['app'], xbterminal.gui.runtime['main_win'] = gui.initGUI()
    ui = xbterminal.gui.runtime['main_win'].ui

    # Load configs
    xbterminal.helpers.configs.load_config()

    #init runtime data
    defaults.QR_IMAGE_PATH = os.path.join(defaults.PROJECT_ABS_PATH, 'xbterminal', 'images', 'qr.png')
    xbterminal.runtime = {}
    run = xbterminal.runtime
    run['CURRENT_STAGE'] = defaults.STAGES[0]
    run['amount_to_pay_fiat'] = None
    run['amount_to_pay_btc'] = None
    run['key_pressed'] = None
    run['current_text_piece'] = 'decimal'
    run['display_value_unformatted'] = ''
    run['display_value_formatted'] = ''

    blockchain.init()

    try:
        kp = keypad.keypad(columnCount=4)
    except NameError:
        pass

    write_msg_log("STAGE: Initialisation", 'DEBUG')

    while True:
        # At beginning of each loop push events
        try:
            xbterminal.gui.runtime['app'].sendPostedEvents()
            xbterminal.gui.runtime['app'].processEvents()
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
            if run['key_pressed'] is not None:
                ui.stackedWidget.setCurrentIndex(1)
                run['CURRENT_STAGE'] = 'enter_amount'
                ui.amount_text.setText(stages.formatInput(run['display_value_unformatted'], defaults.OUTPUT_DEC_PLACES))
                continue

        elif run['CURRENT_STAGE'] == 'enter_amount':
            if (isinstance(run['key_pressed'], (int, long)) or run['key_pressed'] == "A"):
                if run['key_pressed'] == "A" and run['display_value_unformatted'] == '':
                    ui.stackedWidget.setCurrentIndex(0)
                    run['CURRENT_STAGE'] = 'standby'
                    continue

                ui.amount_text.setStyleSheet('background: #FFF')
                run['display_value_unformatted'] = stages.processKeyInput(run['display_value_unformatted'], run['key_pressed'])

                run['display_value_formatted'] = stages.formatInput(run['display_value_unformatted'], defaults.OUTPUT_DEC_PLACES)

                ui.amount_text.setText(run['display_value_formatted'])
            elif run['key_pressed'] is "D":
                run['amount_to_pay_fiat'] = stages.inputToDecimal(run['display_value_unformatted'])
                if run['amount_to_pay_fiat'] > 0:
                    ui.stackedWidget.setCurrentIndex(2)
                    run['CURRENT_STAGE'] = 'prepare_payment'
                else:
                    ui.amount_text.setStyleSheet('background: #B33A3A')
                    ui.continue_lbl.setText("error: no amount entered")
                    pass
                continue

        elif run['CURRENT_STAGE'] == 'prepare_payment':
            if run['amount_to_pay_fiat'] is None:
                ui.stackedWidget.setCurrentIndex(1)
                run['CURRENT_STAGE'] = 'enter_amount'
                continue

            if run['amount_to_pay_btc'] is None:
                run['qr_rendered'] = False
                run['received_payment'] = False
                run['invoice_paid'] = False

                run['transactions_addresses'] = {}
                run['transactions_addresses']['local'] = blockchain.getFreshAddress()
                run['transactions_addresses']['merchant'] = defaults.MERCHANT_BITCOIN_ADDRESS
                run['transactions_addresses']['fee'] = defaults.OUR_FEE_BITCOIN_ADDRESS

                if defaults.MERCHANT_INSTANTFIAT_EXCHANGE_SERVICE is not None and defaults.MERCHANT_INSTANTFIAT_SHARE > 0:
                    (instantfiat_btc_amount,
                     run['instantfiat_invoice_id'],
                     run['transactions_addresses']['instantfiat'],
                     run['exchange_rate']) = stages.createInvoice(run['amount_to_pay_fiat'])
                else:
                    instantfiat_btc_amount = Decimal(0).quantize(defaults.BTC_DEC_PLACES)
                    run['instantfiat_invoice_id'] = None
                    run['transactions_addresses']['instantfiat'] = None
                    run['exchange_rate'] = xbterminal.bitcoinaverage.getExchangeRate(defaults.MERCHANT_CURRENCY)

                our_fee_btc_amount = stages.getOurFeeBtcAmount(run['amount_to_pay_fiat'], run['exchange_rate'])
                merchants_btc_amount = stages.getMerchantBtcAmount(run['amount_to_pay_fiat'], run['exchange_rate'])

                run['amount_to_pay_btc'] = (our_fee_btc_amount
                                            + instantfiat_btc_amount
                                            + merchants_btc_amount
                                            + defaults.BTC_DEFAULT_FEE) #tx fee to be paid for forwarding transaction from device to merchant and/or instantfiat
                run['rate_btc'] = run['amount_to_pay_fiat'] / run['amount_to_pay_btc']

                run['payment_requested_timestamp'] = time.time()
                run['transaction_bitcoin_uri'] = stages.getBitcoinURI(run['transactions_addresses']['local'],
                                                                      run['amount_to_pay_btc'])

                helpers.nfcpy.start(run['transaction_bitcoin_uri'])


                print ''
                print '<<<'
                print "fiat to pay: " + str(run['amount_to_pay_fiat'])
                print "instantfiat: " + str(instantfiat_btc_amount)
                print "merchant: " + str(merchants_btc_amount)
                print "fee: " + str(our_fee_btc_amount)
                print "tx_fee: " + str(defaults.BTC_DEFAULT_FEE)
                print "total: " + str(run['amount_to_pay_btc'])
                print ''
                print "local address: " + str(run['transactions_addresses']['local'])
                print "instantfiat address: " + str(run['transactions_addresses']['instantfiat'])
                print "merchant address: " + str(run['transactions_addresses']['merchant'])
                print "fee address: " + str(run['transactions_addresses']['fee'])
                print '>>>'
                print ''

                run['CURRENT_STAGE'] = 'pay_nfc'
                continue

        elif run['CURRENT_STAGE'] == 'pay_nfc' or run['CURRENT_STAGE'] == 'pay_qr' or run['CURRENT_STAGE'] == 'pay_qr_addr_only':
            ui.fiat_amount.setText(stages.formatDecimal(run['amount_to_pay_fiat'], defaults.OUTPUT_DEC_PLACES))
            ui.btc_amount.setText(str(run['amount_to_pay_btc']))
            ui.exchange_rate.setText(stages.formatDecimal(run['rate_btc'], defaults.OUTPUT_DEC_PLACES))

            if run['key_pressed'] == "A" or run['payment_requested_timestamp'] + defaults.IN_PERSON_TRANSACTION_TIMEOUT < time.time():
                run['amount_to_pay_btc'] = None
                run['rate_btc'] = None
                run['transactions_addresses'] = None
                run['payment_requested_timestamp'] = None
                # run['display_value_unformatted'] = ''
                # run['display_value_formatted'] = stages.formatInput(run['display_value_unformatted'], defaults.OUTPUT_DEC_PLACES)

                # ui.amount_text.setText(run['display_value_formatted'])
                # ui.fiat_amount.setText("0")
                # ui.btc_amount.setText("0")
                # ui.exchange_rate.setText("0")
                # ui.continue_lbl.setText("")
                ui.stackedWidget.setCurrentIndex(1)

                run['CURRENT_STAGE'] = 'enter_amount'
                continue

            if run['key_pressed'] == "#":
                if run['CURRENT_STAGE'] == 'pay_nfc':
                    run['CURRENT_STAGE'] = 'pay_qr'
                elif run['CURRENT_STAGE'] == 'pay_qr':
                    run['qr_rendered'] = False
                    run['CURRENT_STAGE'] = 'pay_qr_addr_only'
                elif run['CURRENT_STAGE'] == 'pay_qr_addr_only':
                    run['qr_rendered'] = False
                    run['CURRENT_STAGE'] = 'pay_qr'
                continue

            if (run['CURRENT_STAGE'] == 'pay_qr' or run['CURRENT_STAGE'] == 'pay_qr_addr_only') and not run['qr_rendered']:
                helpers.qr.ensure_dir(defaults.QR_IMAGE_PATH)
                if run['CURRENT_STAGE'] == 'pay_qr':
                    helpers.qr.qr_gen(stages.getBitcoinURI(run['transactions_addresses']['local'], run['amount_to_pay_btc'])).save(defaults.QR_IMAGE_PATH)
                else:
                    helpers.qr.qr_gen(run['transactions_addresses']['local']).save(defaults.QR_IMAGE_PATH)
                ui.stackedWidget.setCurrentIndex(3)
                ui.qr_address_lbl.setText(run['transactions_addresses']['local'])
                ui.qr_image.setPixmap(QtGui.QPixmap(defaults.QR_IMAGE_PATH))
                run['qr_rendered'] = True

            if not run['received_payment']:
                current_balance = blockchain.getAddressBalance(run['transactions_addresses']['local'])
                if current_balance >= run['amount_to_pay_btc']:
                    run['received_payment'] = True
                    if current_balance > run['amount_to_pay_btc']:
                        our_fee_btc_amount = our_fee_btc_amount + current_balance - run['amount_to_pay_btc'] #overpayment goes to our fee
                    amounts = {'instantfiat': instantfiat_btc_amount,
                               'merchant': merchants_btc_amount,
                               'fee': our_fee_btc_amount,
                                }
                    tx_hash = stages.createOutgoingTransaction(amounts=amounts,
                                                               addresses=run['transactions_addresses'])


                    run['CURRENT_STAGE'] = 'payment_successful'
                    ui.stackedWidget.setCurrentIndex(4)

                    continue
            elif run['invoice_id'] is not None and not run['invoice_paid']:
                if getattr(xbterminal.instantfiat, defaults.MERCHANT_INSTANTFIAT_EXCHANGE_SERVICE).isInvoicePaid(run['invoice_id']):
                    run['CURRENT_STAGE'] = 'payment_successful'
                    continue

        elif run['CURRENT_STAGE'] == 'payment_successful':
            helpers.nfcpy.stop()
            if run['key_pressed'] is not None:
                ui.stackedWidget.setCurrentIndex(0)
                run['CURRENT_STAGE'] = 'enter_amount'
                ui.amount_text.setText(stages.formatInput(run['display_value_unformatted'], defaults.OUTPUT_DEC_PLACES))
                continue
            pass
        elif run['CURRENT_STAGE'] == 'payment_cancelled':
            helpers.nfcpy.stop()
            if run['key_pressed'] is not None:
                ui.stackedWidget.setCurrentIndex(0)
                run['CURRENT_STAGE'] = 'enter_amount'
                ui.amount_text.setText(stages.formatInput(run['display_value_unformatted'], defaults.OUTPUT_DEC_PLACES))
                continue
            pass
        elif run['CURRENT_STAGE'] == 'application_halt':
            helpers.nfcpy.stop()
            sys.exit()

        time.sleep(0.1)

