import time
from email import utils

import nfc_terminal


def write_msg_log(message_text, message_type=None):
    global nfc_terminal
    if message_type is None:
        message_type = nfc_terminal.defaults.LOG_MESSAGE_TYPES['ERROR']

    timestamp = utils.formatdate(time.time())

    if (message_type == nfc_terminal.defaults.LOG_MESSAGE_TYPES['DEBUG']
        and 'config' in nfc_terminal
        and nfc_terminal.config.LOG_LEVEL != nfc_terminal.defaults.LOG_LEVELS['DEBUG']):
        return

    with open(nfc_terminal.defaults.LOG_FILE_PATH, 'a') as log_file:
        log_string = '%s; %s: %s' % (timestamp, message_type, message_text)
        if 'config' not in nfc_terminal or nfc_terminal.config.LOG_LEVEL == nfc_terminal.defaults.LOG_LEVELS['DEBUG']:
            print log_string
        log_file.write(log_string+'\n')


