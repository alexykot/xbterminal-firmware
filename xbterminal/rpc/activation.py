import logging

from xbterminal.rpc.utils import api, crypto, configs, salt

logger = logging.getLogger(__name__)


def register_device():
    # Prepare payload
    batch_number = configs.read_batch_number()
    device_key = configs.read_device_key()
    secret_key, public_key = crypto.generate_keypair()
    salt_fingerprint = salt.get_public_key_fingerprint()
    data = {
        'batch': batch_number,
        'key': device_key,
        'api_key': public_key,
        'salt_fingerprint': salt_fingerprint,
    }
    # Send registration request
    registration_url = api.get_url('registration')
    response = api.send_request('post', registration_url, data)
    data = response.json()
    activation_code = data['activation_code']
    logger.info('device registered, activation code {}'.format(
        activation_code))
    # Save secret key
    crypto.save_secret_key(secret_key)
    return activation_code


def is_registered():
    try:
        # Registered devices must have the secret key
        crypto.read_secret_key()
    except IOError:
        return False
    return True
