#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import time
import sys
import os
import logging.config
import subprocess
from collections import deque

include_path = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, include_path)

import xbterminal
import xbterminal.defaults
from xbterminal.exceptions import ConfigLoadError
from xbterminal.keypad.keypad import Keypad
import xbterminal.gui.gui
import xbterminal.helpers.configs
from xbterminal import defaults
from xbterminal.stages.worker import StageWorker, move_to_thread
import xbterminal.watcher

logger = logging.getLogger(__name__)


def get_initial_state():
    run = {}
    run['init'] = {}
    run['init']['internet'] = False
    run['init']['clock_synchronized'] = False
    run['init']['remote_config'] = False
    run['init']['remote_config_last_update'] = 0
    run['init']['blockchain_network'] = None
    run['CURRENT_STAGE'] = defaults.STAGES['bootup']
    run['payment'] = {
        # Store variables related to payment process
        'fiat_amount': None,
        'order': None,
        'qr_image_path': None,
        'receipt_url': None,
    }
    run['withdrawal'] = {
        # Variables related to withdrawal process
        'fiat_amount': None,
        'order': None,
        'address': None,
        'receipt_url': None,
        'qr_image_path': None,
    }
    run['screen_buttons'] = {
        # Store button states
        'skip_wifi': False,
        'pay': False,
        'withdraw': False,
        'confirm_withdrawal': False,
    }
    run['device_key'] = None
    run['local_config'] = {}
    run['remote_server'] = None
    run['remote_config'] = {}
    run['last_activity_timestamp'] = None
    run['wifi'] = {}
    run['wifi']['connected'] = False
    run['keypad'] = None
    run['keyboard_events'] = deque(maxlen=1)  # Only for keyboard driver
    run['bluetooth_server'] = None
    run['nfc_server'] = None
    run['qr_scanner'] = None
    return run


def main():
    logging.config.dictConfig(xbterminal.defaults.LOG_CONFIG)
    logger.debug('starting')

    run = xbterminal.runtime = get_initial_state()

    run['device_key'] = xbterminal.helpers.configs.get_device_key()
    logger.info('device key {}'.format(run['device_key']))

    run['local_config'] = xbterminal.helpers.configs.load_local_config()

    if run['local_config'].get('use_dev_remote_server'):
        run['remote_server'] = xbterminal.defaults.REMOTE_SERVERS['dev']
        logger.warning('!!! DEV SERVER OVERRRIDE ACTIVE')
    else:
        run['remote_server'] = xbterminal.defaults.REMOTE_SERVERS['main']
    logger.info('remote server: {}'.format(run['remote_server']))

    if run['local_config'].get('use_predefined_connection'):
        run['init']['internet'] = True
        logger.debug('!!! CUSTOM INTERNET CONNECTION OVERRIDE ACTIVE')

    main_window = xbterminal.gui.gui.initGUI()

    run['keypad'] = Keypad()

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
                run['remote_config'] = xbterminal.helpers.configs.load_remote_config()
            except ConfigLoadError as error:
                # Do not raise error, wait for internet connection
                watcher.set_error('remote_config', 'remote config load failed')
            else:
                run['init']['remote_config'] = True
                run['init']['remote_config_last_update'] = int(time.time())
                watcher.discard_error('remote_config')
                main_window.retranslateUi(
                    run['remote_config']['MERCHANT_LANGUAGE'],
                    run['remote_config']['MERCHANT_CURRENCY_SIGN_PREFIX'])

        # Reboot if blockchain network has changed
        if (
            run['init']['remote_config']
            and run['init']['blockchain_network'] is not None
            and run['init']['blockchain_network'] != run['remote_config']['BITCOIN_NETWORK']
        ):
            gracefulExit(system_reboot=True)

        # Communicate with watcher
        watcher_errors = watcher.get_errors()
        if watcher_errors:
            main_window.showErrors(watcher_errors)
            continue
        else:
            main_window.hideErrors()

        # Read keypad input
        run['keypad'].getKey()
        if run['last_activity_timestamp'] < run['keypad'].last_activity_timestamp:
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
    xbterminal.helpers.configs.save_local_config(
        xbterminal.runtime['local_config'])
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
