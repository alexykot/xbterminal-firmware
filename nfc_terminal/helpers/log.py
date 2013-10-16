# -*- coding: utf-8 -*-
import os
import time
from email import utils

import nfc_terminal


def write_msg_log(message_text, message_type=None):
    global nfc_terminal
    if message_type is None:
        message_type = nfc_terminal.defaults.LOG_MESSAGE_TYPES['ERROR']

    timestamp = utils.formatdate(time.time())

    log_abs_path = os.path.abspath(os.path.join(nfc_terminal.defaults.PROJECT_ABS_PATH, nfc_terminal.defaults.LOG_FILE_PATH))

    if (message_type == nfc_terminal.defaults.LOG_MESSAGE_TYPES['DEBUG']
        and hasattr(nfc_terminal, 'config')
        and 'LOG_LEVEL' in nfc_terminal.config
        and nfc_terminal.config['LOG_LEVEL'] != nfc_terminal.defaults.LOG_LEVELS['DEBUG']):
        return

    with open(log_abs_path, 'a') as log_file:
        log_string = '%s; %s: %s' % (timestamp, message_type, message_text)
        if (not hasattr(nfc_terminal, 'config')
            or 'LOG_LEVEL' not in nfc_terminal.config
            or nfc_terminal.config['LOG_LEVEL'] == nfc_terminal.defaults.LOG_LEVELS['DEBUG']):
            print log_string
        log_file.write(log_string+'\n')


