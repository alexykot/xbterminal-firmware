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

    with open(local_state_file_abs_path, 'rb') as state_file:
        xbterminal.local_state = json.loads(state_file.read())
        log('local state loaded from "{state_path}"'.format(state_path=local_state_file_abs_path),
                      xbterminal.defaults.LOG_MESSAGE_TYPES['DEBUG'])

    device_key_file_abs_path = os.path.abspath(os.path.join(xbterminal.defaults.PROJECT_ABS_PATH,
                                                            xbterminal.defaults.DEVICE_KEY_FILE_PATH))
    if not os.path.exists(device_key_file_abs_path):
        log('device key missing at path "{device_key_path}", exiting'.format(device_key_path=device_key_file_abs_path),
                      xbterminal.defaults.LOG_MESSAGE_TYPES['ERROR'])
        exit()

    with open(device_key_file_abs_path, 'r') as device_key_file:
        xbterminal.device_key = device_key_file.read().strip()

    for server in xbterminal.defaults.REMOTE_SERVERS:
        config_url = xbterminal.defaults.REMOTE_SERVER_CONFIG_URL_TEMPLATE.format(server_address=server,
                                                                                  device_key=xbterminal.device_key)
        try:
            result = requests.get(url=config_url)
            xbterminal.remote_config = result.json()
            log('remote config loaded from {config_url}'.format(config_url=config_url),
                xbterminal.defaults.LOG_MESSAGE_TYPES['DEBUG'])
            save_remote_config_cache()
        except:
            log('remote config {config_url} unreachable, trying to load cache'.format(config_url=config_url),
                      xbterminal.defaults.LOG_MESSAGE_TYPES['WARNING'])
            load_remote_config_cache()

    if not hasattr(xbterminal, 'remote_config'):
        log('remote config load failed, exiting', xbterminal.defaults.LOG_MESSAGE_TYPES['ERROR'])
        exit()


def save_local_state():
    global xbterminal

    local_state_file_abs_path = os.path.abspath(os.path.join(xbterminal.defaults.PROJECT_ABS_PATH,
                                                              xbterminal.defaults.STATE_FILE_PATH))
    with open(local_state_file_abs_path, 'wb') as state_file:
        state_file.write(json.dumps(xbterminal.local_state))


def save_remote_config_cache():
    global xbterminal

    remote_config_cache_file_abs_path = os.path.abspath(os.path.join(xbterminal.defaults.PROJECT_ABS_PATH,
                                                                     xbterminal.defaults.REMOTE_CONFIG_CACHE_FILE_PATH))
    with open(remote_config_cache_file_abs_path, 'wb') as cache_file:
        cache_file.write(json.dumps(xbterminal.remote_config))

def load_remote_config_cache():
    global xbterminal

    remote_config_cache_file_abs_path = os.path.abspath(os.path.join(xbterminal.defaults.PROJECT_ABS_PATH,
                                                                     xbterminal.defaults.REMOTE_CONFIG_CACHE_FILE_PATH))

    if not os.path.exists(remote_config_cache_file_abs_path):
        log('config cache file {cache_path} not exists, cache load failed'.format(cache_path=remote_config_cache_file_abs_path),
            xbterminal.defaults.LOG_MESSAGE_TYPES['WARNING'])
        return

    with open(remote_config_cache_file_abs_path, 'rb') as cache_file:
        xbterminal.remote_config = json.loads(cache_file.read())

    log('remote config loaded from cache file {cache_path}'.format(cache_path=remote_config_cache_file_abs_path),
        xbterminal.defaults.LOG_MESSAGE_TYPES['DEBUG'])

