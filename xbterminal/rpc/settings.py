import os
from decimal import Decimal

VERSION = '0.22.1'

try:
    from xbterminal.nuitka_fix import BASE_DIR
except ImportError:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

PROJECT_LOCAL_PATH = os.path.join(BASE_DIR, 'xbterminal')

RUNTIME_PATH = os.path.join(PROJECT_LOCAL_PATH, 'runtime')
BATCH_NUMBER_FILE_PATH = os.path.join(RUNTIME_PATH, 'batch_number')
DEVICE_KEY_FILE_PATH = os.path.join(RUNTIME_PATH, 'device_key')
RPC_CONFIG_FILE_PATH = os.path.join(RUNTIME_PATH, 'rpc_config')
REMOTE_CONFIG_CACHE_FILE_PATH = os.path.join(RUNTIME_PATH, 'remote_config_cache')
SECRET_KEY_FILE_PATH = os.path.join(RUNTIME_PATH, 'secret_key')

LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(asctime)s %(name)s [%(levelname)s] :: %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'simple',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'requests.packages.urllib3.connectionpool': {
            'level': 'WARNING',
        },
        'urllib3.connectionpool': {
            'level': 'WARNING',
        },
        'tornado.access': {
            'level': 'WARNING',
        },
    },
}

REMOTE_SERVERS = {
    'prod': 'https://xbterminal.io',
    'stage': 'http://stage.xbterminal.com',
    'dev': 'http://dev.xbterminal.com:8083',
}

REMOTE_API_ENDPOINTS = {
    'ping': '/api/v2/ping/',
    'registration': '/api/v2/devices/',
    'config': '/api/v2/devices/{device_key}/',
    'payment_init': '/api/v2/payments/',
    'payment_cancel': '/api/v2/payments/{uid}/cancel/',
    'payment_response': '/api/v2/payments/{uid}/response/',
    'payment_info': '/api/v2/payments/{uid}/',
    'payment_receipt': '/prc/{uid}/',
    'withdrawal_init': '/api/v2/withdrawals/',
    'withdrawal_confirm': '/api/v2/withdrawals/{uid}/confirm/',
    'withdrawal_cancel': '/api/v2/withdrawals/{uid}/cancel/',
    'withdrawal_info': '/api/v2/withdrawals/{uid}/',
    'withdrawal_receipt': '/wrc/{uid}/',
}
EXTERNAL_CALLS_TIMEOUT = 15
EXTERNAL_CALLS_REQUEST_HEADERS = {'User-Agent': 'XBTerminal type 1'}

FIAT_DEC_PLACES = Decimal('0.00000000')
BTC_DEC_PLACES = Decimal('0.00000000')
