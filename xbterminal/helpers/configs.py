# -*- coding: utf-8 -*-
import json
import os
import requests
import logging
import pprint

import xbterminal
import xbterminal.defaults
from xbterminal.exceptions import (
    ConfigLoadError,
    DeviceKeyMissingError)

logger = logging.getLogger(__name__)


def get_device_key():
    device_key_file_abs_path = xbterminal.defaults.DEVICE_KEY_FILE_PATH
    if not os.path.exists(device_key_file_abs_path):
        logger.critical("device key missing at path \"{device_key_path}\", exiting".format(
            device_key_path=device_key_file_abs_path))
        raise DeviceKeyMissingError()
    with open(device_key_file_abs_path, 'r') as device_key_file:
        device_key = device_key_file.read().strip()
    return device_key


def load_remote_config():
    config_url = xbterminal.runtime['remote_server'] + xbterminal.defaults.REMOTE_API_ENDPOINTS['config'].format(
        device_key=xbterminal.runtime['device_key'])
    headers = xbterminal.defaults.EXTERNAL_CALLS_REQUEST_HEADERS.copy()
    headers['Content-type'] = 'application/json'
    try:
        response = requests.get(url=config_url, headers=headers)
        response.raise_for_status()
        remote_config = response.json()
    except Exception as error:
        logger.warning("no remote configs available, trying local cache")
        try:
            return load_remote_config_cache()
        except IOError:
            raise ConfigLoadError()
    else:
        # Compare configs
        if set(xbterminal.runtime['remote_config'].items()) ^ set(remote_config.items()):
            logger.info('remote config loaded, contents:\n{config_contents}'.format(
                config_contents=pprint.pformat(remote_config)))
        else:
            logger.debug('remote config loaded, unchanged'.format(
                server_url=xbterminal.runtime['remote_server']))
        save_remote_config_cache(remote_config)
        return remote_config


def save_remote_config_cache(remote_config):
    remote_config_cache_file_abs_path = xbterminal.defaults.REMOTE_CONFIG_CACHE_FILE_PATH
    with open(remote_config_cache_file_abs_path, 'wb') as cache_file:
        cache_file.write(json.dumps(remote_config))


def load_remote_config_cache():
    remote_config_cache_file_abs_path = xbterminal.defaults.REMOTE_CONFIG_CACHE_FILE_PATH

    if not os.path.exists(remote_config_cache_file_abs_path):
        logger.warning('remote config cache file not exists, cache load failed'.format(
            cache_path=remote_config_cache_file_abs_path))
        raise IOError

    with open(remote_config_cache_file_abs_path, 'rb') as cache_file:
        remote_config = json.loads(cache_file.read())

    logger.debug('remote config loaded from cache'.format(
        cache_path=remote_config_cache_file_abs_path))

    return remote_config


def load_local_config():
    """
    Local config params:
        last_started: float
        show_cursor: boolean
        use_default_keypad_override: boolean
        use_dev_remote_server: boolean
        wifi_ssid: string
        wifi_pass: string
    Returns:
        local_config: dict
    """
    local_config_path = xbterminal.defaults.LOCAL_CONFIG_FILE_PATH

    if not os.path.exists(local_config_path):
        local_config = {}
        save_local_config(local_config)
        logger.info('created new local config at {}'.format(
            local_config_path))
    else:
        with open(local_config_path) as local_config_file:
            local_config = json.loads(local_config_file.read())
            logger.info('local config loaded from {0}:\n{1}'.format(
                local_config_path,
                pprint.pformat(local_config)))
    return local_config


def save_local_config(local_config):
    local_config_path = xbterminal.defaults.LOCAL_CONFIG_FILE_PATH
    with open(local_config_path, 'w') as local_config_file:
        local_config_file.write(json.dumps(
            local_config, indent=2, sort_keys=True, separators=(',', ': ')))
