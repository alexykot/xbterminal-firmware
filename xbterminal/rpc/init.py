import logging
import time

from xbterminal.rpc import activation, settings
from xbterminal.rpc.utils import configs, clock
from xbterminal.rpc.utils.bt import BluetoothServer
from xbterminal.rpc.utils.camera import QRScanner
from xbterminal.rpc.utils.bsp import BSPLibraryInterface
from xbterminal.rpc.watcher import Watcher

logger = logging.getLogger(__name__)


def init_step_1(state):
    state['device_key'] = configs.read_device_key()
    state['rpc_config'] = configs.load_rpc_config()

    remote_server_name = state['rpc_config'].get('remote_server', 'prod')
    state['remote_server'] = settings.REMOTE_SERVERS[remote_server_name]
    logger.info('remote server {}'.format(state['remote_server']))

    state['watcher'] = Watcher()
    state['watcher'].start()

    state['bsp_interface'] = BSPLibraryInterface(
        use_mock=state['rpc_config'].get('use_bsp_mock', False))
    state['bluetooth_server'] = BluetoothServer()
    state['qr_scanner'] = QRScanner()


def init_step_2(state):
    # Check system clock
    while True:
        internet_time = clock.get_internet_time()
        time_delta = abs(time.time() - internet_time)
        if time_delta < 60:  # 1 minute
            logger.info('clock synchronized')
            state['init']['clock_synchronized'] = True
            state['rpc_config']['last_started'] = time.time()
            configs.save_rpc_config(state['rpc_config'])
            break
        logger.warning('machine time differs from internet time: {0}'.format(time_delta))
        time.sleep(5)

    # Check registration
    if not activation.is_registered():
        state['rpc_config']['activation_code'] = activation.register_device()
        configs.save_rpc_config(state['rpc_config'])
    state['init']['registration'] = True

    # Load remote config
    state['remote_config'] = configs.load_remote_config()
    state['init']['remote_config'] = True
    state['remote_config_last_update'] = int(time.time())
    logger.info('working with {0}'.format(
        state['remote_config']['bitcoin_network']))
