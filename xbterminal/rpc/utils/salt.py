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
    result = subprocess.check_output(command)
    data = json.loads(result)
    fingerprint = data['local']
    logger.info('salt public key fingerprint {}'.format(fingerprint))
    return fingerprint
