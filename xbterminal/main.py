#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import time
import sys
import os
import logging.config

include_path = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, include_path)

from xbterminal import defaults
from xbterminal.api_client import JSONRPCClient
from xbterminal.gui.gui import GUI
from xbterminal.stages.worker import StageWorker, move_to_thread
from xbterminal.state import gui_state as run

logger = logging.getLogger(__name__)


def main():
    logging.config.dictConfig(defaults.LOG_CONFIG)
    logger.debug('starting')

    run['client'] = JSONRPCClient()

    main_window = GUI()
    worker = None
    worker_thread = None

    logger.debug('main loop starting')
    while True:
        time.sleep(0.05)

        main_window.processEvents()

        # Check for errors
        server_status = run['client'].get_connection_status()
        if server_status != 'online':
            main_window.showErrors(['internet disconnected'])
            continue
        else:
            main_window.hideErrors()

        # Reload remote config
        if run['remote_config_last_update'] + \
                defaults.REMOTE_CONFIG_UPDATE_CYCLE < time.time():
            run['remote_config'] = run['client'].get_device_config()
            run['remote_config_last_update'] = int(time.time())
            main_window.retranslateUi(
                run['remote_config']['language']['code'],
                run['remote_config']['currency']['prefix'])

        # Read keypad input
        run['keypad'].getKey()
        if run['last_activity_timestamp'] < run['keypad'].last_activity_timestamp:
            run['last_activity_timestamp'] = run['keypad'].last_activity_timestamp

        if run['keypad'].last_key_pressed == 'application_halt':
            main_window.close()
            break

        # Manage stages
        if run['CURRENT_STAGE'] == 'application_halt':
            main_window.close()
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


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        logger.exception(error)
    logger.warning('application halted')
