import logging

from xbterminal import defaults
from xbterminal.helpers import configs
from xbterminal.keypad.keypad import Keypad
from xbterminal.watcher import Watcher

logger = logging.getLogger(__name__)


def init_step_1(state):
    state['device_key'] = configs.read_device_key()
    state['local_config'] = configs.load_local_config()

    remote_server_name = state['local_config'].get('remote_server', 'prod')
    state['remote_server'] = defaults.REMOTE_SERVERS[remote_server_name]
    logger.info('remote server {}'.format(state['remote_server']))

    state['keypad'] = Keypad()

    state['watcher'] = Watcher()
    state['watcher'].start()
