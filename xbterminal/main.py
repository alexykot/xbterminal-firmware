#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
from decimal import Decimal
import time
import sys
import os
import unicodedata
import logging.config

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
import xbterminal.gui.gui
import xbterminal.helpers.nfcpy
import xbterminal.helpers.qr
import xbterminal.helpers.configs
import xbterminal.helpers.wireless
from xbterminal import defaults
from xbterminal.blockchain import blockchain
from xbterminal.stages import stages, payment
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
    run['pay_with'] = 'nfc'
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
    run['current_screen'] = None
    run['main_window'] = None
    run['keypad'] = None

    qt_application, run['main_window'] = xbterminal.gui.gui.initGUI()
    run['main_window'].advanceLoadingProgressBar(defaults.LOAD_PROGRESS_LEVELS['gui_init'])

    xbterminal.helpers.configs.load_local_state()
    if xbterminal.local_state.get('use_predefined_connection'):
        run['init']['internet'] = True
        logger.debug('!!! CUSTOM INTERNET CONNECTION OVERRIDE ACTIVE')
    run['main_window'].advanceLoadingProgressBar(defaults.LOAD_PROGRESS_LEVELS['local_config_load'])

    run['keypad'] = Keypad()
    run['main_window'].advanceLoadingProgressBar(defaults.LOAD_PROGRESS_LEVELS['keypad_init'])

    watcher = xbterminal.watcher.Watcher()
    watcher.start()

    xbterminal.local_state['last_started'] = time.time()
    xbterminal.helpers.configs.save_local_state() #@TODO make local_state a custom dict with automated saving on update and get rid of this call

    logger.debug('main loop starting')
    while True:
        # Processes all pending events
        try:
            qt_application.sendPostedEvents()
            qt_application.processEvents()
        except NameError as error:
            logger.exception(error)

        # Communicate with watcher
        watcher_messages, watcher_errors = watcher.get_data()
        for level, message in watcher_messages:
            logger.log(level, message)
        if watcher_errors:
            if run['main_window'].currentScreen() != 'errors':
                # Show error screen
                run['current_screen'] = run['main_window'].currentScreen()
                run['main_window'].showScreen('errors')
                run['main_window'].setText('errors_lbl', "\n".join(watcher_errors))
            continue
        else:
            if run['main_window'].currentScreen() == 'errors' and run['current_screen'] is not None:
                # Restore previous screen
                run['main_window'].showScreen(run['current_screen'])

        # Read keypad input
        if run['keypad'].last_key_pressed is not None:
            time.sleep(0.1)

        run['keypad'].resetKey()
        try:
            run['keypad'].getKey()
            if run['keypad'].last_key_pressed is not None:
                if run['keypad'].last_key_pressed == 'application_halt':
                    run['CURRENT_STAGE'] = defaults.STAGES['application_halt']
                if run['keypad'].last_key_pressed == 'system_halt':
                    run['CURRENT_STAGE'] = defaults.STAGES['system_halt']
                run['last_activity_timestamp'] = time.time()
        except NameError as error:
            logger.exception(error)

        # Load remote config
        if run['init']['internet']:
            if (not run['init']['remote_config']
                or (run['init']['remote_config_last_update'] is not None
                    and run['init']['remote_config_last_update']+defaults.REMOTE_CONFIG_UPDATE_CYCLE < time.time())):
                try:
                    xbterminal.helpers.configs.load_remote_config()
                    run['main_window'].setText('merchant_name_lbl', "{} \n{} ".format(xbterminal.remote_config['MERCHANT_NAME'],
                                                                   xbterminal.remote_config['MERCHANT_DEVICE_NAME'])) #trailing space required
                    run['init']['remote_config'] = True
                    run['init']['remote_config_last_update'] = int(time.time())
                except ConfigLoadError as error:
                    logger.error('remote config load failed, exiting')
                    raise error
                continue

        # Show blockchain network notice
        if hasattr(xbterminal, 'remote_config'):
            if run['init']['blockchain_network'] is None:
                if xbterminal.remote_config['BITCOIN_NETWORK'] == 'testnet':
                    run['main_window'].toggleTestnetNotice(True)
                else:
                    run['main_window'].toggleTestnetNotice(False)
                run['init']['blockchain_network'] = xbterminal.remote_config['BITCOIN_NETWORK']
            elif run['init']['blockchain_network'] != xbterminal.remote_config['BITCOIN_NETWORK']:
                payment.gracefullExit(system_reboot=True)

### NEW STAGES
        if hasattr(stages, run['CURRENT_STAGE']):
            logger.debug("moving to stage {0}".format(run['CURRENT_STAGE']))
            next_stage = getattr(stages, run['CURRENT_STAGE'])(run)
            if next_stage is not None:
                run['CURRENT_STAGE'] = next_stage
                continue

###PAY SUCCESS
        elif run['CURRENT_STAGE'] == defaults.STAGES['payment']['pay_success']:
            if not run['stage_init']:
                run['main_window'].showScreen('pay_success')
                if run['receipt_url'] is not None:
                    image_path = os.path.join(defaults.PROJECT_ABS_PATH, defaults.QR_IMAGE_PATH)
                    xbterminal.helpers.qr.qr_gen(run['receipt_url'], image_path)
                    run['main_window'].setImage("receipt_qr_image", image_path)
                    if not xbterminal.helpers.nfcpy.is_active():
                        xbterminal.helpers.nfcpy.start(run['receipt_url'])
                        logger.debug('nfc receipt URI activated: {}'.format(run['receipt_url']))
                        time.sleep(0.5)
                run['stage_init'] = True
                continue

            if run['keypad'].last_key_pressed == 'enter':
                xbterminal.helpers.nfcpy.stop()
                run['stage_init'] = False
                run['CURRENT_STAGE'] = defaults.STAGES['payment']['enter_amount']
                continue
            if run['keypad'].last_key_pressed == 'backspace':
                xbterminal.helpers.nfcpy.stop()
                run['stage_init'] = False
                run['CURRENT_STAGE'] = defaults.STAGES['idle']
                continue

###PAY CANCEL
        elif run['CURRENT_STAGE'] == defaults.STAGES['payment']['pay_cancel']:
            if not run['stage_init']:
                run['main_window'].showScreen('pay_cancel')
                run['stage_init'] = True
                continue

            if run['keypad'].last_key_pressed is not None:
                run['display_value_unformatted'] = ''
                run['display_value_formatted'] = payment.formatInput(run['display_value_unformatted'], defaults.OUTPUT_DEC_PLACES)
                run['main_window'].setText('amount_input', run['display_value_formatted'])

                run['main_window'].showScreen('pay_cancel')
                run['stage_init'] = False
                run['CURRENT_STAGE'] = defaults.STAGES['payment']['enter_amount']
                continue

###CHOOSE SSID
        elif run['CURRENT_STAGE'] == defaults.STAGES['wifi']['choose_ssid']:
            if not run['stage_init']:
                run['main_window'].showScreen('choose_ssid')
                run['stage_init'] = True

            if run['screen_buttons']['skip_wifi']:
                logger.warning('wifi setup cancelled, hoping for preconfigured wired connection')
                run['screen_buttons']['skip_wifi'] = False
                run['stage_init'] = False
                run['init']['internet'] = True
                run['CURRENT_STAGE'] = defaults.STAGES['bootup']
                continue

            if run['wifi']['networks_last_listed_timestamp'] + 30 < time.time():
                networks_list = xbterminal.helpers.wireless.discover_networks()
                run['wifi']['networks_last_listed_timestamp'] = time.time()
                if run['wifi']['networks_list_length'] != len(networks_list):
                    run['wifi']['networks_list_length'] = len(networks_list)
                    run['main_window'].wifiListClear()
                    network_index = 0
                    for network in networks_list:
                        run['main_window'].wifiListAddItem(network['ssid'])
                        if ('wifi_ssid' in xbterminal.local_state
                            and xbterminal.local_state['wifi_ssid'] == network['ssid']):
                            run['wifi']['networks_list_selected_index'] = network_index
                        network_index = network_index + 1

            if run['keypad'].last_key_pressed is not None:
                if run['keypad'].last_key_pressed == 8:
                    run['wifi']['networks_list_selected_index'] = min(run['wifi']['networks_list_selected_index']+1,
                                                                      (run['wifi']['networks_list_length']-1))
                elif run['keypad'].last_key_pressed == 2:
                    run['wifi']['networks_list_selected_index'] = max(run['wifi']['networks_list_selected_index']-1, 0)
                elif run['keypad'].last_key_pressed == 'enter':
                    xbterminal.local_state['wifi_ssid'] = run['main_window'].wifiListGetSelectedItem()
                    xbterminal.helpers.configs.save_local_state()
                    run['stage_init'] = False
                    run['CURRENT_STAGE'] = defaults.STAGES['wifi']['enter_passkey']
                    continue

            run['main_window'].wifiListSelectItem(run['wifi']['networks_list_selected_index'])

###ENTER PASSKEY
        elif run['CURRENT_STAGE'] == defaults.STAGES['wifi']['enter_passkey']:
            if not run['stage_init']:
                run['main_window'].showScreen('enter_passkey')
                run['main_window'].setText('ssid_entered_lbl', xbterminal.local_state['wifi_ssid'])
                xbterminal.local_state['wifi_pass'] = ''
                run['stage_init'] = True

            if run['keypad'].last_key_pressed is not None:
                run['main_window'].toggleWifiWrongPasswordState(False)

                if run['keypad'].checkIsDone(run['keypad'].last_key_pressed):
                    run['wifi']['try_to_connect'] = True
                    run['main_window'].toggleWifiConnectingState(True)
                    continue
                elif run['keypad'].checkIsCancelled(xbterminal.local_state['wifi_pass'], run['keypad'].last_key_pressed):
                    del xbterminal.local_state['wifi_ssid']
                    del xbterminal.local_state['wifi_pass']
                    xbterminal.helpers.configs.save_local_state()
                    run['stage_init'] = False
                    run['CURRENT_STAGE'] = defaults.STAGES['wifi']['choose_ssid']
                    continue
                else:
                    xbterminal.local_state['wifi_pass'] = run['keypad'].createAlphaNumString(xbterminal.local_state['wifi_pass'],
                                                                                        run['keypad'].last_key_pressed)
                char_selector_tupl = run['keypad'].getCharSelectorTupl(run['keypad'].last_key_pressed)
                if char_selector_tupl is not None:
                    char_select_str = xbterminal.gui.gui.formatCharSelectHelperHMTL(char_selector_tupl,
                                                                     xbterminal.local_state['wifi_pass'][-1])
                else:
                    char_select_str = ''
                run['main_window'].setText('input_help_lbl', char_select_str)

                run['main_window'].setText('password_input', xbterminal.local_state['wifi_pass'])

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
                    run['stage_init'] = False
                    run['CURRENT_STAGE'] = defaults.STAGES['wifi']['wifi_connected']
                    continue
                else:
                    logger.debug('wifi wrong passkey')
                    run['main_window'].toggleWifiConnectingState(False)
                    run['main_window'].toggleWifiWrongPasswordState(True)


###WIFI CONNECTED
        elif run['CURRENT_STAGE'] == defaults.STAGES['wifi']['wifi_connected']:
            if not run['stage_init']:
                run['main_window'].showScreen('wifi_connected')
                run['stage_init'] = True
                continue

            time.sleep(3)
            run['stage_init'] = False
            run['CURRENT_STAGE'] = defaults.STAGES['bootup']
            continue

###APPLICATION HALT
        elif run['CURRENT_STAGE'] == defaults.STAGES['application_halt']:
            payment.gracefullExit()

###SYSTEM HALT
        elif run['CURRENT_STAGE'] == defaults.STAGES['system_halt']:
            payment.gracefullExit(True)

###INACTIVITY STATE RESET
        if (run['CURRENT_STAGE'] in defaults.STAGES['payment']
            and run['last_activity_timestamp'] + defaults.TRANSACTION_TIMEOUT < time.time()):

            payment.clearPaymentRuntime()
            xbterminal.helpers.nfcpy.stop()

            if run['CURRENT_STAGE'] == defaults.STAGES['payment']['pay']:
                run['last_activity_timestamp'] = (time.time()
                                                  - defaults.TRANSACTION_TIMEOUT
                                                  + defaults.TRANSACTION_CANCELLED_MESSAGE_TIMEOUT)
                run['stage_init'] = False
                run['CURRENT_STAGE'] = defaults.STAGES['payment']['pay_cancel']
                continue
            else:
                run['stage_init'] = False
                run['CURRENT_STAGE'] = defaults.STAGES['idle']
                continue

        time.sleep(0.1)


try:
    main()
except Exception as error:
    logger.exception(error)

payment.gracefullExit()
