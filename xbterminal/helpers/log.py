# -*- coding: utf-8 -*-
import os
import time
from email import utils

import xbterminal


def log(message_text, message_type=None):
    global xbterminal
    if message_type is None:
        message_type = xbterminal.defaults.LOG_MESSAGE_TYPES['DEBUG']

    timestamp = utils.formatdate(time.time())

    log_abs_path = os.path.abspath(os.path.join(xbterminal.defaults.PROJECT_ABS_PATH, xbterminal.defaults.LOG_FILE_PATH))

    if (message_type == xbterminal.defaults.LOG_MESSAGE_TYPES['DEBUG']
        and hasattr(xbterminal, 'remote_config')
        and 'LOG_LEVEL' in xbterminal.remote_config
        and xbterminal.remote_config['LOG_LEVEL'] != xbterminal.defaults.LOG_LEVELS['DEBUG']):
        return

    with open(log_abs_path, 'a') as log_file:
        log_string = '%s; %s: %s' % (timestamp, message_type, message_text)
        if (not hasattr(xbterminal, 'remote_config')
            or 'LOG_LEVEL' not in xbterminal.remote_config
            or xbterminal.remote_config['LOG_LEVEL'] == xbterminal.defaults.LOG_LEVELS['DEBUG']):
            print log_string
        log_file.write(log_string+'\n')


