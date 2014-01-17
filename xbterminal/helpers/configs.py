# -*- coding: utf-8 -*-
import hashlib
import json
import os
import requests

import xbterminal
import xbterminal.defaults
from xbterminal.exceptions import ConfigLoadError
from xbterminal.helpers.misc import log

def load_remote_config():
    global xbterminal

    device_key_file_abs_path = os.path.abspath(os.path.join(xbterminal.defaults.PROJECT_ABS_PATH,
                                                            xbterminal.defaults.DEVICE_KEY_FILE_PATH))
    if not os.path.exists(device_key_file_abs_path):
        log('device key missing at path "{device_key_path}", exiting'.format(device_key_path=device_key_file_abs_path),
                      xbterminal.defaults.LOG_MESSAGE_TYPES['ERROR'])
        exit()

    with open(device_key_file_abs_path, 'r') as device_key_file:
        xbterminal.device_key = device_key_file.read().strip()

    for server_url in xbterminal.defaults.REMOTE_SERVERS:
        config_url = server_url + xbterminal.defaults.REMOTE_API_ENDPOINTS['config'].format(device_key=xbterminal.device_key)

        try:
            headers = xbterminal.defaults.EXTERNAL_CALLS_REQUEST_HEADERS
            headers['Content-type'] = 'application/json'

            result = requests.get(url=config_url, headers=headers)
            xbterminal.remote_config = result.json()
            xbterminal.runtime['remote_server'] = server_url
            log('remote config loaded from {config_url}'.format(config_url=config_url),
                xbterminal.defaults.LOG_MESSAGE_TYPES['DEBUG'])
            log('remote config: {remote_config}'.format(remote_config=result.text),
                xbterminal.defaults.LOG_MESSAGE_TYPES['DEBUG'])
            save_remote_config_cache()
            return
        except:
            log('remote config {config_url} unreachable, trying next server'.format(config_url=config_url),
                      xbterminal.defaults.LOG_MESSAGE_TYPES['WARNING'])

    log('no remote configs available, trying local cache'.format(config_url=config_url),
              xbterminal.defaults.LOG_MESSAGE_TYPES['WARNING'])
    try:
        load_remote_config_cache()
    except IOError:
        raise ConfigLoadError()


def load_local_state():
    local_state_file_abs_path = os.path.abspath(os.path.join(xbterminal.defaults.PROJECT_ABS_PATH,
                                                              xbterminal.defaults.STATE_FILE_PATH))

    with open(local_state_file_abs_path, 'a') as config_file:
        pass

    with open(local_state_file_abs_path, 'rb') as state_file:
        try:
            local_state_contents = state_file.read()

            xbterminal.local_state = json.loads(local_state_contents)
            log('local state loaded from "{state_path}"'.format(state_path=local_state_file_abs_path),
                          xbterminal.defaults.LOG_MESSAGE_TYPES['DEBUG'])
            log('local state: {local_state}'.format(local_state=local_state_contents),
                          xbterminal.defaults.LOG_MESSAGE_TYPES['DEBUG'])
        except ValueError:
            xbterminal.local_state = {}
            save_local_state()
            log('local state load error, local state purged', xbterminal.defaults.LOG_MESSAGE_TYPES['DEBUG'])


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
        raise IOError

    with open(remote_config_cache_file_abs_path, 'rb') as cache_file:
        xbterminal.remote_config = json.loads(cache_file.read())

    log('remote config loaded from cache file {cache_path}'.format(cache_path=remote_config_cache_file_abs_path),
        xbterminal.defaults.LOG_MESSAGE_TYPES['DEBUG'])

