import logging

from xbterminal import defaults
from xbterminal.helpers import configs
from xbterminal.helpers.bt import BluetoothServer
from xbterminal.helpers.camera import QRScanner
from xbterminal.helpers.host import HostSystem
from xbterminal.helpers.nfcpy import NFCServer
from xbterminal.keypad.keypad import Keypad
from xbterminal.watcher import Watcher

logger = logging.getLogger(__name__)


def init_step_1(state):
    state['device_key'] = configs.read_device_key()
    state['local_config'] = configs.load_local_config()

    remote_server_name = state['local_config'].get('remote_server', 'prod')
    state['remote_server'] = defaults.REMOTE_SERVERS[remote_server_name]
    logger.info('remote server {}'.format(state['remote_server']))

    state['watcher'] = Watcher()
    state['watcher'].start()

    state['keypad'] = Keypad()
    state['host_system'] = HostSystem(
        use_mock=state['local_config'].get('use_cctalk_mock', True))
    state['bluetooth_server'] = BluetoothServer()
    state['nfc_server'] = NFCServer()
    state['qr_scanner'] = QRScanner(backend='fswebcam')
