# -*- coding: utf-8 -*-
import json
import os
import requests
import logging

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
    remote_config_old_items = set(getattr(xbterminal, "remote_config", {}).items())
    config_url = xbterminal.runtime['remote_server'] + xbterminal.defaults.REMOTE_API_ENDPOINTS['config'].format(
        device_key=xbterminal.runtime['device_key'])
    headers = xbterminal.defaults.EXTERNAL_CALLS_REQUEST_HEADERS.copy()
    headers['Content-type'] = 'application/json'
    try:
        response = requests.get(url=config_url, headers=headers)
        response.raise_for_status()
        xbterminal.remote_config = response.json()
    except Exception as error:
        logger.warning("no remote configs available, trying local cache")
        try:
            xbterminal.remote_config = load_remote_config_cache()
        except IOError:
            raise ConfigLoadError()
    else:
        # Compare configs
        if remote_config_old_items ^ set(xbterminal.remote_config.items()):
            logger.debug("remote config loaded from {server_url}, contents: {config_contents}".format(
                server_url=xbterminal.runtime['remote_server'],
                config_contents=xbterminal.remote_config))
        else:
            logger.debug("remote config loaded from {server_url}, unchanged".format(
                server_url=xbterminal.runtime['remote_server']))
        save_remote_config_cache()


def load_local_state():
    local_state_file_abs_path = xbterminal.defaults.STATE_FILE_PATH

    with open(local_state_file_abs_path, 'a') as state_file:
        pass
    with open(local_state_file_abs_path, 'rb') as state_file:
        local_state_contents = state_file.read()
        try:
            xbterminal.local_state = json.loads(local_state_contents)
        except ValueError:
            xbterminal.local_state = {}
            save_local_state()
            logger.debug('local state load error, local state purged')
        else:
            logger.debug('local state loaded from {path}, {contents}'.format(
                path=local_state_file_abs_path,
                contents=local_state_contents))


def save_local_state():
    local_state_file_abs_path = xbterminal.defaults.STATE_FILE_PATH
    with open(local_state_file_abs_path, 'wb') as state_file:
        state_file.write(json.dumps(xbterminal.local_state, indent=2, sort_keys=True, separators=(',', ': ')))


def save_remote_config_cache():
    remote_config_cache_file_abs_path = xbterminal.defaults.REMOTE_CONFIG_CACHE_FILE_PATH
    with open(remote_config_cache_file_abs_path, 'wb') as cache_file:
        cache_file.write(json.dumps(xbterminal.remote_config))


def load_remote_config_cache():
    remote_config_cache_file_abs_path = xbterminal.defaults.REMOTE_CONFIG_CACHE_FILE_PATH

    if not os.path.exists(remote_config_cache_file_abs_path):
        logger.warning('config cache file {cache_path} not exists, cache load failed'.format(
            cache_path=remote_config_cache_file_abs_path))
        raise IOError

    with open(remote_config_cache_file_abs_path, 'rb') as cache_file:
        remote_config = json.loads(cache_file.read())

    logger.debug('remote config loaded from cache file {cache_path}'.format(
        cache_path=remote_config_cache_file_abs_path))

    return remote_config
