import logging
import time

from xbterminal.rpc import activation, settings
from xbterminal.rpc.utils import configs, clock
from xbterminal.rpc.utils.bt import BluetoothServer
from xbterminal.rpc.utils.camera import QRScanner
from xbterminal.rpc.utils.host import HostSystem
from xbterminal.rpc.utils.nfcpy import NFCServer
from xbterminal.rpc.watcher import Watcher

logger = logging.getLogger(__name__)


def init_step_1(state):
    state['device_key'] = configs.read_device_key()
    state['local_config'] = configs.load_local_config()

    remote_server_name = state['local_config'].get('remote_server', 'prod')
    state['remote_server'] = settings.REMOTE_SERVERS[remote_server_name]
    logger.info('remote server {}'.format(state['remote_server']))

    state['watcher'] = Watcher()
    state['watcher'].start()

    state['host_system'] = HostSystem(
        use_mock=state['local_config'].get('use_cctalk_mock', True))
    state['bluetooth_server'] = BluetoothServer()
    state['nfc_server'] = NFCServer()
    state['qr_scanner'] = QRScanner(backend='fswebcam')


def init_step_2(state):
    # Check system clock
    while True:
        internet_time = clock.get_internet_time()
        time_delta = abs(time.time() - internet_time)
        if time_delta < 60:  # 1 minute
            logger.info('clock synchronized')
            state['init']['clock_synchronized'] = True
            state['local_config']['last_started'] = time.time()
            configs.save_local_config(state['local_config'])
            break
        logger.warning('machine time differs from internet time: {0}'.format(time_delta))
        time.sleep(5)

    # Check registration
    if not activation.is_registered():
        state['local_config']['activation_code'] = activation.register_device()
        configs.save_local_config(state['local_config'])
    state['init']['registration'] = True

    # Load remote config
    state['remote_config'] = configs.load_remote_config()
    state['init']['remote_config'] = True
    state['remote_config_last_update'] = int(time.time())
    logger.info('working with {0}'.format(
        state['remote_config']['bitcoin_network']))
