# -*- coding: utf-8 -*-
import json
import os
import logging
import pprint

import xbterminal
from xbterminal import defaults
from xbterminal.exceptions import ConfigLoadError
from xbterminal.helpers import api

logger = logging.getLogger(__name__)


def read_device_key():
    with open(defaults.DEVICE_KEY_FILE_PATH) as device_key_file:
        device_key = device_key_file.read().strip()
    logger.info('device key {}'.format(device_key))
    return device_key


def read_batch_number():
    with open(defaults.BATCH_NUMBER_FILE_PATH) as batch_number_file:
        batch_number = batch_number_file.read().strip()
    logger.info('batch number {}'.format(batch_number))
    return batch_number


def load_remote_config():
    config_url = api.get_url('config',
                             device_key=xbterminal.runtime['device_key'])
    try:
        response = api.send_request('get', config_url)
        remote_config = response.json()
    except Exception as error:
        logger.warning("no remote configs available, trying local cache")
        try:
            return load_remote_config_cache()
        except IOError:
            raise ConfigLoadError()
    else:
        # Compare configs
        if cmp(xbterminal.runtime['remote_config'], remote_config):
            logger.info('remote config loaded, contents:\n{config_contents}'.format(
                config_contents=pprint.pformat(remote_config)))
        else:
            logger.debug('remote config loaded, unchanged')
        save_remote_config_cache(remote_config)
        return remote_config


def save_remote_config_cache(remote_config):
    with open(defaults.REMOTE_CONFIG_CACHE_FILE_PATH, 'wb') as cache_file:
        cache_file.write(json.dumps(remote_config))


def load_remote_config_cache():
    if not os.path.exists(defaults.REMOTE_CONFIG_CACHE_FILE_PATH):
        logger.warning('remote config cache file not exists, cache load failed')
        raise IOError

    with open(defaults.REMOTE_CONFIG_CACHE_FILE_PATH, 'rb') as cache_file:
        remote_config = json.loads(cache_file.read())

    logger.debug('remote config loaded from cache')

    return remote_config


def load_local_config():
    """
    Local config params:
        activation_code: string (default: None)
        language: string (default: 'en')
        theme: string (default: 'default')
        last_started: float (default: None)
        show_cursor: boolean (default: False)
        use_dev_remote_server: boolean (default: False)
        use_cctalk_mock: boolean (default: True)
    Obsolete:
        disable_cctalk: boolean
        use_default_keypad_override: boolean
        use_keypad: boolean
        use_predefined_connection: boolean
        wifi_ssid: string
        wifi_pass: string
    Returns:
        local_config: dict
    """
    if not os.path.exists(defaults.LOCAL_CONFIG_FILE_PATH):
        local_config = {}
        save_local_config(local_config)
        logger.info('created new local config at {}'.format(
            defaults.LOCAL_CONFIG_FILE_PATH))
    else:
        with open(defaults.LOCAL_CONFIG_FILE_PATH) as local_config_file:
            local_config = json.loads(local_config_file.read())
            logger.info('local config loaded from {0}:\n{1}'.format(
                defaults.LOCAL_CONFIG_FILE_PATH,
                pprint.pformat(local_config)))
    return local_config


def save_local_config(local_config):
    with open(defaults.LOCAL_CONFIG_FILE_PATH, 'w') as local_config_file:
        local_config_file.write(json.dumps(
            local_config, indent=2, sort_keys=True, separators=(',', ': ')))
