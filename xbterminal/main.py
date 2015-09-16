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
    return {
        'device_key': None,
        'batch_number': None,
        'local_config': {},
        'remote_server': None,
        'remote_config': {},
        'last_activity_timestamp': None,
        'keypad': None,
        'keyboard_events': deque(maxlen=1),  # Only for keyboard driver
        'bluetooth_server': None,
        'nfc_server': None,
        'qr_scanner': None,
        'screen_buttons': {
            # Button states
            'skip_wifi': False,
            'pay': False,
            'withdraw': False,
            'confirm_withdrawal': False,
        },
        'init': {
            'clock_synchronized': False,
            'remote_config': False,
            'remote_config_last_update': 0,
        },
        'CURRENT_STAGE': defaults.STAGES['bootup'],
        'payment': {
            # Variables related to payment process
            'fiat_amount': None,
            'order': None,
            'qr_image_path': None,
            'receipt_url': None,
        },
        'withdrawal': {
            # Variables related to withdrawal process
            'fiat_amount': None,
            'order': None,
            'address': None,
            'receipt_url': None,
            'qr_image_path': None,
        },
    }


def main():
    logging.config.dictConfig(xbterminal.defaults.LOG_CONFIG)
    logger.debug('starting')

    run = xbterminal.runtime = get_initial_state()

    run['local_config'] = xbterminal.helpers.configs.load_local_config()

    if run['local_config'].get('use_dev_remote_server'):
        run['remote_server'] = xbterminal.defaults.REMOTE_SERVERS['dev']
        logger.warning('!!! DEV SERVER OVERRRIDE ACTIVE')
    else:
        run['remote_server'] = xbterminal.defaults.REMOTE_SERVERS['main']
    logger.info('remote server {}'.format(run['remote_server']))

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
        if watcher.internet and \
                run['device_key'] and \
                run['init']['remote_config_last_update'] + defaults.REMOTE_CONFIG_UPDATE_CYCLE < time.time():
            try:
                run['remote_config'] = xbterminal.helpers.configs.load_remote_config()
            except ConfigLoadError as error:
                # No remote config available, stop
                logger.exception(error)
                break
            else:
                run['init']['remote_config'] = True
                run['init']['remote_config_last_update'] = int(time.time())
                main_window.retranslateUi(
                    run['remote_config']['language']['code'],
                    run['remote_config']['currency']['prefix'])

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
