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
    run['init']['blockchain'] = False
    run['init']['remote_config'] = False
    run['init']['remote_config_last_update'] = None
    run['init']['blockchain_network'] = None
    run['CURRENT_STAGE'] = defaults.STAGES['bootup']
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
    run['current_screen'] = None
    run['keypad'] = None

    qt_application, main_window = xbterminal.gui.gui.initGUI()
    main_window.advanceLoadingProgressBar(defaults.LOAD_PROGRESS_LEVELS['gui_init'])

    xbterminal.helpers.configs.load_local_state()
    if xbterminal.local_state.get('use_predefined_connection'):
        run['init']['internet'] = True
        logger.debug('!!! CUSTOM INTERNET CONNECTION OVERRIDE ACTIVE')
    main_window.advanceLoadingProgressBar(defaults.LOAD_PROGRESS_LEVELS['local_config_load'])

    run['keypad'] = Keypad()
    main_window.advanceLoadingProgressBar(defaults.LOAD_PROGRESS_LEVELS['keypad_init'])

    watcher = xbterminal.watcher.Watcher()
    watcher.start()

    worker = None
    worker_thread = None

    logger.debug('main loop starting')
    while True:
        time.sleep(0.05)

        # Processes all pending events
        try:
            qt_application.sendPostedEvents()
            qt_application.processEvents()
        except NameError as error:
            logger.exception(error)


        # Temporary solution for the freezing of terminal
        # Reboot once per hour
        if (
            run['init']['clock_synchronized']
            and run['CURRENT_STAGE'] == defaults.STAGES['idle']
            and time.time() - xbterminal.local_state['last_started'] > 3600
        ):
            gracefulExit(system_reboot=True)

        # Load remote config
        if run['init']['internet']:
            if (not run['init']['remote_config']
                or (run['init']['remote_config_last_update'] is not None
                    and run['init']['remote_config_last_update']+defaults.REMOTE_CONFIG_UPDATE_CYCLE < time.time())):
                try:
                    xbterminal.helpers.configs.load_remote_config()
                    main_window.setText('merchant_name_lbl', "{} \n{} ".format(xbterminal.remote_config['MERCHANT_NAME'],
                                                                   xbterminal.remote_config['MERCHANT_DEVICE_NAME'])) #trailing space required
                    run['init']['remote_config'] = True
                    run['init']['remote_config_last_update'] = int(time.time())
                except ConfigLoadError as error:
                    logger.error('remote config load failed, exiting')
                    raise error

        # Communicate with watcher
        watcher_messages, watcher_errors = watcher.get_data()
        for level, message in watcher_messages:
            logger.log(level, message)
        if watcher_errors:
            if main_window.currentScreen() != 'errors':
                # Show error screen
                run['current_screen'] = main_window.currentScreen()
                main_window.showScreen('errors')
                main_window.setText('errors_lbl', "\n".join(watcher_errors))
            continue
        else:
            if main_window.currentScreen() == 'errors' and run['current_screen'] is not None:
                # Restore previous screen
                main_window.showScreen(run['current_screen'])

        # Read keypad input
        run['keypad'].getKey()
        run['last_activity_timestamp'] = run['keypad'].last_activity_timestamp

        if run['keypad'].last_key_pressed == 'application_halt':
            gracefulExit()
        elif run['keypad'].last_key_pressed == 'system_halt':
            gracefulExit(system_halt=True)

        # Show blockchain network notice
        if hasattr(xbterminal, 'remote_config'):
            if run['init']['blockchain_network'] is None:
                if xbterminal.remote_config['BITCOIN_NETWORK'] == 'testnet':
                    main_window.toggleTestnetNotice(True)
                else:
                    main_window.toggleTestnetNotice(False)
                run['init']['blockchain_network'] = xbterminal.remote_config['BITCOIN_NETWORK']
            elif run['init']['blockchain_network'] != xbterminal.remote_config['BITCOIN_NETWORK']:
                gracefulExit(system_reboot=True)

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
