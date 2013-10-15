import hashlib
import json
import os

import nfc_terminal
from nfc_terminal import defaults
from nfc_terminal.helpers.log import write_msg_log


def load_config():
    global nfc_terminal

    config_file_abs_path = os.path.abspath(os.path.join(defaults.PROJECT_ABS_PATH, defaults.CONFIG_FILE_PATH))

    if not os.path.exists(config_file_abs_path):
        write_msg_log('config missing at path "%s", creating default config' % config_file_abs_path,
                      defaults.LOG_MESSAGE_TYPES['WARNING'])
        create_default_config()

    with open(config_file_abs_path, 'r') as config_file:
        nfc_terminal.config = json.loads(config_file.read())
        write_msg_log('config loaded from "%s"' % config_file_abs_path,
                      defaults.LOG_MESSAGE_TYPES['DEBUG'])


def create_default_config():
    global defaults

    default_config_data = {'device_reference': hashlib.sha256(os.urandom(32)).hexdigest(),
                           'merchant_id': 0,
                           'loglevel': defaults.LOG_LEVELS['DEBUG'],
                           }
    default_config_data['device_id'] = '%s|%s' % (default_config_data['device_reference'], default_config_data['merchant_id'])
    default_config_data['device_id'] = hashlib.sha256(default_config_data['device_id']).hexdigest(),


    config_file_abs_path = os.path.abspath(os.path.join(defaults.PROJECT_ABS_PATH, defaults.CONFIG_FILE_PATH))
    with open(config_file_abs_path, 'w') as config_file:
        config_file.write(json.dumps(default_config_data, indent=2, sort_keys=True, separators=(',', ': ')))


def formatDefaultAmountOutput():
    def strrepeat(string_to_expand, length):
        return (string_to_expand * ((length/len(string_to_expand))+1))[:length]

    decimal_part = '0'
    fractional_part = strrepeat('0', defaults.OUTPUT_DEC_PLACES)

    default_amount_output = '%s%s%s' % (decimal_part, defaults.OUTPUT_DEC_FRACTIONAL_SPLIT, fractional_part)
    return default_amount_output

