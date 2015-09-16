import hashlib
import logging
import os
import uuid

from xbterminal import defaults
from xbterminal.helpers import api, crypto
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
    logger.info('generated device key {}'.format(device_key))
    return device_key


def save_device_key(device_key):
    with open(defaults.DEVICE_KEY_FILE_PATH, 'w') as device_key_file:
        device_key_file.write(device_key)


def read_batch_number():
    with open(defaults.BATCH_NUMBER_FILE_PATH) as batch_number_file:
        batch_number = batch_number_file.read().strip()
    logger.info('batch number {}'.format(batch_number))
    return batch_number


def register_device():
    # Prepare payload
    batch_number = read_batch_number()
    device_key = generate_device_key()
    secret_key, public_key = crypto.generate_keypair()
    data = {
        'batch': batch_number,
        'key': device_key,
        'api_key': public_key,
    }
    # Send registration request
    registration_url = api.get_url('registration')
    response = api.send_request('post', registration_url, data)
    data = response.json()
    activation_code = data['activation_code']
    logger.info('device registered, activation code {}'.format(
        activation_code))
    # Save keys
    save_device_key(device_key)
    crypto.save_secret_key(secret_key)
    return device_key, activation_code
