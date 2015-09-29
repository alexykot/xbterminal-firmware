import os
from decimal import Decimal


STAGES = {
    'bootup': 'bootup',
    'activate': 'activate',
    'wifi': {
        'choose_ssid': 'choose_ssid',
        'enter_passkey': 'enter_passkey',
        'wifi_connected': 'wifi_connected',
    },
    'idle': 'idle',
    'payment': {
        'pay_amount': 'pay_amount',
        'pay_loading': 'pay_loading',
        'pay_wait': 'pay_wait',
        'pay_success': 'pay_success',
        'pay_cancel': 'pay_cancel',
    },
    'withdrawal': {
        'withdraw_amount': 'withdraw_amount',
        'withdraw_loading1': 'withdraw_loading1',
        'withdraw_scan': 'withdraw_scan',
        'withdraw_confirm': 'withdraw_confirm',
        'withdraw_loading2': 'withdraw_loading2',
        'withdraw_success': 'withdraw_success',
    },
    'application_halt': 'application_halt',
}

SCREENS = {
    'load_indefinite': 0,
    'activation': 1,
    'choose_ssid': 2,
    'enter_passkey': 3,
    'wifi_connected': 4,
    'idle': 5,
    'enter_amount': 6,
    'pay_wait': 7,
    'pay_success': 8,
    'pay_cancel': 9,
    'withdraw_scan': 10,
    'withdraw_confirm': 11,
    'withdraw_success': 12,
    'errors': 13,
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

UI_IMAGES_PATH = os.path.join(PROJECT_LOCAL_PATH, 'gui', 'images')
UI_FONTS_PATH = os.path.join(PROJECT_LOCAL_PATH, 'gui', 'fonts')
UI_TRANSLATIONS_PATH = os.path.join(PROJECT_LOCAL_PATH, 'gui', 'ts')
UI_DEFAULT_LANGUAGE = 'en'

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
    'receipt': '/rc/{receipt_key}/',
    'payment_init': '/api/payments/init/',
    'payment_response': '/api/payments/{payment_uid}/response/',
    'payment_check': '/api/payments/{payment_uid}/check/',
    'withdrawal_init': '/api/withdrawals/',
    'withdrawal_confirm': '/api/withdrawals/{uid}/confirm/',
    'withdrawal_check': '/api/withdrawals/{uid}/',
}
EXTERNAL_CALLS_TIMEOUT = 15
EXTERNAL_CALLS_REQUEST_HEADERS = {'User-Agent': 'XBTerminal type 1'}

TRANSACTION_TIMEOUT = 900  # in person transaction timeout in seconds
TRANSACTION_CANCELLED_MESSAGE_TIMEOUT = 60  # if transaction cancelled - how long to show "cancelled" message in seconds

OUTPUT_DEC_PLACES = 2  # fractional decimal places to show on screen
OUTPUT_TOTAL_PLACES = 7  # total decimal places to show on screen

EXCHANGE_RATE_DEC_PLACES = 3  # fractional decimal places for exchange rate to show on screen

BITCOIN_SCALE_DIVIZER = 1000  # 1 for BTC, 1000 for mBTC, 1000000 for uBTC
BITCOIN_OUTPUT_DEC_PLACES = 2

SATOSHI_FACTOR = Decimal(100000000)  # satoshis per BTC
FIAT_DEC_PLACES = Decimal('0.00000000')
BTC_DEC_PLACES = Decimal('0.00000000')
BTC_DEFAULT_FEE = Decimal('0.00010000')  # typical transaction expected to be less than 1024 bytes
BTC_MIN_OUTPUT = Decimal('0.00005460')  # minimal tx output
