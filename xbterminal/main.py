#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import time
import sys
import os
import logging.config
import signal

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
from xbterminal.state import state

logger = logging.getLogger(__name__)


def init(state):
    state['device_key'] = xbterminal.helpers.configs.read_device_key()
    state['local_config'] = xbterminal.helpers.configs.load_local_config()

    remote_server_name = state['local_config'].get('remote_server', 'prod')
    state['remote_server'] = xbterminal.defaults.REMOTE_SERVERS[remote_server_name]
    logger.info('remote server {}'.format(state['remote_server']))

    state['keypad'] = Keypad()

    state['watcher'] = xbterminal.watcher.Watcher()
    state['watcher'].start()


def main():
    logging.config.dictConfig(xbterminal.defaults.LOG_CONFIG)
    logger.debug('starting')

    init(state)

    main_window = xbterminal.gui.gui.initGUI()
    worker = None
    worker_thread = None
    run = state

    logger.debug('main loop starting')
    while True:
        time.sleep(0.05)

        main_window.processEvents()

        # (Re)load remote config
        if run['watcher'].internet and \
                run['init']['registration'] and \
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
        watcher_errors = run['watcher'].get_errors()
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
            graceful_exit()

        # Manage stages
        if run['CURRENT_STAGE'] == 'application_halt':
            graceful_exit()
        if worker_thread is None:
            worker = StageWorker(run['CURRENT_STAGE'], run)
            worker.ui.signal.connect(main_window.stageWorkerSlot)
            worker_thread = move_to_thread(worker)
        elif not worker_thread.is_alive():
            if worker.next_stage is not None:
                run['CURRENT_STAGE'] = worker.next_stage
            worker_thread = None
            run['keypad'].resetKey()


def sighup_handler(*args):
    state['local_config'] = xbterminal.helpers.configs.load_local_config()

signal.signal(signal.SIGHUP, sighup_handler)


def graceful_exit():
    xbterminal.helpers.configs.save_local_config(
        state['local_config'])
    logger.warning('application halted')
    sys.exit()


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        logger.exception(error)
    graceful_exit()
