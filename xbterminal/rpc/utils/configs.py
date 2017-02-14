# -*- coding: utf-8 -*-
import json
import os
import logging
import pprint

from xbterminal.rpc import settings
from xbterminal.rpc.exceptions import ConfigLoadError
from xbterminal.rpc.utils import api
from xbterminal.rpc.state import state

logger = logging.getLogger(__name__)


def read_device_key():
    with open(settings.DEVICE_KEY_FILE_PATH) as device_key_file:
        device_key = device_key_file.read().strip()
    logger.info('device key {}'.format(device_key))
    return device_key


def read_batch_number():
    with open(settings.BATCH_NUMBER_FILE_PATH) as batch_number_file:
        batch_number = batch_number_file.read().strip()
    logger.info('batch number {}'.format(batch_number))
    return batch_number


def load_remote_config():
    config_url = api.get_url('config',
                             device_key=state['device_key'])
    try:
        response = api.send_request('get', config_url)
        remote_config = response.json()
    except Exception:
        logger.warning("no remote configs available, trying local cache")
        try:
            return load_remote_config_cache()
        except IOError:
            raise ConfigLoadError()
    else:
        # Compare configs
        if cmp(state['remote_config'], remote_config):
            logger.info('remote config loaded, contents:\n{config_contents}'.format(
                config_contents=pprint.pformat(remote_config)))
            save_remote_config_cache(remote_config)
        else:
            logger.debug('remote config loaded, unchanged')
        return remote_config


def save_remote_config_cache(remote_config):
    with open(settings.REMOTE_CONFIG_CACHE_FILE_PATH, 'wb') as cache_file:
        cache_file.write(json.dumps(remote_config))


def load_remote_config_cache():
    if not os.path.exists(settings.REMOTE_CONFIG_CACHE_FILE_PATH):
        logger.warning('remote config cache file not exists, cache load failed')
        raise IOError

    with open(settings.REMOTE_CONFIG_CACHE_FILE_PATH, 'rb') as cache_file:
        remote_config = json.loads(cache_file.read())

    logger.debug('remote config loaded from cache')

    return remote_config


def load_rpc_config():
    """
    RPC server config params:
        activation_code: string (default: None)
        last_started: float (default: None)
        remote_server: string (default: 'prod')
        use_bsp_mock: boolean (default: False)
    Returns:
        rpc_config: dict
    """
    if not os.path.exists(settings.RPC_CONFIG_FILE_PATH):
        rpc_config = {}
        save_rpc_config(rpc_config)
        logger.info('created new rpc config at {}'.format(
            settings.RPC_CONFIG_FILE_PATH))
    else:
        with open(settings.RPC_CONFIG_FILE_PATH) as rpc_config_file:
            rpc_config = json.loads(rpc_config_file.read())
            logger.info('rpc config loaded from {0}:\n{1}'.format(
                settings.RPC_CONFIG_FILE_PATH,
                pprint.pformat(rpc_config)))
    return rpc_config


def save_rpc_config(rpc_config):
    with open(settings.RPC_CONFIG_FILE_PATH, 'w') as rpc_config_file:
        rpc_config_file.write(json.dumps(
            rpc_config, indent=2, sort_keys=True, separators=(',', ': ')))
