import os
from decimal import Decimal


STAGES = {
    'bootup': 'bootup',
    'activate': 'activate',
    'idle': 'idle',
    'selection': 'selection',
    'payment': {
        'pay_amount': 'pay_amount',
        'pay_confirm': 'pay_confirm',
        'pay_loading': 'pay_loading',
        'pay_info': 'pay_info',
        'pay_wait': 'pay_wait',
        'pay_success': 'pay_success',
        'pay_receipt': 'pay_receipt',
        'pay_cancel': 'pay_cancel',
    },
    'withdrawal': {
        'withdraw_loading1': 'withdraw_loading1',
        'withdraw_scan': 'withdraw_scan',
        'withdraw_confirm': 'withdraw_confirm',
        'withdraw_loading2': 'withdraw_loading2',
        'withdraw_success': 'withdraw_success',
        'withdraw_receipt': 'withdraw_receipt',
    },
    'application_halt': 'application_halt',
}

SCREENS = {
    'load_indefinite': 0,
    'activation': 1,
    'idle': 2,
    'selection': 3,
    'pay_amount': 4,
    'pay_confirm': 5,
    'pay_info': 6,
    'pay_wait': 7,
    'pay_success': 8,
    'pay_receipt': 9,
    'pay_cancel': 10,
    'withdraw_scan': 11,
    'withdraw_confirm': 12,
    'withdraw_success': 13,
    'withdraw_receipt': 14,
    'errors': 15,
}

SCREEN_BRIGHTNESS = 40

try:
    from xbterminal.nuitka_fix import BASE_DIR
except ImportError:
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))

PROJECT_LOCAL_PATH = os.path.join(BASE_DIR, 'xbterminal')

RUNTIME_PATH = os.path.join(PROJECT_LOCAL_PATH, 'runtime')
BATCH_NUMBER_FILE_PATH = os.path.join(RUNTIME_PATH, 'batch_number')
DEVICE_KEY_FILE_PATH = os.path.join(RUNTIME_PATH, 'device_key')
LOCAL_CONFIG_FILE_PATH = os.path.join(RUNTIME_PATH, 'local_config')
REMOTE_CONFIG_CACHE_FILE_PATH = os.path.join(RUNTIME_PATH, 'remote_config_cache')
SECRET_KEY_FILE_PATH = os.path.join(RUNTIME_PATH, 'secret_key')
LOG_FILE_PATH = os.path.join(RUNTIME_PATH, 'app.log')
QR_IMAGE_PATH = os.path.join(RUNTIME_PATH, 'qr.png')

UI_TRANSLATIONS_PATH = os.path.join(PROJECT_LOCAL_PATH, 'gui', 'ts')
UI_DEFAULT_LANGUAGE = 'en'
UI_THEMES_PATH = os.path.join(PROJECT_LOCAL_PATH, 'gui', 'themes')
UI_DEFAULT_THEME = 'default'

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
        'file': {
            'class': 'logging.FileHandler',
            'level': 'WARNING',
            'formatter': 'simple',
            'filename': LOG_FILE_PATH,
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
        'requests.packages.urllib3.connectionpool': {
            'level': 'WARNING',
        },
        'urllib3.connectionpool': {
            'level': 'WARNING',
        },
    },
}

REMOTE_SERVERS = {
    'main': 'https://xbterminal.io',
    'dev': 'http://stage.xbterminal.com',
}
REMOTE_CONFIG_UPDATE_CYCLE = 60  # seconds between remote config updates

REMOTE_API_ENDPOINTS = {
    'registration': '/api/v2/devices/',
    'config': '/api/v2/devices/{device_key}/',
    'payment_init': '/api/v2/payments/',
    'payment_response': '/api/v2/payments/{uid}/response/',
    'payment_check': '/api/v2/payments/{uid}/',
    'payment_receipt': '/prc/{uid}/',
    'withdrawal_init': '/api/v2/withdrawals/',
    'withdrawal_confirm': '/api/v2/withdrawals/{uid}/confirm/',
    'withdrawal_check': '/api/v2/withdrawals/{uid}/',
    'withdrawal_receipt': '/wrc/{uid}/',
}
EXTERNAL_CALLS_TIMEOUT = 15
EXTERNAL_CALLS_REQUEST_HEADERS = {'User-Agent': 'XBTerminal type 1'}

TRANSACTION_TIMEOUT = 900  # in person transaction timeout in seconds
TRANSACTION_CANCELLED_MESSAGE_TIMEOUT = 60  # if transaction cancelled - how long to show "cancelled" message in seconds

OUTPUT_DEC_PLACES = 2  # fractional decimal places to show on screen

BITCOIN_SCALE_DIVIZER = 1000  # 1 for BTC, 1000 for mBTC, 1000000 for uBTC
BITCOIN_OUTPUT_DEC_PLACES = 5

FIAT_DEC_PLACES = Decimal('0.00000000')
BTC_DEC_PLACES = Decimal('0.00000000')
