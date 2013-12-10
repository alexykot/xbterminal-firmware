# -*- coding: utf-8 -*-
import hashlib
import json
import os
import requests

import xbterminal
import xbterminal.defaults
from xbterminal.helpers.log import log

def load_configs():
    global xbterminal

    local_state_file_abs_path = os.path.abspath(os.path.join(xbterminal.defaults.PROJECT_ABS_PATH,
                                                              xbterminal.defaults.STATE_FILE_PATH))

    with open(local_state_file_abs_path, 'a') as config_file:
        pass

    with open(local_state_file_abs_path, 'r') as state_file:
        xbterminal.local_state = json.loads(state_file.read())
        log('config loaded from "%s"'.format(local_state_file_abs_path),
                      xbterminal.defaults.LOG_MESSAGE_TYPES['DEBUG'])

    device_key_file_abs_path = os.path.abspath(os.path.join(xbterminal.defaults.PROJECT_ABS_PATH,
                                                            xbterminal.defaults.DEVICE_KEY_FILE_PATH))
    if not os.path.exists(local_config_file_abs_path):
        log('device key missing at path "{device_key_path}", exiting'.format(device_key_path=local_config_file_abs_path),
                      xbterminal.defaults.LOG_MESSAGE_TYPES['ERROR'])
        exit()

    with open(device_key_file_abs_path, 'r') as device_key_file:
        xbterminal.device_key = device_key_file.read().strip()

    xbterminal.remote_config = None
    for server in xbterminal.defaults.REMOTE_SERVERS:
        config_url = xbterminal.defaults.REMOTE_SERVER_CONFIG_URL_TEMPLATE.format(server_address=server,
                                                                                  device_key=xbterminal.device_key)
        try:
            result = requests.get(url=config_url)
            xbterminal.remote_config = result.json()
        except:
            log('remote config server {server_name} unreachable'.format(server),
                      xbterminal.defaults.LOG_MESSAGE_TYPES['WARNING'])

    if xbterminal.remote_config is None:
        log('remote config load failed, exiting'.format(local_config_file_abs_path),
                      xbterminal.defaults.LOG_MESSAGE_TYPES['ERROR'])
        exit()

