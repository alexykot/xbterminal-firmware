#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import time
import sys
import os
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
import xbterminal.gui.gui
import xbterminal.helpers.nfcpy
import xbterminal.helpers.configs
from xbterminal import defaults
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

        # Manage stages
        if hasattr(stages, run['CURRENT_STAGE']):
            next_stage = getattr(stages, run['CURRENT_STAGE'])(run)
            if next_stage is not None:
                if next_stage != run['CURRENT_STAGE']:
                    logger.debug("moving to stage {0}".format(next_stage))
                run['CURRENT_STAGE'] = next_stage
                continue

        # Inactivity state reset
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
