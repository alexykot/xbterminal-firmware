import json
import logging
import subprocess

logger = logging.getLogger(__name__)


def get_public_key_fingerprint():
    """
    https://docs.saltstack.com/en/latest/ref/cli/salt-call.html
    """
    command = [
        'salt-call',
        '--local',
        '--out', 'json',
        'key.finger',
    ]
    try:
        result = subprocess.check_output(command)
    except subprocess.CalledProcessError as error:
        logger.exception(error)
        return
    data = json.loads(result)
    fingerprint = data['local']
    logger.info('salt public key fingerprint {}'.format(fingerprint))
    return fingerprint
