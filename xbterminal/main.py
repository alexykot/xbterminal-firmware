#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
from decimal import Decimal
import time
import sys
import os
import unicodedata
import logging.config
from PyQt4 import QtGui, QtCore

include_path = os.path.abspath(os.path.join(__file__, os.pardir, os.pardir))
sys.path.insert(0, include_path)
import xbterminal
import xbterminal.defaults
xbterminal.defaults.PROJECT_ABS_PATH = include_path

# Set up logging
log_config = xbterminal.defaults.LOG_CONFIG
log_file_path = os.path.abspath(os.path.join(
    xbterminal.defaults.PROJECT_ABS_PATH,
    xbterminal.defaults.LOG_FILE_PATH))
log_config['handlers']['file']['filename'] = log_file_path
logging.config.dictConfig(log_config)
logging.getLogger("requests.packages.urllib3.connectionpool").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

from xbterminal.exceptions import ConfigLoadError
from xbterminal.keypad.keypad import Keypad
import xbterminal.bitcoinaverage
import xbterminal.instantfiat
import xbterminal.gui
import xbterminal.gui.ui
import xbterminal.helpers.nfcpy
import xbterminal.helpers.qr
import xbterminal.helpers.configs
import xbterminal.helpers.wireless
from xbterminal import defaults
from xbterminal.blockchain import blockchain
from xbterminal.gui import gui
from xbterminal import stages
import xbterminal.watcher


def main():
    logger.debug('starting')
    #init runtime
    run = xbterminal.runtime = {}
    run['init'] = {}
    run['init']['internet'] = False
    run['init']['blockchain'] = False
    run['init']['remote_config'] = False
    run['init']['remote_config_last_update'] = None
    run['init']['blockchain_network'] = None
    run['CURRENT_STAGE'] = defaults.STAGES['bootup']
    run['stage_init'] = False
    run['amounts'] = {}
    run['amounts']['amount_to_pay_fiat'] = None
    run['amounts']['amount_to_pay_btc'] = None
    run['key_pressed'] = None
    run['screen_buttons'] = {}
    run['screen_buttons']['qr_button'] = False
    run['screen_buttons']['skip_wifi'] = False
    run['last_activity_timestamp'] = None
    run['current_text_piece'] = 'decimal'
    run['display_value_unformatted'] = ''
    run['display_value_formatted'] = ''
    run['wifi'] = {}
    run['wifi']['try_to_connect'] = False
    run['wifi']['connected'] = False

    xbterminal.gui.runtime = {}
    xbterminal.gui.runtime['app'], xbterminal.gui.runtime['main_win'] = gui.initGUI()
    ui = xbterminal.gui.runtime['main_win'].ui
    gui.advanceLoadingProgressBar(defaults.LOAD_PROGRESS_LEVELS['gui_init'])

    xbterminal.helpers.configs.load_local_state()
    gui.advanceLoadingProgressBar(defaults.LOAD_PROGRESS_LEVELS['local_config_load'])

    keypad = Keypad()
    gui.advanceLoadingProgressBar(defaults.LOAD_PROGRESS_LEVELS['keypad_init'])

    watcher = xbterminal.watcher.Watcher()
    watcher.start()

    xbterminal.local_state['last_started'] = time.time()
    xbterminal.helpers.configs.save_local_state() #@TODO make local_state a custom dict with automated saving on update and get rid of this call

    logger.debug('main loop starting')
    while True:
        # Communicate with watcher
        watcher_messages, watcher_errors = watcher.get_data()
        for level, message in watcher_messages:
            logger.log(level, message)
        if watcher_errors:
            pass

        try:
            xbterminal.gui.runtime['app'].sendPostedEvents()
            xbterminal.gui.runtime['app'].processEvents()
        except NameError as error:
            logger.exception(error)


        if run['key_pressed'] is not None:
            time.sleep(0.1)

        run['key_pressed'] = None
        try:
            run['key_pressed'] = keypad.getKey()
            if run['key_pressed'] is not None:
                if run['key_pressed'] == 'application_halt':
                    run['CURRENT_STAGE'] = defaults.STAGES['application_halt']
                if run['key_pressed'] == 'system_halt':
                    run['CURRENT_STAGE'] = defaults.STAGES['system_halt']
                run['last_activity_timestamp'] = time.time()
        except NameError as error:
            logger.exception(error)

        if run['init']['internet']:
            if (not run['init']['remote_config']
                or (run['init']['remote_config_last_update'] is not None
                    and run['init']['remote_config_last_update']+defaults.REMOTE_CONFIG_UPDATE_CYCLE < time.time())):
                try:
                    xbterminal.helpers.configs.load_remote_config()
                    ui.merchant_name_lbl.setText("{} \n{} ".format(xbterminal.remote_config['MERCHANT_NAME'],
                                                                   xbterminal.remote_config['MERCHANT_DEVICE_NAME'])) #trailing space required
                    run['init']['remote_config'] = True
                    run['init']['remote_config_last_update'] = int(time.time())
                except ConfigLoadError as error:
                    logger.error('remote config load failed, exiting')
                    raise error
                continue

        if hasattr(xbterminal, 'remote_config'):
            if run['init']['blockchain_network'] is None:
                if xbterminal.remote_config['BITCOIN_NETWORK'] == 'testnet':
                    xbterminal.gui.runtime['main_win'].toggleTestnetNotice(True)
                else:
                    xbterminal.gui.runtime['main_win'].toggleTestnetNotice(False)
                run['init']['blockchain_network'] = xbterminal.remote_config['BITCOIN_NETWORK']
            elif run['init']['blockchain_network'] != xbterminal.remote_config['BITCOIN_NETWORK']:
                stages.gracefullExit(system_reboot=True)


###BOOTUP
        if run['CURRENT_STAGE'] == defaults.STAGES['bootup']:
            if not run['stage_init']:
                ui.main_stackedWidget.setCurrentIndex(defaults.SCREENS['load_indefinite'])
                run['stage_init'] = True
                continue

            if (not run['init']['internet']
                and run['CURRENT_STAGE'] != defaults.STAGES['wifi']['choose_ssid']
                and run['CURRENT_STAGE'] != defaults.STAGES['wifi']['enter_passkey']):
                if xbterminal.helpers.wireless.is_wifi_available():
                    try:
                        if ('wifi_ssid' in xbterminal.local_state
                            and xbterminal.local_state['wifi_ssid'] != ''
                            and 'wifi_pass' in xbterminal.local_state
                            and xbterminal.local_state['wifi_pass'] != ''):
                            logger.debug('trying to connect to cached wifi,  '
                                'ssid "{wifi_ssid}" '
                                'password "{wifi_pass}" '.format(wifi_ssid=xbterminal.local_state['wifi_ssid'],
                                                                 wifi_pass=xbterminal.local_state['wifi_pass']))
                            if isinstance(xbterminal.local_state['wifi_pass'], unicode):
                                xbterminal.local_state['wifi_pass'] = unicodedata.normalize('NFKD', xbterminal.local_state['wifi_pass']).encode('ascii','ignore')
                            run['wifi']['connected'] = xbterminal.helpers.wireless.connect(xbterminal.local_state['wifi_ssid'],
                                                                                           xbterminal.local_state['wifi_pass'])
                            if run['wifi']['connected']:
                                run['init']['internet'] = True
                                logger.debug('cached wifi connected')
                            else:
                                del xbterminal.local_state['wifi_ssid']
                                del xbterminal.local_state['wifi_pass']
                                xbterminal.helpers.configs.save_local_state()
                                logger.debug('cached wifi connection failed, wifi setup needed')
                    except KeyError as error:
                        logger.exception(error)

                    if not run['wifi']['connected']:
                        if 'wifi_ssid' in xbterminal.local_state:
                            run['CURRENT_STAGE'] = defaults.STAGES['wifi']['enter_passkey']
                        else:
                            run['CURRENT_STAGE'] = defaults.STAGES['wifi']['choose_ssid']
                        run['wifi']['networks_last_listed_timestamp'] = 0
                        run['wifi']['networks_list_selected_index'] = 0
                        run['wifi']['networks_list_length'] = 0
                        run['stage_init'] = False
                        continue
                else:
                    logger.warning('no wifi found, hoping for preconfigured wired connection')
                    run['init']['internet'] = True
                gui.advanceLoadingProgressBar(defaults.LOAD_PROGRESS_LEVELS['wifi_init'])
                continue

            if run['init']['internet']:
                if (not run['init']['remote_config']
                    or (run['init']['remote_config_last_update'] is not None
                        and run['init']['remote_config_last_update']+defaults.REMOTE_CONFIG_UPDATE_CYCLE < time.time())):
                    try:
                        xbterminal.helpers.configs.load_remote_config()
                        ui.merchant_name_lbl.setText("{} \n{} ".format(xbterminal.remote_config['MERCHANT_NAME'],
                                                                       xbterminal.remote_config['MERCHANT_DEVICE_NAME'])) #trailing space required
                        run['init']['remote_config'] = True
                        run['init']['remote_config_last_update'] = int(time.time())
                    except ConfigLoadError as error:
                        logger.error('remote config load failed, exiting')
                        raise error
                    continue

                if not run['init']['blockchain']:
                    blockchain.init()
                    run['init']['blockchain'] = True
                    gui.advanceLoadingProgressBar(defaults.LOAD_PROGRESS_LEVELS['blockchain_init'])
                    gui.advanceLoadingProgressBar(defaults.LOAD_PROGRESS_LEVELS['finish'])
                    continue

            if run['init']['internet'] and run['init']['remote_config'] and run['init']['blockchain']:
                run['CURRENT_STAGE'] = defaults.STAGES['idle']
                run['stage_init'] = False
                continue

###IDLE
        elif run['CURRENT_STAGE'] == defaults.STAGES['idle']:
            if not run['stage_init']:
                ui.main_stackedWidget.setCurrentIndex(defaults.SCREENS['idle'])
                run['stage_init'] = True
                continue

            if run['key_pressed'] is not None:
                run['CURRENT_STAGE'] = defaults.STAGES['payment']['enter_amount']
                run['stage_init'] = False
                continue

###ENTER AMOUNT
        elif run['CURRENT_STAGE'] == defaults.STAGES['payment']['enter_amount']:
            if not run['stage_init']:
                ui.main_stackedWidget.setCurrentIndex(defaults.SCREENS['enter_amount'])
                ui.amount_input.setText(stages.formatInput(run['display_value_unformatted'], defaults.OUTPUT_DEC_PLACES))
                run['stage_init'] = True
                continue

            if (isinstance(run['key_pressed'], (int, long)) or run['key_pressed'] == 'backspace'):
                if run['key_pressed'] == 'backspace' and run['display_value_unformatted'] == '':
                    run['stage_init'] = False
                    run['CURRENT_STAGE'] = defaults.STAGES['idle']
                    continue

                ui.amount_input.setStyleSheet('background: #FFF')
                ui.error_text_lbl.setText("")
                run['display_value_unformatted'] = stages.processKeyInput(run['display_value_unformatted'], run['key_pressed'])

                run['display_value_formatted'] = stages.formatInput(run['display_value_unformatted'], defaults.OUTPUT_DEC_PLACES)

                ui.amount_input.setText(run['display_value_formatted'])
            elif run['key_pressed'] is 'enter':
                run['amounts']['amount_to_pay_fiat'] = stages.inputToDecimal(run['display_value_unformatted'])
                if run['amounts']['amount_to_pay_fiat'] > 0:
                    run['stage_init'] = False
                    run['CURRENT_STAGE'] = defaults.STAGES['payment']['pay_loading']
                else:
                    ui.amount_input.setStyleSheet('background: #B33A3A')
                    ui.error_text_lbl.setText("no amount entered ") #trailing space here is needed, otherwise last letter if halfcut

###PAY LOADING
        elif run['CURRENT_STAGE'] == defaults.STAGES['payment']['pay_loading']:
            if not run['stage_init']:
                ui.main_stackedWidget.setCurrentIndex(defaults.SCREENS['load_indefinite'])
                ui.indefinite_load_lbl.setText('preparing payment')
                run['stage_init'] = True
                continue

            if run['amounts']['amount_to_pay_fiat'] is None:
                run['CURRENT_STAGE'] = defaults.STAGES['payment']['enter_amount']
                run['stage_init'] = False
                continue

            if run['amounts']['amount_to_pay_btc'] is None:
                run['received_payment'] = False
                run['invoice_paid'] = False

                run['transactions_addresses'] = {}
                run['transactions_addresses']['local'] = blockchain.getFreshAddress()
                run['transactions_addresses']['merchant'] = xbterminal.remote_config['MERCHANT_BITCOIN_ADDRESS']
                run['transactions_addresses']['fee'] = xbterminal.remote_config['OUR_FEE_BITCOIN_ADDRESS']

                if (xbterminal.remote_config['MERCHANT_INSTANTFIAT_EXCHANGE_SERVICE'] is not None
                    and xbterminal.remote_config['MERCHANT_INSTANTFIAT_SHARE'] > 0):
                    (run['amounts']['instantfiat_fiat_amount'],
                     run['amounts']['instantfiat_btc_amount'],
                     run['instantfiat_invoice_id'],
                     run['transactions_addresses']['instantfiat'],
                     run['exchange_rate']) = stages.createInvoice(run['amounts']['amount_to_pay_fiat'])
                else:
                    run['amounts']['instantfiat_fiat_amount'] = Decimal(0).quantize(defaults.BTC_DEC_PLACES)
                    run['amounts']['instantfiat_btc_amount'] = Decimal(0).quantize(defaults.BTC_DEC_PLACES)
                    run['instantfiat_invoice_id'] = None
                    run['transactions_addresses']['instantfiat'] = None
                    run['exchange_rate'] = xbterminal.bitcoinaverage.getExchangeRate(xbterminal.remote_config['MERCHANT_CURRENCY'])

                run['amounts']['our_fee_btc_amount'] = stages.getOurFeeBtcAmount(run['amounts']['amount_to_pay_fiat'], run['exchange_rate'])
                run['amounts']['merchants_btc_amount'] = stages.getMerchantBtcAmount(run['amounts']['amount_to_pay_fiat'], run['exchange_rate'])

                run['amounts']['amount_to_pay_btc'] = (run['amounts']['our_fee_btc_amount']
                                            + run['amounts']['instantfiat_btc_amount']
                                            + run['amounts']['merchants_btc_amount']
                                            + defaults.BTC_DEFAULT_FEE) #tx fee to be paid for forwarding transaction from device to merchant and/or instantfiat
                run['effective_rate_btc'] = run['amounts']['amount_to_pay_fiat'] / run['amounts']['amount_to_pay_btc']

                run['payment_requested_timestamp'] = time.time()
                run['transaction_bitcoin_uri'] = stages.getBitcoinURI(run['transactions_addresses']['local'],
                                                                      run['amounts']['amount_to_pay_btc'])

                run['CURRENT_STAGE'] = defaults.STAGES['payment']['pay_rates']
                run['stage_init'] = False
                continue

###PAY RATES
        elif run['CURRENT_STAGE'] == defaults.STAGES['payment']['pay_rates']:
            if not run['stage_init']:
                ui.main_stackedWidget.setCurrentIndex(defaults.SCREENS['pay_rates'])
                ui.fiat_amount.setText(stages.formatDecimal(run['amounts']['amount_to_pay_fiat'], defaults.OUTPUT_DEC_PLACES))
                ui.btc_amount.setText(stages.formatBitcoin(run['amounts']['amount_to_pay_btc']))
                ui.exchange_rate_amount.setText(stages.formatDecimal(run['effective_rate_btc'] / defaults.BITCOIN_SCALE_DIVIZER,
                                                                     defaults.EXCHANGE_RATE_DEC_PLACES))
                run['stage_init'] = True

            if run['key_pressed'] == 'enter':
                run['CURRENT_STAGE'] = defaults.STAGES['payment']['pay_nfc']
                run['stage_init'] = False
                continue
            if run['key_pressed'] == 'backspace':
                stages.clearPaymentRuntime(False)
                run['CURRENT_STAGE'] = defaults.STAGES['payment']['enter_amount']
                run['stage_init'] = False
                continue

###PAY NFC & QR
        elif (run['CURRENT_STAGE'] == defaults.STAGES['payment']['pay_nfc'] or
                run['CURRENT_STAGE'] == defaults.STAGES['payment']['pay_qr']):
            if not run['stage_init']:
                if run['CURRENT_STAGE'] == defaults.STAGES['payment']['pay_nfc']:
                    ui.main_stackedWidget.setCurrentIndex(defaults.SCREENS['pay_nfc'])
                    ui.fiat_amount_nfc.setText(stages.formatDecimal(run['amounts']['amount_to_pay_fiat'], defaults.OUTPUT_DEC_PLACES))
                    ui.btc_amount_nfc.setText(stages.formatBitcoin(run['amounts']['amount_to_pay_btc']))
                    ui.exchange_rate_nfc.setText(stages.formatDecimal(run['effective_rate_btc'] / defaults.BITCOIN_SCALE_DIVIZER,
                                                                        defaults.EXCHANGE_RATE_DEC_PLACES))
                elif run['CURRENT_STAGE'] == defaults.STAGES['payment']['pay_qr']:
                    ui.main_stackedWidget.setCurrentIndex(defaults.SCREENS['pay_qr'])
                    ui.fiat_amount_qr.setText(stages.formatDecimal(run['amounts']['amount_to_pay_fiat'], defaults.OUTPUT_DEC_PLACES))
                    ui.btc_amount_qr.setText(stages.formatBitcoin(run['amounts']['amount_to_pay_btc']))
                    ui.exchange_rate_qr.setText(stages.formatDecimal(run['effective_rate_btc'] / defaults.BITCOIN_SCALE_DIVIZER,
                                                                         defaults.EXCHANGE_RATE_DEC_PLACES))
                    image_path = os.path.join(defaults.PROJECT_ABS_PATH, defaults.QR_IMAGE_PATH)
                    if run['CURRENT_STAGE'] == defaults.STAGES['payment']['pay_qr']:
                        xbterminal.helpers.qr.qr_gen(stages.getBitcoinURI(run['transactions_addresses']['local'],
                                                                          run['amounts']['amount_to_pay_btc']),
                                                     image_path)
                    else:
                        xbterminal.helpers.qr.qr_gen(run['transactions_addresses']['local'],
                                                     image_path) #address only qr
                    ui.qr_address_lbl.setText(run['transactions_addresses']['local'])
                    ui.qr_image.setPixmap(QtGui.QPixmap(image_path))
                    logger.debug('payment qr code requested')

                logger.debug('local payment requested, address: {local_address}, '
                    'amount fiat: {amount_fiat}, '
                    'amount btc: {amount_btc}, '
                    'rate: {effective_rate}'.
                        format(local_address=run['transactions_addresses']['local'],
                               amount_fiat=run['amounts']['amount_to_pay_fiat'],
                               amount_btc=run['amounts']['amount_to_pay_btc'],
                               effective_rate=run['effective_rate_btc'],
                               ))
                run['stage_init'] = True
                continue

            if run['key_pressed'] == 'backspace':
                stages.clearPaymentRuntime(False)
                xbterminal.helpers.nfcpy.stop()
                run['CURRENT_STAGE'] = defaults.STAGES['payment']['enter_amount']
                run['stage_init'] = False
                continue

            if run['key_pressed'] == 'qr_code' or run['screen_buttons']['qr_button'] == True:
                logger.debug('QR code requested')
                run['screen_buttons']['qr_button'] = False
                run['CURRENT_STAGE'] = defaults.STAGES['payment']['pay_qr']
                run['stage_init'] = False
                continue

            if not run['received_payment']:
                if not xbterminal.helpers.nfcpy.is_active():
                    xbterminal.helpers.nfcpy.start(run['transaction_bitcoin_uri'])
                    logger.debug('nfc bitcoin URI activated: {}'.format(run['transaction_bitcoin_uri']))

                current_balance = blockchain.getAddressBalance(run['transactions_addresses']['local'])
                time.sleep(0.5)
                if current_balance >= run['amounts']['amount_to_pay_btc']:
                    run['received_payment'] = True
                    incoming_tx_hash = blockchain.getLastUnspentTransactionId(run['transactions_addresses']['local'])
                    logger.debug('payment received locally, incoming txid: {txid}'.format(txid=incoming_tx_hash))

                    if current_balance > run['amounts']['amount_to_pay_btc']:
                        run['amounts']['our_fee_btc_amount'] = run['amounts']['our_fee_btc_amount'] + current_balance - run['amounts']['amount_to_pay_btc'] #overpayment goes to our fee
                    amounts = {'instantfiat': run['amounts']['instantfiat_btc_amount'],
                               'merchant': run['amounts']['merchants_btc_amount'],
                               'fee': run['amounts']['our_fee_btc_amount'],
                                }

                    outgoing_tx_hash = stages.createOutgoingTransaction(addresses=run['transactions_addresses'],
                                                                        amounts=amounts)
                    logger.debug('payment forwarded, outgoing txid: {txid},'
                        'addresses: {addresses},'
                        'amounts: {amounts},'.format(txid=outgoing_tx_hash,
                                                     amounts=amounts,
                                                     addresses=run['transactions_addresses']))

                    run['receipt_url'] = stages.logTransaction(
                        run['transactions_addresses']['local'],
                        run['transactions_addresses']['instantfiat'],
                        run['transactions_addresses']['merchant'],

                        incoming_tx_hash,
                        outgoing_tx_hash,
                        run['instantfiat_invoice_id'],

                        run['amounts']['amount_to_pay_fiat'],
                        run['amounts']['amount_to_pay_btc'],
                        run['amounts']['instantfiat_fiat_amount'],
                        run['amounts']['instantfiat_btc_amount'],
                        run['amounts']['our_fee_btc_amount'],

                        xbterminal.remote_config['MERCHANT_CURRENCY'],
                        run['effective_rate_btc']
                    )
                    logger.debug('receipt: {}'.format(run['receipt_url']))

                    stages.clearPaymentRuntime()

                    xbterminal.helpers.nfcpy.stop()
                    run['CURRENT_STAGE'] = defaults.STAGES['payment']['pay_success']
                    run['stage_init'] = False
                    continue

            elif run['invoice_id'] is not None and not run['invoice_paid']:
                if getattr(xbterminal.instantfiat,
                           xbterminal.remote_config['MERCHANT_INSTANTFIAT_EXCHANGE_SERVICE']).isInvoicePaid(run['invoice_id']):
                    xbterminal.helpers.nfcpy.stop()
                    run['CURRENT_STAGE'] = defaults.STAGES['payment']['pay_success']
                    run['stage_init'] = False
                    continue

###PAY SUCCESS
        elif run['CURRENT_STAGE'] == defaults.STAGES['payment']['pay_success']:
            if not run['stage_init']:
                ui.main_stackedWidget.setCurrentIndex(defaults.SCREENS['pay_success'])
                if run['receipt_url'] is not None:
                    image_path = os.path.join(defaults.PROJECT_ABS_PATH, defaults.QR_IMAGE_PATH)
                    xbterminal.helpers.qr.qr_gen(run['receipt_url'], image_path)
                    ui.receipt_qr_image.setPixmap(QtGui.QPixmap(image_path))
                    if not xbterminal.helpers.nfcpy.is_active():
                        xbterminal.helpers.nfcpy.start(run['receipt_url'])
                        logger.debug('nfc receipt URI activated: {}'.format(run['receipt_url']))
                        time.sleep(0.5)
                run['stage_init'] = True
                continue

            if run['key_pressed'] == 'enter':
                xbterminal.helpers.nfcpy.stop()
                run['CURRENT_STAGE'] = defaults.STAGES['payment']['enter_amount']
                run['stage_init'] = False
                continue
            if run['key_pressed'] == 'backspace':
                xbterminal.helpers.nfcpy.stop()
                run['CURRENT_STAGE'] = defaults.STAGES['idle']
                run['stage_init'] = False
                continue

###PAY CANCEL
        elif run['CURRENT_STAGE'] == defaults.STAGES['payment']['pay_cancel']:
            if not run['stage_init']:
                ui.main_stackedWidget.setCurrentIndex(defaults.SCREENS['pay_cancel'])
                run['stage_init'] = True
                continue

            if run['key_pressed'] is not None:
                run['display_value_unformatted'] = ''
                run['display_value_formatted'] = stages.formatInput(run['display_value_unformatted'], defaults.OUTPUT_DEC_PLACES)
                ui.amount_input.setText(run['display_value_formatted'])

                ui.main_stackedWidget.setCurrentIndex(defaults.SCREENS['pay_cancel'])
                run['CURRENT_STAGE'] = defaults.STAGES['payment']['enter_amount']
                run['stage_init'] = False
                continue

###CHOOSE SSID
        elif run['CURRENT_STAGE'] == defaults.STAGES['wifi']['choose_ssid']:
            if not run['stage_init']:
                ui.main_stackedWidget.setCurrentIndex(defaults.SCREENS['choose_ssid'])
                run['stage_init'] = True

            if run['screen_buttons']['skip_wifi']:
                logger.warning('wifi setup cancelled, hoping for preconfigured wired connection')
                run['screen_buttons']['skip_wifi'] = False
                run['stage_init'] = False
                run['CURRENT_STAGE'] = defaults.STAGES['bootup']
                run['init']['internet'] = True
                continue

            if run['wifi']['networks_last_listed_timestamp'] + 30 < time.time():
                networks_list = xbterminal.helpers.wireless.discover_networks()
                run['wifi']['networks_last_listed_timestamp'] = time.time()
                if run['wifi']['networks_list_length'] != len(networks_list):
                    run['wifi']['networks_list_length'] = len(networks_list)
                    ui.wifi_listWidget.clear()
                    network_index = 0
                    for network in networks_list:
                        ui.wifi_listWidget.addItem(network['ssid'])
                        if ('wifi_ssid' in xbterminal.local_state
                            and xbterminal.local_state['wifi_ssid'] == network['ssid']):
                            run['wifi']['networks_list_selected_index'] = network_index
                        network_index = network_index + 1

            if run['key_pressed'] is not None:
                if run['key_pressed'] == 8:
                    run['wifi']['networks_list_selected_index'] = min(run['wifi']['networks_list_selected_index']+1,
                                                                      (run['wifi']['networks_list_length']-1))
                elif run['key_pressed'] == 2:
                    run['wifi']['networks_list_selected_index'] = max(run['wifi']['networks_list_selected_index']-1, 0)
                elif run['key_pressed'] == 'enter':
                    xbterminal.local_state['wifi_ssid'] = str(ui.wifi_listWidget.currentItem().text())
                    xbterminal.helpers.configs.save_local_state()
                    run['CURRENT_STAGE'] = defaults.STAGES['wifi']['enter_passkey']
                    run['stage_init'] = False
                    continue

            ui.wifi_listWidget.setCurrentRow(run['wifi']['networks_list_selected_index'])

###ENTER PASSKEY
        elif run['CURRENT_STAGE'] == defaults.STAGES['wifi']['enter_passkey']:
            if not run['stage_init']:
                ui.main_stackedWidget.setCurrentIndex(defaults.SCREENS['enter_passkey'])
                ui.ssid_entered_lbl.setText(xbterminal.local_state['wifi_ssid'])
                xbterminal.local_state['wifi_pass'] = ''
                run['stage_init'] = True

            if run['key_pressed'] is not None:
                xbterminal.gui.runtime['main_win'].toggleWifiWrongPasswordState(False)

                if keypad.checkIsDone(run['key_pressed']):
                    run['wifi']['try_to_connect'] = True
                    xbterminal.gui.runtime['main_win'].toggleWifiConnectingState(True)
                    continue
                elif keypad.checkIsCancelled(xbterminal.local_state['wifi_pass'], run['key_pressed']):
                    del xbterminal.local_state['wifi_ssid']
                    del xbterminal.local_state['wifi_pass']
                    xbterminal.helpers.configs.save_local_state()
                    run['CURRENT_STAGE'] = defaults.STAGES['wifi']['choose_ssid']
                    run['stage_init'] = False
                    continue
                else:
                    xbterminal.local_state['wifi_pass'] = keypad.createAlphaNumString(xbterminal.local_state['wifi_pass'],
                                                                                        run['key_pressed'])
                char_selector_tupl = keypad.getCharSelectorTupl(run['key_pressed'])
                if char_selector_tupl is not None:
                    char_select_str = gui.formatCharSelectHelperHMTL(char_selector_tupl,
                                                                     xbterminal.local_state['wifi_pass'][-1])
                else:
                    char_select_str = ''
                ui.input_help_lbl.setText(char_select_str)

                ui.password_input.setText(xbterminal.local_state['wifi_pass'])

            if run['wifi']['try_to_connect']:
                run['wifi']['try_to_connect'] = False
                logger.debug('trying to connect to wifi, '
                    'ssid: "{ssid}", pass: "{passkey}" '.format(ssid=xbterminal.local_state['wifi_ssid'],
                                                                passkey=xbterminal.local_state['wifi_pass']))
                run['wifi']['connected'] = xbterminal.helpers.wireless.connect(xbterminal.local_state['wifi_ssid'],
                                                                               xbterminal.local_state['wifi_pass'])
                if run['wifi']['connected']:
                    run['init']['internet'] = True
                    logger.debug('connected to wifi, ssid: {ssid}'.format(ssid=xbterminal.local_state['wifi_ssid']))
                    xbterminal.helpers.configs.save_local_state()
                    run['CURRENT_STAGE'] = defaults.STAGES['wifi']['wifi_connected']
                    run['stage_init'] = False
                    continue
                else:
                    logger.debug('wifi wrong passkey')
                    xbterminal.gui.runtime['main_win'].toggleWifiConnectingState(False)
                    xbterminal.gui.runtime['main_win'].toggleWifiWrongPasswordState(True)


###WIFI CONNECTED
        elif run['CURRENT_STAGE'] == defaults.STAGES['wifi']['wifi_connected']:
            if not run['stage_init']:
                ui.main_stackedWidget.setCurrentIndex(defaults.SCREENS['wifi_connected'])
                run['stage_init'] = True
                continue

            time.sleep(3)
            run['CURRENT_STAGE'] = defaults.STAGES['bootup']
            run['stage_init'] = False
            continue

###APPLICATION HALT
        elif run['CURRENT_STAGE'] == defaults.STAGES['application_halt']:
            stages.gracefullExit()

###SYSTEM HALT
        elif run['CURRENT_STAGE'] == defaults.STAGES['system_halt']:
            stages.gracefullExit(True)

###INACTIVITY STATE RESET
        if (run['CURRENT_STAGE'] in defaults.STAGES['payment']
            and run['last_activity_timestamp'] + defaults.TRANSACTION_TIMEOUT < time.time()):

            stages.clearPaymentRuntime()
            xbterminal.helpers.nfcpy.stop()

            if (run['CURRENT_STAGE'] == defaults.STAGES['payment']['pay_nfc']
                or run['CURRENT_STAGE'] == defaults.STAGES['payment']['pay_qr']):
                run['last_activity_timestamp'] = (time.time()
                                                  - defaults.TRANSACTION_TIMEOUT
                                                  + defaults.TRANSACTION_CANCELLED_MESSAGE_TIMEOUT)
                run['CURRENT_STAGE'] = defaults.STAGES['payment']['pay_cancel']
                run['stage_init'] = False
            else:
                run['CURRENT_STAGE'] = defaults.STAGES['idle']
                run['stage_init'] = False
            continue

        time.sleep(0.1)


try:
    main()
except Exception as error:
    logger.exception(error)

xbterminal.stages.gracefullExit()



