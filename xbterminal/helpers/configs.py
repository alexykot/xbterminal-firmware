# -*- coding: utf-8 -*-
import hashlib
import json
import os
import requests

import xbterminal
import xbterminal.defaults
from xbterminal.helpers.log import write_msg_log

def load_configs():
    global xbterminal

    local_config_file_abs_path = os.path.abspath(os.path.join(xbterminal.defaults.PROJECT_ABS_PATH,
                                                                xbterminal.defaults.CONFIG_FILE_PATH))

    if not os.path.exists(local_config_file_abs_path):
        write_msg_log('config missing at path "{}", exiting'.format(local_config_file_abs_path),
                      xbterminal.defaults.LOG_MESSAGE_TYPES['ERROR'])
        exit()

    with open(local_config_file_abs_path, 'r') as config_file:
        xbterminal.local_config = json.loads(config_file.read())
        write_msg_log('config loaded from "%s"'.format(local_config_file_abs_path),
                      xbterminal.defaults.LOG_MESSAGE_TYPES['DEBUG'])


    xbterminal.remote_config = None
    for server in xbterminal.defaults.REMOTE_SERVERS:
        config_url = xbterminal.defaults.REMOTE_SERVER_CONFIG_URL_TEMPLATE.format(server_address=server,
                                                                                  device_key=xbterminal.local_config['device_key'])
        try:
            result = requests.get(url=config_url)
            xbterminal.remote_config = result.json()
        except:
            write_msg_log('remote config server {server_name} unreachable'.format(server),
                      xbterminal.defaults.LOG_MESSAGE_TYPES['WARNING'])

    if xbterminal.remote_config is None:
        write_msg_log('remote config load failed, exiting'.format(local_config_file_abs_path),
                      xbterminal.defaults.LOG_MESSAGE_TYPES['ERROR'])
        exit()

