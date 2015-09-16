import hashlib
import logging
import os
import uuid

from xbterminal import defaults
from xbterminal.exceptions import DeviceKeyMissingError

logger = logging.getLogger(__name__)


def read_device_key():
    if not os.path.exists(defaults.DEVICE_KEY_FILE_PATH):
        raise DeviceKeyMissingError()
    with open(defaults.DEVICE_KEY_FILE_PATH, 'r') as device_key_file:
        device_key = device_key_file.read().strip()
    logger.info('device key {}'.format(device_key))
    return device_key


def generate_device_key():
    device_key = hashlib.sha256(uuid.uuid4().bytes).hexdigest()
    with open(defaults.DEVICE_KEY_FILE_PATH, 'w') as device_key_file:
        device_key_file.write(device_key)
    logger.info('generated device key {key}, saved to {path}'.format(
        key=device_key, path=defaults.DEVICE_KEY_FILE_PATH))
    return device_key


def read_batch_number():
    with open(defaults.BATCH_NUMBER_FILE_PATH) as batch_number_file:
        batch_number = batch_number_file.read().strip()
    logger.info('batch number {}'.format(batch_number))
    return batch_number
