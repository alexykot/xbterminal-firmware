# -*- coding: utf-8 -*-
import hashlib
import json
import os
import requests
import logging

import xbterminal
import xbterminal.defaults
from xbterminal.exceptions import ConfigLoadError, DeviceKeyMissingError

logger = logging.getLogger(__name__)


def get_device_key():
    device_key_file_abs_path = os.path.abspath(os.path.join(
        xbterminal.defaults.PROJECT_ABS_PATH,
        xbterminal.defaults.DEVICE_KEY_FILE_PATH))
    if not os.path.exists(device_key_file_abs_path):
        logger.critical("device key missing at path \"{device_key_path}\", exiting".format(
            device_key_path=device_key_file_abs_path))
        raise DeviceKeyMissingError()
    with open(device_key_file_abs_path, 'r') as device_key_file:
        device_key = device_key_file.read().strip()
    return device_key


def choose_remote_server(device_key):
    for server in xbterminal.defaults.REMOTE_SERVERS:
        config_url = server + xbterminal.defaults.REMOTE_API_ENDPOINTS['config'].format(
            device_key=device_key)
        headers = xbterminal.defaults.EXTERNAL_CALLS_REQUEST_HEADERS.copy()
        headers['Content-type'] = 'application/json'
        try:
            response = requests.get(url=config_url, headers=headers, timeout=5)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            logger.warning("remote config {config_url} unreachable, trying next server".format(
                config_url=config_url))
            continue
        config = response.json()
        return server, config
    raise ConfigLoadError()


def load_remote_config():
    xbterminal.device_key = get_device_key()
    try:
        xbterminal.runtime['remote_server'], xbterminal.remote_config = choose_remote_server(
            xbterminal.device_key)
    except ConfigLoadError as config_error:
        logger.warning("no remote configs available, trying local cache")
        try:
            load_remote_config_cache()
        except IOError:
            raise config_error
        init_defaults_config()
    else:
        logger.debug("remote config loaded from {server_url}, contents: {config_contents}".format(
            server_url=xbterminal.runtime['remote_server'],
            config_contents=xbterminal.remote_config))
        save_remote_config_cache()


def load_local_state():
    global xbterminal

    local_state_file_abs_path = os.path.abspath(os.path.join(xbterminal.defaults.PROJECT_ABS_PATH,
                                                              xbterminal.defaults.STATE_FILE_PATH))

    with open(local_state_file_abs_path, 'a') as config_file:
        pass

    with open(local_state_file_abs_path, 'rb') as state_file:
        try:
            local_state_contents = state_file.read()

            xbterminal.local_state = json.loads(local_state_contents)
            logger.debug('local state loaded from {path}, {contents}'.format(path=local_state_file_abs_path,
                                                                    contents=local_state_contents))

            if 'use_dev_remote_server' in xbterminal.local_state and xbterminal.local_state['use_dev_remote_server']:
                xbterminal.defaults.REMOTE_SERVERS = ('http://stage.xbterminal.com',)
                logger.debug('!!! DEV SERVER OVERRRIDE ACTIVE, servers: {}'.format(xbterminal.defaults.REMOTE_SERVERS[0]))

        except ValueError:
            xbterminal.local_state = {}
            save_local_state()
            logger.debug('local state load error, local state purged')


def save_local_state():
    global xbterminal

    local_state_file_abs_path = os.path.abspath(os.path.join(xbterminal.defaults.PROJECT_ABS_PATH,
                                                              xbterminal.defaults.STATE_FILE_PATH))
    with open(local_state_file_abs_path, 'wb') as state_file:
        state_file.write(json.dumps(xbterminal.local_state, indent=2, sort_keys=True, separators=(',', ': ')))


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
        logger.warning('config cache file {cache_path} not exists, cache load failed'.format(cache_path=remote_config_cache_file_abs_path))
        raise IOError

    with open(remote_config_cache_file_abs_path, 'rb') as cache_file:
        xbterminal.remote_config = json.loads(cache_file.read())

    logger.debug('remote config loaded from cache file {cache_path}'.format(cache_path=remote_config_cache_file_abs_path))


def init_defaults_config():
    global xbterminal

    xbterminal.defaults.EXTERNAL_CALLS_REQUEST_HEADERS['Origin'].format(serial_number=xbterminal.remote_config['SERIAL_NUMBER'])
