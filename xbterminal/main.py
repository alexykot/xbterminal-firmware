#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import time
import sys
import os
import logging.config
import subprocess

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
import xbterminal.helpers.configs
from xbterminal import defaults
from xbterminal.stages.worker import StageWorker, move_to_thread
import xbterminal.watcher


def main():
    logger.debug('starting')
    #init runtime
    run = xbterminal.runtime = {}
    run['init'] = {}
    run['init']['internet'] = False
    run['init']['clock_synchronized'] = False
    run['init']['remote_config'] = False
    run['init']['remote_config_last_update'] = 0
    run['init']['blockchain_network'] = None
    run['CURRENT_STAGE'] = defaults.STAGES['bootup']
    run['payment'] = None
    run['amounts'] = {}
    run['amounts']['amount_to_pay_fiat'] = None
    run['amounts']['amount_to_pay_btc'] = None
    run['screen_buttons'] = {}
    run['screen_buttons']['qr_button'] = False
    run['screen_buttons']['skip_wifi'] = False
    run['last_activity_timestamp'] = None
    run['current_text_piece'] = 'decimal'
    run['display_value_unformatted'] = ''
    run['display_value_formatted'] = ''
    run['wifi'] = {}
    run['wifi']['connected'] = False
    run['current_screen'] = 'load_indefinite'
    run['keypad'] = None
    run['bluetooth_server'] = None

    xbterminal.helpers.configs.load_local_state()
    if xbterminal.local_state.get('use_predefined_connection'):
        run['init']['internet'] = True
        logger.debug('!!! CUSTOM INTERNET CONNECTION OVERRIDE ACTIVE')

    main_window = xbterminal.gui.gui.initGUI()
    main_window.advanceLoadingProgressBar(defaults.LOAD_PROGRESS_LEVELS['gui_init'])

    run['keypad'] = Keypad()
    main_window.advanceLoadingProgressBar(defaults.LOAD_PROGRESS_LEVELS['keypad_init'])

    watcher = xbterminal.watcher.Watcher()
    watcher.start()

    worker = None
    worker_thread = None

    logger.debug('main loop starting')
    while True:
        time.sleep(0.05)

        main_window.processEvents()

        # (Re)load remote config
        if (
            run['init']['internet']
            and run['init']['remote_config_last_update'] + defaults.REMOTE_CONFIG_UPDATE_CYCLE < time.time()
        ):
            try:
                xbterminal.helpers.configs.load_remote_config()
            except ConfigLoadError as error:
                # Do not raise error, wait for internet connection
                watcher.set_error('remote_config', 'remote config load failed')
            else:
                run['init']['remote_config'] = True
                run['init']['remote_config_last_update'] = int(time.time())
                watcher.discard_error('remote_config')
                main_window.setText('merchant_name_lbl', "{} \n{} ".format(  # trailing space required
                    xbterminal.remote_config['MERCHANT_NAME'],
                    xbterminal.remote_config['MERCHANT_DEVICE_NAME']))
                main_window.retranslateUi(
                    xbterminal.remote_config['MERCHANT_LANGUAGE'],
                    xbterminal.remote_config['MERCHANT_CURRENCY_SIGN_PREFIX'])

        # Reboot if blockchain network has changed
        if (
            run['init']['remote_config']
            and run['init']['blockchain_network'] is not None
            and run['init']['blockchain_network'] != xbterminal.remote_config['BITCOIN_NETWORK']
        ):
            gracefulExit(system_reboot=True)

        # Communicate with watcher
        watcher_errors = watcher.get_errors()
        if watcher_errors:
            # Show error screen
            if main_window.currentScreen() != 'errors':
                run['current_screen'] = main_window.currentScreen()
                main_window.showScreen('errors')
            main_window.setText('errors_lbl', '\n'.join(watcher_errors))
            continue
        else:
            if main_window.currentScreen() == 'errors':
                # Restore previous screen
                main_window.showScreen(run['current_screen'])

        # Read keypad input
        run['keypad'].getKey()
        run['last_activity_timestamp'] = run['keypad'].last_activity_timestamp

        if run['keypad'].last_key_pressed == 'application_halt':
            gracefulExit()
        elif run['keypad'].last_key_pressed == 'system_halt':
            gracefulExit(system_halt=True)

        # Manage stages
        if worker_thread is None:
            worker = StageWorker(run['CURRENT_STAGE'], run)
            worker.ui.signal.connect(main_window.stageWorkerSlot)
            worker_thread = move_to_thread(worker)
        elif not worker_thread.is_alive():
            if worker.next_stage is not None:
                run['CURRENT_STAGE'] = worker.next_stage
            worker_thread = None
            run['keypad'].resetKey()


def gracefulExit(system_halt=False, system_reboot=False):
    xbterminal.helpers.configs.save_local_state()
    logger.debug('application halted')
    if system_halt:
        logger.debug('system halt command sent')
        subprocess.Popen(['halt', ])
    if system_reboot:
        logger.debug('system reboot command sent')
        subprocess.Popen(['reboot', ])
    sys.exit()


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        logger.exception(error)
    gracefulExit()
