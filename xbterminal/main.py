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
import xbterminal.gui.gui
import xbterminal.helpers.configs
from xbterminal import defaults
from xbterminal.stages.worker import StageWorker, move_to_thread
from xbterminal.stages.init import init_step_1
from xbterminal.state import state

logger = logging.getLogger(__name__)


def main():
    logging.config.dictConfig(xbterminal.defaults.LOG_CONFIG)
    logger.debug('starting')

    init_step_1(state)

    main_window = xbterminal.gui.gui.GUI()
    worker = None
    worker_thread = None
    run = state

    logger.debug('main loop starting')
    while True:
        time.sleep(0.05)

        main_window.processEvents()

        # Check for errors
        watcher_errors = run['watcher'].get_errors()
        if watcher_errors:
            main_window.showErrors(watcher_errors)
            continue
        else:
            main_window.hideErrors()

        # Reload remote config
        if run['init']['registration'] and \
                run['remote_config_last_update'] + defaults.REMOTE_CONFIG_UPDATE_CYCLE < time.time():
            run['remote_config'] = xbterminal.helpers.configs.load_remote_config()
            run['remote_config_last_update'] = int(time.time())
            main_window.retranslateUi(
                run['remote_config']['language']['code'],
                run['remote_config']['currency']['prefix'])

        # Read keypad input
        run['keypad'].getKey()
        if run['last_activity_timestamp'] < run['keypad'].last_activity_timestamp:
            run['last_activity_timestamp'] = run['keypad'].last_activity_timestamp

        if run['keypad'].last_key_pressed == 'application_halt':
            break

        # Manage stages
        if run['CURRENT_STAGE'] == 'application_halt':
            break
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
