#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import time
import sys
import os
import logging.config

include_path = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, include_path)

from xbterminal.gui import settings
from xbterminal.gui.rpc_client import JSONRPCClient
from xbterminal.gui.gui import GUI
from xbterminal.gui.worker import StageWorker, move_to_thread
from xbterminal.gui.state import state

logger = logging.getLogger(__name__)


def main():
    logging.config.dictConfig(settings.LOG_CONFIG)
    logger.debug('starting')

    state['client'] = JSONRPCClient()

    main_window = GUI()
    worker = None
    worker_thread = None

    logger.debug('main loop starting')
    while True:
        time.sleep(settings.MAIN_LOOP_PERIOD)

        main_window.processEvents()

        # Check for errors
        try:
            connection_status = state['client'].get_connection_status()
        except:
            connection_status = 'offline'
        if connection_status != 'online':
            main_window.showConnectionError()
            continue
        else:
            main_window.hideConnectionError()

        # Reload remote config
        if state['remote_config_last_update'] + \
                settings.REMOTE_CONFIG_UPDATE_CYCLE < time.time():
            state['remote_config'] = state['client'].get_device_config()
            state['remote_config_last_update'] = int(time.time())
            main_window.retranslateUi(
                state['remote_config']['language']['code'],
                state['remote_config']['currency']['prefix'])

        # Read keypad input
        state['keypad'].get_key()
        if state['last_activity_timestamp'] < state['keypad'].last_activity_timestamp:
            state['last_activity_timestamp'] = state['keypad'].last_activity_timestamp

        if state['keypad'].last_key_pressed == 'application_halt':
            main_window.close()
            break

        # Manage stages
        if state['CURRENT_STAGE'] == 'application_halt':
            main_window.close()
            break
        if worker_thread is None:
            worker = StageWorker(state['CURRENT_STAGE'], state)
            worker.ui.signal.connect(main_window.stageWorkerSlot)
            worker_thread = move_to_thread(worker)
        elif not worker_thread.is_alive():
            if worker.next_stage is not None:
                state['CURRENT_STAGE'] = worker.next_stage
            worker_thread = None
            state['keypad'].reset_key()


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        logger.exception(error)
    logger.warning('application halted')
