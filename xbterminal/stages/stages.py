from decimal import Decimal
import logging
import os.path
import time
import unicodedata

logger = logging.getLogger(__name__)

import xbterminal
from xbterminal import defaults
from xbterminal.stages import payment

import xbterminal.bitcoinaverage
import xbterminal.blockchain.blockchain
import xbterminal.helpers.bt
import xbterminal.helpers.clock
import xbterminal.helpers.configs
import xbterminal.helpers.nfcpy
import xbterminal.helpers.qr
import xbterminal.helpers.wireless
import xbterminal.gui.gui
import xbterminal.exceptions


def bootup(run, ui):
    ui.showScreen('load_indefinite')

    if not run['init']['internet']:
        if xbterminal.helpers.wireless.is_wifi_available():
            run['wifi']['networks_last_listed_timestamp'] = 0
            run['wifi']['networks_list_selected_index'] = 0
            run['wifi']['networks_list_length'] = 0
            if (
                'wifi_ssid' in xbterminal.local_state
                and 'wifi_pass' in xbterminal.local_state
            ):
                # Connect to cached wifi
                logger.debug('trying to connect to cached wifi,  '
                    'ssid "{wifi_ssid}" '
                    'password "{wifi_pass}" '.format(wifi_ssid=xbterminal.local_state['wifi_ssid'],
                                                     wifi_pass=xbterminal.local_state['wifi_pass']))
                if isinstance(xbterminal.local_state['wifi_pass'], unicode):
                    xbterminal.local_state['wifi_pass'] = unicodedata.normalize('NFKD', xbterminal.local_state['wifi_pass']).encode('ascii','ignore')
                run['wifi']['connected'] = xbterminal.helpers.wireless.connect(xbterminal.local_state['wifi_ssid'],
                                                                               xbterminal.local_state['wifi_pass'])
                if run['wifi']['connected']:
                    logger.debug('cached wifi connected')
                    run['init']['internet'] = True
                else:
                    # Clear cache
                    del xbterminal.local_state['wifi_ssid']
                    del xbterminal.local_state['wifi_pass']
                    xbterminal.helpers.configs.save_local_state()
                    logger.debug('cached wifi connection failed, wifi setup needed')
                    return defaults.STAGES['wifi']['choose_ssid']
            elif 'wifi_ssid' in xbterminal.local_state:
                # Enter passkey for cached wifi
                return defaults.STAGES['wifi']['enter_passkey']
            else:
                return defaults.STAGES['wifi']['choose_ssid']
        else:
            logger.warning('no wifi found, hoping for preconfigured wired connection')
            run['init']['internet'] = True
        ui.advanceLoadingProgressBar(defaults.LOAD_PROGRESS_LEVELS['wifi_init'])

    # Check system clock
    # BBB has no battery, so system time gets reset after every reboot and may be wildly incorrect
    while True:
        internet_time = xbterminal.helpers.clock.get_internet_time()
        time_delta = abs(time.time() - internet_time)
        if time_delta < 60:  # 1 minute
            logger.info('clock synchronized')
            run['init']['clock_synchronized'] = True
            xbterminal.local_state['last_started'] = time.time()
            xbterminal.helpers.configs.save_local_state()
            break
        logger.warning('machine time differs from internet time: {0}'.format(time_delta))
        time.sleep(5)

    # Wait for remote config
    while True:
        if run['init']['remote_config']:
            break
        time.sleep(1)

    # Initialize blockchain driver
    xbterminal.blockchain.blockchain.init()
    run['init']['blockchain'] = True
    ui.advanceLoadingProgressBar(defaults.LOAD_PROGRESS_LEVELS['blockchain_init'])
    ui.advanceLoadingProgressBar(defaults.LOAD_PROGRESS_LEVELS['finish'])

    ui.toggleTestnetNotice(xbterminal.remote_config['BITCOIN_NETWORK'] == 'testnet')
    run['init']['blockchain_network'] = xbterminal.remote_config['BITCOIN_NETWORK']

    # Initialize bluetooth server
    run['bluetooth_server'] = xbterminal.helpers.bt.BluetoothServer()

    return defaults.STAGES['idle']


def idle(run, ui):
    ui.showScreen('idle')
    while True:
        if run['keypad'].last_key_pressed is not None:
            if run['keypad'].last_key_pressed in range(10) + ['00']:
                run['display_value_unformatted'] = payment.processKeyInput(run['display_value_unformatted'], run['keypad'].last_key_pressed)
            return defaults.STAGES['payment']['enter_amount']
        time.sleep(0.1)


def enter_amount(run, ui):
    ui.showScreen('enter_amount')
    ui.setText('amount_input', payment.formatInput(run['display_value_unformatted'], defaults.OUTPUT_DEC_PLACES))
    while True:
        if (
            run['keypad'].last_key_pressed in range(10) + ['00']
            or run['keypad'].last_key_pressed == 'backspace'
        ):
            if run['keypad'].last_key_pressed == 'backspace' and run['display_value_unformatted'] == '':
                return defaults.STAGES['idle']
            ui.setStyle('amount_input', 'background: #FFF')
            ui.setText('error_text_lbl', '')
            run['display_value_unformatted'] = payment.processKeyInput(run['display_value_unformatted'], run['keypad'].last_key_pressed)
            run['display_value_formatted'] = payment.formatInput(run['display_value_unformatted'], defaults.OUTPUT_DEC_PLACES)
            ui.setText('amount_input', run['display_value_formatted'])
        elif run['keypad'].last_key_pressed == 'enter':
            run['amounts']['amount_to_pay_fiat'] = payment.inputToDecimal(run['display_value_unformatted'])
            if run['amounts']['amount_to_pay_fiat'] > 0:
                return defaults.STAGES['payment']['pay_loading']
            else:
                ui.setStyle('amount_input', 'background: #B33A3A')
                ui.setText('error_text_lbl', "no amount entered ") #trailing space here is needed, otherwise last letter if halfcut
        if run['last_activity_timestamp'] + defaults.TRANSACTION_TIMEOUT < time.time():
            payment.clearPaymentRuntime(run, ui)
            return defaults.STAGES['idle']
        run['keypad'].resetKey()
        time.sleep(0.1)


def pay_loading(run, ui):
    ui.showScreen('load_indefinite')
    ui.setText('indefinite_load_lbl', 'preparing payment')

    if run['amounts']['amount_to_pay_fiat'] is None:
        return defaults.STAGES['payment']['enter_amount']

    while True:
        run['payment'] = payment.Payment.create_order(run['amounts']['amount_to_pay_fiat'],
                                              run['bluetooth_server'].mac_address)
        if run['payment'] is not None:
            # Payment parameters loaded
            run['amounts']['amount_to_pay_btc'] = run['payment'].btc_amount
            run['effective_rate_btc'] = run['payment'].exchange_rate
            run['transaction_bitcoin_uri'] = run['payment'].payment_uri

            # Prepare QR image
            run['qr_image_path'] = os.path.join(defaults.PROJECT_ABS_PATH, defaults.QR_IMAGE_PATH)
            xbterminal.helpers.qr.qr_gen(run['transaction_bitcoin_uri'], run['qr_image_path'])
            return defaults.STAGES['payment']['pay_rates']
        else:
            # Network error
            time.sleep(1)


def pay_loading_old(run, ui):
    ui.showScreen('load_indefinite')
    ui.setText('indefinite_load_lbl', 'preparing payment')

    if run['amounts']['amount_to_pay_fiat'] is None:
        return defaults.STAGES['payment']['enter_amount']

    run['invoice_paid'] = False

    run['transactions_addresses'] = {}
    run['transactions_addresses']['local'] = xbterminal.blockchain.blockchain.getFreshAddress()
    run['transactions_addresses']['merchant'] = xbterminal.remote_config['MERCHANT_BITCOIN_ADDRESS']
    run['transactions_addresses']['fee'] = xbterminal.remote_config['OUR_FEE_BITCOIN_ADDRESS']

    while True:
        try:
            if (
                xbterminal.remote_config['MERCHANT_INSTANTFIAT_EXCHANGE_SERVICE'] is not None
                and xbterminal.remote_config['MERCHANT_INSTANTFIAT_SHARE'] > 0
            ):
                (run['amounts']['instantfiat_fiat_amount'],
                 run['amounts']['instantfiat_btc_amount'],
                 run['instantfiat_invoice_id'],
                 run['transactions_addresses']['instantfiat'],
                 run['exchange_rate']) = payment.createInvoice(run['amounts']['amount_to_pay_fiat'])
            else:
                run['amounts']['instantfiat_fiat_amount'] = Decimal(0).quantize(defaults.BTC_DEC_PLACES)
                run['amounts']['instantfiat_btc_amount'] = Decimal(0).quantize(defaults.BTC_DEC_PLACES)
                run['instantfiat_invoice_id'] = None
                run['transactions_addresses']['instantfiat'] = None
                run['exchange_rate'] = xbterminal.bitcoinaverage.getExchangeRate(xbterminal.remote_config['MERCHANT_CURRENCY'])
            break
        except xbterminal.exceptions.NetworkError as error:
            # Wait for internet connection
            logger.warning(str(error))
            time.sleep(2)

    run['amounts']['our_fee_btc_amount'] = payment.getOurFeeBtcAmount(run['amounts']['amount_to_pay_fiat'], run['exchange_rate'])
    run['amounts']['merchants_btc_amount'] = payment.getMerchantBtcAmount(run['amounts']['amount_to_pay_fiat'], run['exchange_rate'])

    run['amounts']['amount_to_pay_btc'] = (run['amounts']['our_fee_btc_amount']
                                + run['amounts']['instantfiat_btc_amount']
                                + run['amounts']['merchants_btc_amount']
                                + defaults.BTC_DEFAULT_FEE) #tx fee to be paid for forwarding transaction from device to merchant and/or instantfiat
    run['effective_rate_btc'] = run['amounts']['amount_to_pay_fiat'] / run['amounts']['amount_to_pay_btc']

    run['payment_requested_timestamp'] = time.time()
    run['transaction_bitcoin_uri'] = payment.getBitcoinURI(run['transactions_addresses']['local'],
                                                           run['amounts']['amount_to_pay_btc'])
    # Prepare QR image
    run['qr_image_path'] = os.path.join(defaults.PROJECT_ABS_PATH, defaults.QR_IMAGE_PATH)
    xbterminal.helpers.qr.qr_gen(run['transaction_bitcoin_uri'], run['qr_image_path'])
    return defaults.STAGES['payment']['pay_rates']


def pay_rates(run, ui):
    ui.showScreen('pay_rates')
    ui.setText('fiat_amount', payment.formatDecimal(run['amounts']['amount_to_pay_fiat'], defaults.OUTPUT_DEC_PLACES))
    ui.setText('btc_amount', payment.formatBitcoin(run['amounts']['amount_to_pay_btc']))
    ui.setText('exchange_rate_amount', payment.formatDecimal(
        run['effective_rate_btc'] / defaults.BITCOIN_SCALE_DIVIZER,
        defaults.EXCHANGE_RATE_DEC_PLACES))
    while True:
        if run['keypad'].last_key_pressed == 'enter':
            return defaults.STAGES['payment']['pay']
        elif run['keypad'].last_key_pressed == 'backspace':
            payment.clearPaymentRuntime(run, ui, clear_amounts=False)
            return defaults.STAGES['payment']['enter_amount']
        if run['last_activity_timestamp'] + defaults.TRANSACTION_TIMEOUT < time.time():
            payment.clearPaymentRuntime(run, ui)
            return defaults.STAGES['idle']
        time.sleep(0.1)


def pay(run, ui):
    ui.showScreen('pay_nfc')
    ui.setText('fiat_amount_nfc', payment.formatDecimal(run['amounts']['amount_to_pay_fiat'], defaults.OUTPUT_DEC_PLACES))
    ui.setText('btc_amount_nfc', payment.formatBitcoin(run['amounts']['amount_to_pay_btc']))
    ui.setText('exchange_rate_nfc', payment.formatDecimal(run['effective_rate_btc'] / defaults.BITCOIN_SCALE_DIVIZER,
                                                          defaults.EXCHANGE_RATE_DEC_PLACES))
    logger.debug('local payment requested, '
                 'amount fiat: {amount_fiat}, '
                 'amount btc: {amount_btc}, '
                 'rate: {effective_rate}'.
                    format(amount_fiat=run['amounts']['amount_to_pay_fiat'],
                           amount_btc=run['amounts']['amount_to_pay_btc'],
                           effective_rate=run['effective_rate_btc']))
    run['bluetooth_server'].start(run['payment'])
    while True:
        if run['keypad'].last_key_pressed == 'qr_code' or run['screen_buttons']['qr_button']:
            logger.debug('QR code requested')
            run['screen_buttons']['qr_button'] = False
            ui.showScreen('pay_qr')
            ui.setText('fiat_amount_qr', payment.formatDecimal(run['amounts']['amount_to_pay_fiat'], defaults.OUTPUT_DEC_PLACES))
            ui.setText('btc_amount_qr', payment.formatBitcoin(run['amounts']['amount_to_pay_btc']))
            ui.setText('exchange_rate_qr', payment.formatDecimal(run['effective_rate_btc'] / defaults.BITCOIN_SCALE_DIVIZER,
                                                                 defaults.EXCHANGE_RATE_DEC_PLACES))
            ui.setText('qr_address_lbl', '')
            ui.setImage("qr_image", run['qr_image_path'])
            run['keypad'].resetKey()

        elif run['keypad'].last_key_pressed == 'backspace':
            payment.clearPaymentRuntime(run, ui, clear_amounts=False)
            xbterminal.helpers.nfcpy.stop()
            run['bluetooth_server'].stop()
            return defaults.STAGES['payment']['enter_amount']

        if not xbterminal.helpers.nfcpy.is_active():
            xbterminal.helpers.nfcpy.start(run['transaction_bitcoin_uri'])
            logger.debug('nfc bitcoin URI activated: {}'.format(run['transaction_bitcoin_uri']))
            time.sleep(0.5)

        run['receipt_url'] = run['payment'].check()
        if run['receipt_url'] is not None:
            logger.debug('payment received, receipt: {}'.format(run['receipt_url']))

            run['qr_image_path'] = os.path.join(defaults.PROJECT_ABS_PATH, defaults.QR_IMAGE_PATH)
            xbterminal.helpers.qr.qr_gen(run['receipt_url'], run['qr_image_path'])

            payment.clearPaymentRuntime(run, ui)
            xbterminal.helpers.nfcpy.stop()
            run['bluetooth_server'].stop()
            return defaults.STAGES['payment']['pay_success']

        if run['last_activity_timestamp'] + defaults.TRANSACTION_TIMEOUT < time.time():
            payment.clearPaymentRuntime(run, ui)
            xbterminal.helpers.nfcpy.stop()
            run['bluetooth_server'].stop()
            run['last_activity_timestamp'] = (time.time()
                                                  - defaults.TRANSACTION_TIMEOUT
                                                  + defaults.TRANSACTION_CANCELLED_MESSAGE_TIMEOUT)
            return defaults.STAGES['payment']['pay_cancel']

        time.sleep(0.5)


def pay_old(run, ui):
    ui.showScreen('pay_nfc')
    ui.setText('fiat_amount_nfc', payment.formatDecimal(run['amounts']['amount_to_pay_fiat'], defaults.OUTPUT_DEC_PLACES))
    ui.setText('btc_amount_nfc', payment.formatBitcoin(run['amounts']['amount_to_pay_btc']))
    ui.setText('exchange_rate_nfc', payment.formatDecimal(run['effective_rate_btc'] / defaults.BITCOIN_SCALE_DIVIZER,
                                                                defaults.EXCHANGE_RATE_DEC_PLACES))
    logger.debug('local payment requested, address: {local_address}, '
            'amount fiat: {amount_fiat}, '
            'amount btc: {amount_btc}, '
            'rate: {effective_rate}'.
                format(local_address=run['transactions_addresses']['local'],
                       amount_fiat=run['amounts']['amount_to_pay_fiat'],
                       amount_btc=run['amounts']['amount_to_pay_btc'],
                       effective_rate=run['effective_rate_btc'],
                       ))
    # Wait for incoming transaction
    incoming_tx_hash = None
    while True:
        if run['keypad'].last_key_pressed == 'qr_code' or run['screen_buttons']['qr_button']:
            logger.debug('QR code requested')
            run['screen_buttons']['qr_button'] = False
            ui.showScreen('pay_qr')
            ui.setText('fiat_amount_qr', payment.formatDecimal(run['amounts']['amount_to_pay_fiat'], defaults.OUTPUT_DEC_PLACES))
            ui.setText('btc_amount_qr', payment.formatBitcoin(run['amounts']['amount_to_pay_btc']))
            ui.setText('exchange_rate_qr', payment.formatDecimal(run['effective_rate_btc'] / defaults.BITCOIN_SCALE_DIVIZER,
                                                                 defaults.EXCHANGE_RATE_DEC_PLACES))
            ui.setText('qr_address_lbl', run['transactions_addresses']['local'])
            ui.setImage("qr_image", run['qr_image_path'])
            run['keypad'].resetKey()

        elif run['keypad'].last_key_pressed == 'backspace':
            payment.clearPaymentRuntime(run, ui, clear_amounts=False)
            xbterminal.helpers.nfcpy.stop()
            return defaults.STAGES['payment']['enter_amount']
    
        if not xbterminal.helpers.nfcpy.is_active():
            xbterminal.helpers.nfcpy.start(run['transaction_bitcoin_uri'])
            logger.debug('nfc bitcoin URI activated: {}'.format(run['transaction_bitcoin_uri']))
            time.sleep(0.5)

        try:
            current_balance = xbterminal.blockchain.blockchain.getAddressBalance(run['transactions_addresses']['local'])
            if current_balance >= run['amounts']['amount_to_pay_btc']:
                incoming_tx_hash = xbterminal.blockchain.blockchain.getLastUnspentTransactionId(run['transactions_addresses']['local'])
        except Exception as error:
            pass

        if incoming_tx_hash is not None:
            logger.debug('payment received locally, incoming txid: {txid}'.format(txid=incoming_tx_hash))

            if current_balance > run['amounts']['amount_to_pay_btc']:
                run['amounts']['our_fee_btc_amount'] = run['amounts']['our_fee_btc_amount'] + current_balance - run['amounts']['amount_to_pay_btc'] #overpayment goes to our fee
            amounts = {'instantfiat': run['amounts']['instantfiat_btc_amount'],
                       'merchant': run['amounts']['merchants_btc_amount'],
                       'fee': run['amounts']['our_fee_btc_amount'],
                        }

            outgoing_tx_hash = payment.createOutgoingTransaction(addresses=run['transactions_addresses'],
                                                                amounts=amounts)
            logger.debug('payment forwarded, outgoing txid: {txid},'
                'addresses: {addresses},'
                'amounts: {amounts},'.format(txid=outgoing_tx_hash,
                                             amounts=amounts,
                                             addresses=run['transactions_addresses']))

            run['receipt_url'] = payment.logTransaction(
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

            run['qr_image_path'] = os.path.join(defaults.PROJECT_ABS_PATH, defaults.QR_IMAGE_PATH)
            xbterminal.helpers.qr.qr_gen(run['receipt_url'], run['qr_image_path'])

            payment.clearPaymentRuntime(run, ui)
            xbterminal.helpers.nfcpy.stop()
            return defaults.STAGES['payment']['pay_success']

        if run['last_activity_timestamp'] + defaults.TRANSACTION_TIMEOUT < time.time():
            payment.clearPaymentRuntime(run, ui)
            xbterminal.helpers.nfcpy.stop()
            run['last_activity_timestamp'] = (time.time()
                                                  - defaults.TRANSACTION_TIMEOUT
                                                  + defaults.TRANSACTION_CANCELLED_MESSAGE_TIMEOUT)
            return defaults.STAGES['payment']['pay_cancel']

        time.sleep(0.5)


def pay_success(run, ui):
    ui.showScreen('pay_success')
    ui.setImage("receipt_qr_image", run['qr_image_path'])
    while True:
        if not xbterminal.helpers.nfcpy.is_active():
            xbterminal.helpers.nfcpy.start(run['receipt_url'])
            logger.debug('nfc receipt URI activated: {}'.format(run['receipt_url']))
            time.sleep(0.5)
        if run['keypad'].last_key_pressed == 'enter':
            xbterminal.helpers.nfcpy.stop()
            return defaults.STAGES['payment']['enter_amount']
        elif run['keypad'].last_key_pressed == 'backspace':
            xbterminal.helpers.nfcpy.stop()
            return defaults.STAGES['idle']
        if run['last_activity_timestamp'] + defaults.TRANSACTION_TIMEOUT < time.time():
            xbterminal.helpers.nfcpy.stop()
            return defaults.STAGES['idle']
        time.sleep(0.1)


def pay_cancel(run, ui):
    ui.showScreen('pay_cancel')
    while True:
        if run['keypad'].last_key_pressed is not None:
            run['display_value_unformatted'] = ''
            run['display_value_formatted'] = payment.formatInput(run['display_value_unformatted'], defaults.OUTPUT_DEC_PLACES)
            ui.setText('amount_input', run['display_value_formatted'])
            return defaults.STAGES['payment']['enter_amount']
        if run['last_activity_timestamp'] + defaults.TRANSACTION_TIMEOUT < time.time():
            return defaults.STAGES['idle']
        time.sleep(0.1)


def choose_ssid(run, ui):
    ui.showScreen('choose_ssid')
    while True:
        if run['screen_buttons']['skip_wifi']:
            logger.warning('wifi setup cancelled, hoping for preconfigured wired connection')
            run['screen_buttons']['skip_wifi'] = False
            run['init']['internet'] = True
            return defaults.STAGES['bootup']

        if run['wifi']['networks_last_listed_timestamp'] + 30 < time.time():
            networks_list = xbterminal.helpers.wireless.discover_networks()
            run['wifi']['networks_last_listed_timestamp'] = time.time()
            run['wifi']['networks_list_length'] = len(networks_list)
            run['wifi']['networks_list_selected_index'] = 0
            ui.wifiListClear()
            for i, network in enumerate(networks_list):
                ui.wifiListAddItem(network['ssid'])
                if xbterminal.local_state.get('wifi_ssid') == network['ssid']:
                    run['wifi']['networks_list_selected_index'] = i
            ui.wifiListSelectItem(run['wifi']['networks_list_selected_index'])

        if run['keypad'].last_key_pressed == 8:
            run['wifi']['networks_list_selected_index'] = min(run['wifi']['networks_list_selected_index'] + 1,
                                                              run['wifi']['networks_list_length'] - 1)
            ui.wifiListSelectItem(run['wifi']['networks_list_selected_index'])
            run['keypad'].resetKey()
        elif run['keypad'].last_key_pressed == 2:
            run['wifi']['networks_list_selected_index'] = max(run['wifi']['networks_list_selected_index'] - 1, 0)
            ui.wifiListSelectItem(run['wifi']['networks_list_selected_index'])
            run['keypad'].resetKey()
        elif run['keypad'].last_key_pressed == 'enter':
            ui.wifiListSaveSelectedItem()
            while 'selected_ssid' not in run['wifi']:
                time.sleep(0.1)
            xbterminal.local_state['wifi_ssid'] = run['wifi'].pop('selected_ssid')
            xbterminal.helpers.configs.save_local_state()
            return defaults.STAGES['wifi']['enter_passkey']

        time.sleep(0.1)


def enter_passkey(run, ui):
    ui.showScreen('enter_passkey')
    ui.setText('ssid_entered_lbl', xbterminal.local_state['wifi_ssid'])
    xbterminal.local_state['wifi_pass'] = ''
    while True:
        if run['keypad'].last_key_pressed is not None:
            ui.toggleWifiWrongPasswordState(False)

            if run['keypad'].checkIsDone():
                ui.toggleWifiConnectingState(True)
                logger.debug('trying to connect to wifi, '
                    'ssid: "{ssid}", pass: "{passkey}" '.format(ssid=xbterminal.local_state['wifi_ssid'],
                                                                passkey=xbterminal.local_state['wifi_pass']))
                run['wifi']['connected'] = xbterminal.helpers.wireless.connect(xbterminal.local_state['wifi_ssid'],
                                                                               xbterminal.local_state['wifi_pass'])
                if run['wifi']['connected']:
                    run['init']['internet'] = True
                    logger.debug('connected to wifi, ssid: {ssid}'.format(ssid=xbterminal.local_state['wifi_ssid']))
                    xbterminal.helpers.configs.save_local_state()
                    return defaults.STAGES['wifi']['wifi_connected']
                else:
                    logger.warning('wifi wrong passkey')
                    ui.toggleWifiConnectingState(False)
                    ui.toggleWifiWrongPasswordState(True)
                    run['keypad'].resetKey()

            elif run['keypad'].checkIsCancelled(xbterminal.local_state['wifi_pass']):
                del xbterminal.local_state['wifi_ssid']
                del xbterminal.local_state['wifi_pass']
                xbterminal.helpers.configs.save_local_state()
                return defaults.STAGES['wifi']['choose_ssid']

            else:
                xbterminal.local_state['wifi_pass'] = run['keypad'].createAlphaNumString(xbterminal.local_state['wifi_pass'])
                char_selector_tupl = run['keypad'].getCharSelectorTupl()
                if char_selector_tupl is not None:
                    char_select_str = xbterminal.gui.gui.formatCharSelectHelperHMTL(char_selector_tupl,
                                                                     xbterminal.local_state['wifi_pass'][-1])
                else:
                    char_select_str = ''
                ui.setText('input_help_lbl', char_select_str)
                ui.setText('password_input', xbterminal.local_state['wifi_pass'])
                run['keypad'].resetKey()
        time.sleep(0.1)


def wifi_connected(run, ui):
    ui.showScreen('wifi_connected')
    time.sleep(3)
    return defaults.STAGES['bootup']
