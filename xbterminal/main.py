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
import xbterminal.helpers.wireless
from xbterminal.helpers.log import log

try:
    from xbterminal.keypad import keypad
except ImportError:
    pass

def main():
    xbterminal.helpers.configs.load_configs()

    # Setup GUI and local variables
    xbterminal.gui.runtime = {}
    xbterminal.gui.runtime['app'], xbterminal.gui.runtime['main_win'] = gui.initGUI()
    ui = xbterminal.gui.runtime['main_win'].ui

    #init runtime data
    defaults.QR_IMAGE_PATH = os.path.join(defaults.PROJECT_ABS_PATH, 'xbterminal', 'images', 'qr.png')
    xbterminal.runtime = {}
    run = xbterminal.runtime
    run['CURRENT_STAGE'] = defaults.STAGES['default']
    run['amount_to_pay_fiat'] = None
    run['amount_to_pay_btc'] = None
    run['key_pressed'] = None
    run['last_activity_timestamp'] = None
    run['current_text_piece'] = 'decimal'
    run['display_value_unformatted'] = ''
    run['display_value_formatted'] = ''
    run['wifi'] = {}
    run['wifi']['connected'] = False

    if 'wifi_ssid' in xbterminal.local_state and 'wifi_pass' in xbterminal.local_state and False:
        run['wifi']['connected'] = xbterminal.helpers.wireless.connect(xbterminal.local_state['wifi_ssid'], xbterminal.local_state['wifi_pass'])

    if not run['wifi']['connected']:
        run['CURRENT_STAGE'] = defaults.STAGES['wifi']['choose_ssid']
        run['wifi']['networks_last_listed_timestamp'] = 0
        run['wifi']['networks_list_selected_index'] = 0
        run['wifi']['networks_list_length'] = 0

    #blockchain.init()

    try:
        kp = keypad.keypad(columnCount=4)
    except NameError:
        pass

    xbterminal.local_state['last_started'] = time.time()
    xbterminal.helpers.configs.save_local_state() #@TODO make local_state a custom dict with automated saving on update and get rid of this call

    log('main loop starting', xbterminal.defaults.LOG_MESSAGE_TYPES['DEBUG'])
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
                run['last_activity_timestamp'] = time.time()
                time.sleep(0.2)
        except NameError:
            pass

        if run['CURRENT_STAGE'] == defaults.STAGES['default']:
            if run['key_pressed'] is not None:
                ui.stackedWidget.setCurrentIndex(1)
                run['CURRENT_STAGE'] = defaults.STAGES['payment']['enter_amount']
                ui.amount_text.setText(stages.formatInput(run['display_value_unformatted'], defaults.OUTPUT_DEC_PLACES))
                continue

        elif run['CURRENT_STAGE'] == defaults.STAGES['payment']['enter_amount']:
            if (isinstance(run['key_pressed'], (int, long)) or run['key_pressed'] == "A"):
                if run['key_pressed'] == "A" and run['display_value_unformatted'] == '':
                    ui.stackedWidget.setCurrentIndex(0)
                    run['CURRENT_STAGE'] = defaults.STAGES['default']
                    continue

                ui.amount_text.setStyleSheet('background: #FFF')
                run['display_value_unformatted'] = stages.processKeyInput(run['display_value_unformatted'], run['key_pressed'])

                run['display_value_formatted'] = stages.formatInput(run['display_value_unformatted'], defaults.OUTPUT_DEC_PLACES)

                ui.amount_text.setText(run['display_value_formatted'])
            elif run['key_pressed'] is "D":
                run['amount_to_pay_fiat'] = stages.inputToDecimal(run['display_value_unformatted'])
                if run['amount_to_pay_fiat'] > 0:
                    ui.stackedWidget.setCurrentIndex(2)
                    run['CURRENT_STAGE'] = defaults.STAGES['payment']['prepare_payment']
                else:
                    ui.amount_text.setStyleSheet('background: #B33A3A')
                    ui.continue_lbl.setText("error: no amount entered")
                    pass
                continue

        elif run['CURRENT_STAGE'] == defaults.STAGES['payment']['prepare_payment']:
            if run['amount_to_pay_fiat'] is None:
                ui.stackedWidget.setCurrentIndex(1)
                run['CURRENT_STAGE'] = defaults.STAGES['payment']['enter_amount']
                continue

            if run['amount_to_pay_btc'] is None:
                run['qr_rendered'] = False
                run['received_payment'] = False
                run['invoice_paid'] = False

                run['transactions_addresses'] = {}
                run['transactions_addresses']['local'] = blockchain.getFreshAddress()
                run['transactions_addresses']['merchant'] = xbterminal.remote_config['MERCHANT_BITCOIN_ADDRESS']
                run['transactions_addresses']['fee'] = xbterminal.remote_config['OUR_FEE_BITCOIN_ADDRESS']

                if xbterminal.remote_config['MERCHANT_INSTANTFIAT_EXCHANGE_SERVICE'] is not None and xbterminal.remote_config['MERCHANT_INSTANTFIAT_SHARE'] > 0:
                    (instantfiat_btc_amount,
                     run['instantfiat_invoice_id'],
                     run['transactions_addresses']['instantfiat'],
                     run['exchange_rate']) = stages.createInvoice(run['amount_to_pay_fiat'])
                else:
                    instantfiat_btc_amount = Decimal(0).quantize(defaults.BTC_DEC_PLACES)
                    run['instantfiat_invoice_id'] = None
                    run['transactions_addresses']['instantfiat'] = None
                    run['exchange_rate'] = xbterminal.bitcoinaverage.getExchangeRate(xbterminal.remote_config['MERCHANT_CURRENCY'])

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

                run['CURRENT_STAGE'] = defaults.STAGES['payment']['pay_nfc']
                continue

        elif (run['CURRENT_STAGE'] == defaults.STAGES['payment']['pay_nfc']
              or run['CURRENT_STAGE'] == defaults.STAGES['payment']['pay_qr']
              or run['CURRENT_STAGE'] == defaults.STAGES['payment']['pay_qr_addr_only']):
            ui.fiat_amount.setText(stages.formatDecimal(run['amount_to_pay_fiat'], defaults.OUTPUT_DEC_PLACES))
            ui.btc_amount.setText(str(run['amount_to_pay_btc']))
            ui.exchange_rate.setText(stages.formatDecimal(run['rate_btc'], defaults.OUTPUT_DEC_PLACES))

            if run['key_pressed'] == "A":
                run['amount_to_pay_btc'] = None
                run['amount_to_pay_fiat'] = None
                run['rate_btc'] = None
                run['transactions_addresses'] = None

                ui.fiat_amount.setText("0")
                ui.btc_amount.setText("0")
                ui.exchange_rate.setText("0")
                ui.continue_lbl.setText("")

                ui.stackedWidget.setCurrentIndex(1)

                run['CURRENT_STAGE'] = defaults.STAGES['payment']['enter_amount']
                continue

            if run['key_pressed'] == "#":
                if run['CURRENT_STAGE'] == defaults.STAGES['payment']['pay_nfc']:
                    run['CURRENT_STAGE'] = defaults.STAGES['payment']['pay_qr']
                elif run['CURRENT_STAGE'] == defaults.STAGES['payment']['pay_qr']:
                    run['qr_rendered'] = False
                    run['CURRENT_STAGE'] = defaults.STAGES['payment']['pay_qr_addr_only']
                elif run['CURRENT_STAGE'] == defaults.STAGES['payment']['pay_qr_addr_only']:
                    run['qr_rendered'] = False
                    run['CURRENT_STAGE'] = defaults.STAGES['payment']['pay_qr']
                continue

            if ((run['CURRENT_STAGE'] == defaults.STAGES['payment']['pay_qr'] or run['CURRENT_STAGE'] == defaults.STAGES['payment']['pay_qr_addr_only'])
                and not run['qr_rendered']):
                if run['CURRENT_STAGE'] == defaults.STAGES['payment']['pay_qr']:
                    helpers.qr.qr_gen(stages.getBitcoinURI(run['transactions_addresses']['local'], run['amount_to_pay_btc']), defaults.QR_IMAGE_PATH)
                else:
                    helpers.qr.qr_gen(run['transactions_addresses']['local'], defaults.QR_IMAGE_PATH)
                ui.stackedWidget.setCurrentIndex(3)
                ui.qr_address_lbl.setText(run['transactions_addresses']['local'])
                ui.qr_image.setPixmap(QtGui.QPixmap(defaults.QR_IMAGE_PATH))
                run['qr_rendered'] = True

            if not run['received_payment']:
                if not helpers.nfcpy.is_active():
                    helpers.nfcpy.start(run['transaction_bitcoin_uri'])
                    time.sleep(0.5)

                time.sleep(0.5) #hack for RPi, as it can't work faster
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


                    run['display_value_unformatted'] = ''
                    run['display_value_formatted'] = stages.formatInput(run['display_value_unformatted'], defaults.OUTPUT_DEC_PLACES)

                    run['amount_to_pay_btc'] = None
                    run['amount_to_pay_fiat'] = None
                    run['rate_btc'] = None
                    run['transactions_addresses'] = None

                    ui.fiat_amount.setText("0")
                    ui.btc_amount.setText("0")
                    ui.exchange_rate.setText("0")
                    ui.continue_lbl.setText("")

                    run['CURRENT_STAGE'] = defaults.STAGES['payment']['payment_successful']
                    ui.stackedWidget.setCurrentIndex(4)

                    continue
            elif run['invoice_id'] is not None and not run['invoice_paid']:
                if getattr(xbterminal.instantfiat, xbterminal.remote_config['MERCHANT_INSTANTFIAT_EXCHANGE_SERVICE']).isInvoicePaid(run['invoice_id']):
                    run['CURRENT_STAGE'] = defaults.STAGES['payment']['payment_successful']
                    continue

        elif run['CURRENT_STAGE'] == defaults.STAGES['payment']['payment_successful']:
            helpers.nfcpy.stop()
            if run['key_pressed'] is not None:
                run['display_value_unformatted'] = ''
                run['display_value_formatted'] = stages.formatInput(run['display_value_unformatted'], defaults.OUTPUT_DEC_PLACES)
                ui.amount_text.setText(run['display_value_formatted'])

                ui.stackedWidget.setCurrentIndex(1)
                run['CURRENT_STAGE'] = defaults.STAGES['payment']['enter_amount']
                continue
            pass
        elif run['CURRENT_STAGE'] == defaults.STAGES['payment']['payment_cancelled']:
            helpers.nfcpy.stop()
            if run['key_pressed'] is not None:
                run['display_value_unformatted'] = ''
                run['display_value_formatted'] = stages.formatInput(run['display_value_unformatted'], defaults.OUTPUT_DEC_PLACES)
                ui.amount_text.setText(run['display_value_formatted'])

                ui.stackedWidget.setCurrentIndex(1)
                run['CURRENT_STAGE'] = defaults.STAGES['payment']['enter_amount']
                continue
            pass
        elif run['CURRENT_STAGE'] == defaults.STAGES['wifi']['choose_ssid']:
            ui.stackedWidget.setCurrentIndex(6)
            if run['wifi']['networks_last_listed_timestamp'] + 15 < time.time():
                networks_list = xbterminal.helpers.wireless.discover_networks()
                run['wifi']['networks_last_listed_timestamp'] = time.time()
                if run['wifi']['networks_list_length'] != len(networks_list):
                    run['wifi']['networks_list_length'] = len(networks_list)
                    ui.listWidget.clear()
                    network_index = 0
                    for network in networks_list:
                        ui.listWidget.addItem(network['ssid'])
                        if ('wifi_ssid' in xbterminal.local_state
                            and xbterminal.local_state['wifi_ssid'] == network['ssid']):
                            run['wifi']['networks_list_selected_index'] = network_index
                        network_index = network_index + 1

            if run['key_pressed'] is not None:
                if run['key_pressed'] == 8:
                    run['wifi']['networks_list_selected_index'] = min(run['wifi']['networks_list_selected_index']+1, (run['wifi']['networks_list_length']-1))
                elif run['key_pressed'] == 2:
                    run['wifi']['networks_list_selected_index'] = max(run['wifi']['networks_list_selected_index']-1, 0)
                elif run['key_pressed'] == 'D':
                    xbterminal.local_state['wifi_ssid'] = str(ui.listWidget.currentItem().text())
                    xbterminal.helpers.configs.save_local_state()
                    run['CURRENT_STAGE'] = defaults.STAGES['wifi']['enter_passkey']
                    continue

            ui.listWidget.setCurrentRow(run['wifi']['networks_list_selected_index'])

            if ui.listWidget.currentItem() != None:
                ui.wifi_lbl.setText("WiFi network - {ssid}".format(ssid=ui.listWidget.currentItem().text()))
        elif run['CURRENT_STAGE'] == defaults.STAGES['wifi']['enter_passkey']:
            ui.stackedWidget.setCurrentIndex(6)
            if 'wifi_pass' not in xbterminal.local_state:
                xbterminal.local_state['wifi_pass'] = ''

            if run['key_pressed'] is not None:
                xbterminal.local_state['wifi_pass'] = kp.formAlphaNumString(xbterminal.local_state['wifi_pass'],
                                                                            run['key_pressed'])

            ui.wifi_lbl.setText(xbterminal.local_state['wifi_pass'])

        elif run['CURRENT_STAGE'] == defaults.STAGES['application_halt']:
            xbterminal.helpers.configs.save_local_state()
            log('application halted', xbterminal.defaults.LOG_MESSAGE_TYPES['DEBUG'])
            helpers.nfcpy.stop()
            sys.exit()

        if run['CURRENT_STAGE'] in defaults.STAGES['payment'] and run['last_activity_timestamp'] + defaults.TRANSACTION_TIMEOUT < time.time():
            run['display_value_unformatted'] = ''
            run['display_value_formatted'] = stages.formatInput(run['display_value_unformatted'], defaults.OUTPUT_DEC_PLACES)
            ui.amount_text.setText(run['display_value_formatted'])

            run['amount_to_pay_btc'] = None
            run['amount_to_pay_fiat'] = None
            run['rate_btc'] = None
            run['transactions_addresses'] = None

            ui.fiat_amount.setText("0")
            ui.btc_amount.setText("0")
            ui.exchange_rate.setText("0")
            ui.continue_lbl.setText("")

            if (run['CURRENT_STAGE'] == defaults.STAGES['payment']['pay_nfc']
                or run['CURRENT_STAGE'] == defaults.STAGES['payment']['pay_qr']
                or run['CURRENT_STAGE'] == defaults.STAGES['payment']['pay_qr_addr_only']):
                run['last_activity_timestamp'] = (time.time()
                                                  - defaults.TRANSACTION_TIMEOUT
                                                  + defaults.TRANSACTION_CANCELLED_MESSAGE_TIMEOUT)
                ui.stackedWidget.setCurrentIndex(5)
                run['CURRENT_STAGE'] = 'payment_cancelled'
            else:
                ui.stackedWidget.setCurrentIndex(0)
                run['CURRENT_STAGE'] = 'standby'
            continue


        time.sleep(0.1)

