# -*- coding: utf-8 -*-
import hashlib
import json
import os

import nfc_terminal
from nfc_terminal.helpers.log import write_msg_log

def load_config():
    global nfc_terminal

    config_file_abs_path = os.path.abspath(os.path.join(nfc_terminal.defaults.PROJECT_ABS_PATH,
                                                        nfc_terminal.defaults.CONFIG_FILE_PATH))

    if not os.path.exists(config_file_abs_path):
        write_msg_log('config missing at path "%s", creating default config' % config_file_abs_path,
                      nfc_terminal.defaults.LOG_MESSAGE_TYPES['WARNING'])
        create_default_config()

    with open(config_file_abs_path, 'r') as config_file:
        nfc_terminal.config = json.loads(config_file.read())
        write_msg_log('config loaded from "%s"' % config_file_abs_path,
                      nfc_terminal.defaults.LOG_MESSAGE_TYPES['DEBUG'])


def create_default_config():
    global nfc_terminal

    default_config_data = {'device_reference': hashlib.sha256(os.urandom(32)).hexdigest(),
                           'merchant_id': 0,
                           'loglevel': nfc_terminal.defaults.LOG_LEVELS['DEBUG'],
                           }
    default_config_data['device_id'] = '%s|%s' % (default_config_data['device_reference'], default_config_data['merchant_id'])
    default_config_data['device_id'] = hashlib.sha256(default_config_data['device_id']).hexdigest(),


    config_file_abs_path = os.path.abspath(os.path.join(nfc_terminal.defaults.PROJECT_ABS_PATH,
                                                        nfc_terminal.defaults.CONFIG_FILE_PATH))
    with open(config_file_abs_path, 'w') as config_file:
        config_file.write(json.dumps(default_config_data, indent=2, sort_keys=True, separators=(',', ': ')))


