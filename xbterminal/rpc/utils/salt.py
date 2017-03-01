import json
import logging
import subprocess

logger = logging.getLogger(__name__)

SALT_BIN = '/usr/bin/salt-call'


def get_public_key_fingerprint():
    """
    https://docs.saltstack.com/en/latest/ref/cli/salt-call.html
    """
    result = subprocess.check_output([  # nosec
        SALT_BIN,
        '--local',
        '--hard-crash',
        '--out', 'json',
        'key.finger',
    ])
    data = json.loads(result)
    fingerprint = data['local']
    logger.info('salt public key fingerprint {}'.format(fingerprint))
    return fingerprint
