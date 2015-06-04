from decimal import Decimal
import logging
import os.path
import time
import unicodedata

logger = logging.getLogger(__name__)

import xbterminal
from xbterminal import defaults
from xbterminal.stages import amounts, payment, withdrawal

import xbterminal.helpers.bt
import xbterminal.helpers.camera
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
                    xbterminal.local_state['wifi_pass'] = unicodedata.normalize('NFKD', xbterminal.local_state['wifi_pass']).encode('ascii', 'ignore')
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

    run['init']['blockchain_network'] = xbterminal.remote_config['BITCOIN_NETWORK']
    logger.warning('working with {0}'.format(
        xbterminal.remote_config['BITCOIN_NETWORK']))

    # Initialize bluetooth and NFC servers
    run['bluetooth_server'] = xbterminal.helpers.bt.BluetoothServer()
    run['nfc_server'] = xbterminal.helpers.nfcpy.NFCServer()
    run['qr_scanner'] = xbterminal.helpers.camera.QRScanner(backend='fswebcam')

    return defaults.STAGES['idle']


def idle(run, ui):
    ui.showScreen('idle')
    while True:
        if run['screen_buttons']['pay']:
            run['screen_buttons']['pay'] = False
            run['payment']['fiat_amount'] = Decimal(0)
            return defaults.STAGES['payment']['pay_amount']
        if run['screen_buttons']['withdraw']:
            run['screen_buttons']['withdraw'] = False
            run['withdrawal']['fiat_amount'] = Decimal(0)
            return defaults.STAGES['withdrawal']['withdraw_amount']
        if run['keypad'].last_key_pressed is not None:
            run['payment']['fiat_amount'] = Decimal(0)
            if run['keypad'].last_key_pressed in range(10) + ['00']:
                run['payment']['fiat_amount'] = amounts.process_key_input(run['payment']['fiat_amount'], run['keypad'].last_key_pressed)
            return defaults.STAGES['payment']['pay_amount']
        time.sleep(0.1)


def pay_amount(run, ui):
    ui.showScreen('enter_amount')
    assert run['payment']['fiat_amount'] is not None
    ui.setText('amount_input', amounts.format_amount(run['payment']['fiat_amount']))
    while True:
        if (
            run['keypad'].last_key_pressed in range(10) + ['00']
            or run['keypad'].last_key_pressed == 'backspace'
        ):
            if run['keypad'].last_key_pressed == 'backspace' and run['payment']['fiat_amount'] == 0:
                return defaults.STAGES['idle']
            ui.toggleAmountErrorState(False)
            run['payment']['fiat_amount'] = amounts.process_key_input(run['payment']['fiat_amount'], run['keypad'].last_key_pressed)
            ui.setText('amount_input', amounts.format_amount(run['payment']['fiat_amount']))
        elif run['keypad'].last_key_pressed == 'enter':
            if run['payment']['fiat_amount'] > 0:
                return defaults.STAGES['payment']['pay_loading']
            else:
                ui.toggleAmountErrorState(True)
        if run['last_activity_timestamp'] + defaults.TRANSACTION_TIMEOUT < time.time():
            _clear_payment_runtime(run, ui)
            return defaults.STAGES['idle']
        run['keypad'].resetKey()
        time.sleep(0.1)


def pay_loading(run, ui):
    ui.showScreen('load_indefinite')

    if run['payment']['fiat_amount'] is None:
        return defaults.STAGES['payment']['pay_amount']

    while True:
        run['payment']['order'] = payment.Payment.create_order(run['payment']['fiat_amount'],
                                                               run['bluetooth_server'].mac_address)
        if run['payment']['order'] is not None:
            # Payment parameters loaded
            # Prepare QR image
            run['payment']['qr_image_path'] = defaults.QR_IMAGE_PATH
            xbterminal.helpers.qr.qr_gen(run['payment']['order'].payment_uri,
                                         run['payment']['qr_image_path'])
            return defaults.STAGES['payment']['pay_wait']
        else:
            # Network error
            time.sleep(1)


def pay_wait(run, ui):
    ui.showScreen('pay_wait')
    ui.setText('pwait_fiat_amount_lbl',
               amounts.format_amount(run['payment']['fiat_amount']))
    ui.setText('pwait_btc_amount_lbl',
               amounts.format_btc_amount(run['payment']['order'].btc_amount))
    ui.setText('pwait_xrate_amount_lbl',
               amounts.format_exchange_rate(run['payment']['order'].exchange_rate))
    ui.setImage('pwait_qr_img', run['payment']['qr_image_path'])
    logger.info(
        'local payment requested, '
        'amount fiat: {amount_fiat}, '
        'amount btc: {amount_btc}, '
        'rate: {effective_rate}'.format(
            amount_fiat=run['payment']['fiat_amount'],
            amount_btc=run['payment']['order'].btc_amount,
            effective_rate=run['payment']['order'].exchange_rate))
    logger.info('payment uri: {}'.format(run['payment']['order'].payment_uri))
    run['bluetooth_server'].start(run['payment']['order'])
    while True:
        if run['keypad'].last_key_pressed == 'backspace':
            _clear_payment_runtime(run, ui, clear_amounts=False)
            run['nfc_server'].stop()
            run['bluetooth_server'].stop()
            return defaults.STAGES['payment']['pay_amount']

        if not run['nfc_server'].is_active():
            run['nfc_server'].start(run['payment']['order'].payment_uri)
            time.sleep(0.5)

        run['payment']['receipt_url'] = run['payment']['order'].check()
        if run['payment']['receipt_url'] is not None:
            logger.debug('payment received, receipt: {}'.format(run['payment']['receipt_url']))

            run['payment']['qr_image_path'] = defaults.QR_IMAGE_PATH
            xbterminal.helpers.qr.qr_gen(run['payment']['receipt_url'],
                                         run['payment']['qr_image_path'])

            _clear_payment_runtime(run, ui)
            run['nfc_server'].stop()
            run['bluetooth_server'].stop()
            return defaults.STAGES['payment']['pay_success']

        if run['last_activity_timestamp'] + defaults.TRANSACTION_TIMEOUT < time.time():
            _clear_payment_runtime(run, ui)
            run['nfc_server'].stop()
            run['bluetooth_server'].stop()
            return defaults.STAGES['payment']['pay_cancel']

        time.sleep(0.5)


def pay_success(run, ui):
    ui.showScreen('pay_success')
    ui.setImage('psuccess_receipt_qr_img', run['payment']['qr_image_path'])
    while True:
        if not run['nfc_server'].is_active():
            run['nfc_server'].start(run['payment']['receipt_url'])
            time.sleep(0.5)
        if run['keypad'].last_key_pressed == 'enter':
            run['nfc_server'].stop()
            return defaults.STAGES['payment']['pay_amount']
        elif run['keypad'].last_key_pressed == 'backspace':
            run['nfc_server'].stop()
            return defaults.STAGES['idle']
        if run['last_activity_timestamp'] + defaults.TRANSACTION_TIMEOUT < time.time():
            run['nfc_server'].stop()
            return defaults.STAGES['idle']
        time.sleep(0.1)


def pay_cancel(run, ui):
    ui.showScreen('pay_cancel')
    while True:
        if run['keypad'].last_key_pressed is not None:
            _clear_payment_runtime(run, ui, clear_amounts=False)
            return defaults.STAGES['payment']['pay_amount']
        if run['last_activity_timestamp'] + defaults.TRANSACTION_TIMEOUT < time.time():
            return defaults.STAGES['idle']
        time.sleep(0.1)


def withdraw_amount(run, ui):
    ui.showScreen('enter_amount')
    assert run['withdrawal']['fiat_amount'] is not None
    ui.setText('amount_input', amounts.format_amount(run['withdrawal']['fiat_amount']))
    while True:
        if (
            run['keypad'].last_key_pressed in range(10) + ['00']
            or run['keypad'].last_key_pressed == 'backspace'
        ):
            if run['keypad'].last_key_pressed == 'backspace' and run['withdrawal']['fiat_amount'] == 0:
                _clear_withdrawal_runtime(run, ui)
                return defaults.STAGES['idle']
            ui.toggleAmountErrorState(False)
            run['withdrawal']['fiat_amount'] = amounts.process_key_input(run['withdrawal']['fiat_amount'], run['keypad'].last_key_pressed)
            ui.setText('amount_input', amounts.format_amount(run['withdrawal']['fiat_amount']))
        elif run['keypad'].last_key_pressed == 'enter':
            if run['withdrawal']['fiat_amount'] > 0:
                return defaults.STAGES['withdrawal']['withdraw_loading1']
            else:
                ui.toggleAmountErrorState(True)
        if run['last_activity_timestamp'] + defaults.TRANSACTION_TIMEOUT < time.time():
            _clear_withdrawal_runtime(run, ui)
            return defaults.STAGES['idle']
        run['keypad'].resetKey()
        time.sleep(0.1)


def withdraw_loading1(run, ui):
    ui.showScreen('load_indefinite')
    assert run['withdrawal']['fiat_amount'] > 0
    while True:
        # TODO: get rates from server
        run['withdrawal']['order'] = {
            'btc_amount': defaults.BTC_DEC_PLACES,
            'exchange_rate': defaults.BTC_DEC_PLACES,
        }
        # TODO: loading timeout
        if run['withdrawal']['order'] is not None:
            return defaults.STAGES['withdrawal']['withdraw_scan']
        else:
            _clear_withdrawal_runtime(run, ui, clear_amounts=False)
            return defaults.STAGES['withdrawal']['withdraw_amount']


def withdraw_scan(run, ui):
    ui.showScreen('withdraw_scan')
    assert run['withdrawal']['order'] is not None
    ui.setText('wscan_fiat_amount_lbl', amounts.format_amount(run['withdrawal']['fiat_amount']))
    ui.setText('wscan_btc_amount_lbl', amounts.format_btc_amount(run['withdrawal']['order']['btc_amount']))
    ui.setText('wscan_xrate_amount_lbl', amounts.format_exchange_rate(run['withdrawal']['order']['exchange_rate']))
    run['qr_scanner'].start()
    while True:
        address = withdrawal.get_bitcoin_address(
            run['qr_scanner'].get_data() or '')
        if address:
            logger.debug('address scanned: {0}'.format(address))
            run['qr_scanner'].stop()
            run['withdrawal']['address'] = address
            return defaults.STAGES['withdrawal']['withdraw_confirm']
        if run['keypad'].last_key_pressed == 'backspace':
            run['qr_scanner'].stop()
            _clear_withdrawal_runtime(run, ui, clear_amounts=False)
            return defaults.STAGES['withdrawal']['withdraw_amount']
        if run['last_activity_timestamp'] + defaults.TRANSACTION_TIMEOUT < time.time():
            run['qr_scanner'].stop()
            _clear_withdrawal_runtime(run, ui)
            return defaults.STAGES['idle']
        time.sleep(0.1)


def withdraw_confirm(run, ui):
    ui.showScreen('withdraw_confirm')
    assert run['withdrawal']['address'] is not None
    ui.setText('wconfirm_address_lbl', run['withdrawal']['address'])
    ui.setText('wconfirm_fiat_amount_lbl', amounts.format_amount(run['withdrawal']['fiat_amount']))
    ui.setText('wconfirm_btc_amount_lbl', amounts.format_btc_amount(run['withdrawal']['order']['btc_amount']))
    ui.setText('wconfirm_xrate_amount_lbl', amounts.format_exchange_rate(run['withdrawal']['order']['exchange_rate']))
    while True:
        if run['screen_buttons']['confirm_withdrawal']:
            run['screen_buttons']['confirm_withdrawal'] = False
            return defaults.STAGES['withdrawal']['withdraw_loading2']
        if run['keypad'].last_key_pressed == 'enter':
            return defaults.STAGES['withdrawal']['withdraw_loading2']
        elif run['keypad'].last_key_pressed == 'backspace':
            _clear_withdrawal_runtime(run, ui, clear_amounts=False)
            return defaults.STAGES['withdrawal']['withdraw_amount']
        if run['last_activity_timestamp'] + defaults.TRANSACTION_TIMEOUT < time.time():
            _clear_withdrawal_runtime(run, ui)
            return defaults.STAGES['idle']
        time.sleep(0.1)


def withdraw_loading2(run, ui):
    ui.showScreen('load_indefinite')
    assert run['withdrawal']['address'] is not None
    while True:
        # TODO: get receipt from the server
        run['withdrawal']['receipt_url'] = 'https://xbterminal.io/rc/CV2ALZ'
        # TODO: loading timeout
        if run['withdrawal']['receipt_url'] is not None:
            run['withdrawal']['qr_image_path'] = defaults.QR_IMAGE_PATH
            xbterminal.helpers.qr.qr_gen(run['withdrawal']['receipt_url'],
                                         run['withdrawal']['qr_image_path'])
            return defaults.STAGES['withdrawal']['withdraw_success']
        else:
            _clear_withdrawal_runtime(run, ui, clear_amounts=False)
            return defaults.STAGES['withdrawal']['withdraw_amount']


def withdraw_success(run, ui):
    ui.showScreen('withdraw_success')
    assert run['withdrawal']['qr_image_path'] is not None
    ui.setImage('wsuccess_receipt_qr_img', run['withdrawal']['qr_image_path'])
    while True:
        if run['keypad'].last_key_pressed in ['backspace', 'enter']:
            _clear_withdrawal_runtime(run, ui)
            return defaults.STAGES['idle']
        if run['last_activity_timestamp'] + defaults.TRANSACTION_TIMEOUT < time.time():
            _clear_withdrawal_runtime(run, ui)
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


def _clear_payment_runtime(run, ui, clear_amounts=True):
    ui.showScreen('load_indefinite')
    logger.debug('clearing payment runtime')
    if clear_amounts:
        run['payment']['fiat_amount'] = Decimal(0)
        ui.setText('amount_input', amounts.format_amount(Decimal(0)))

    run['payment']['order'] = None

    ui.setText('pwait_fiat_amount_lbl',
               amounts.format_amount(Decimal(0)))
    ui.setText('pwait_btc_amount_lbl',
               amounts.format_btc_amount(Decimal(0)))
    ui.setText('pwait_xrate_amount_lbl',
               amounts.format_exchange_rate(Decimal(0)))
    ui.setImage('pwait_qr_img', None)
    ui.setImage('psuccess_receipt_qr_img', None)


def _clear_withdrawal_runtime(run, ui, clear_amounts=True):
    logger.debug('clearing withdrawal runtime')
    ui.showScreen('load_indefinite')

    if clear_amounts:
        run['withdrawal']['fiat_amount'] = None
        ui.setText('amount_input', amounts.format_amount(Decimal(0)))

    run['withdrawal']['order'] = None
    run['withdrawal']['address'] = None
    run['withdrawal']['receipt_url'] = None
    run['withdrawal']['qr_image_path'] = None

    ui.setText('wscan_fiat_amount_lbl',
               amounts.format_amount(Decimal(0)))
    ui.setText('wscan_btc_amount_lbl',
               amounts.format_btc_amount(Decimal(0)))
    ui.setText('wscan_xrate_amount_lbl',
               amounts.format_exchange_rate(Decimal(0)))
    ui.setText('wconfirm_fiat_amount_lbl',
               amounts.format_amount(Decimal(0)))
    ui.setText('wconfirm_btc_amount_lbl',
               amounts.format_btc_amount(Decimal(0)))
    ui.setText('wconfirm_xrate_amount_lbl',
               amounts.format_exchange_rate(Decimal(0)))
    ui.setImage('wsuccess_receipt_qr_img', None)
