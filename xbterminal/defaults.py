import os
from decimal import Decimal


STAGES = {'payment': {'enter_amount': 'enter_amount',
                      'pay_loading': 'pay_loading',
                      'pay_rates': 'pay_rates',
                      'pay': 'pay',
                      'pay_success': 'pay_success',
                      'pay_cancel': 'pay_cancel',
                        },
          'wifi': {'choose_ssid': 'choose_ssid',
                   'enter_passkey': 'enter_passkey',
                   'wifi_connected': 'wifi_connected',
                    },
          'idle': 'idle',
          'bootup': 'bootup',
          'application_halt': 'application_halt',
          'system_halt': 'system_halt',
          }

SCREENS = {'load_percent': 0,
           'load_indefinite': 1,
           'choose_ssid': 2,
           'enter_passkey': 3,
           'wifi_connected': 4,
           'idle': 5,
           'enter_amount': 6,
           'pay_rates': 7,
           'pay_nfc': 8,
           'pay_qr': 9,
           'pay_success': 10,
           'pay_cancel': 11,
           'errors': 12,
    }

SCREEN_BRIGHTNESS = 40

LOAD_PROGRESS_LEVELS = {'runtime_init': 2,
                        'gui_init': 2,
                        'keypad_init': 6,
                        'wifi_init': 35,
                        'remote_config_load': 50,
                        'blockchain_init': 95,
                        'finish': 100,
                        }

PROJECT_ABS_PATH = ''  # initialized in main.py
PROJECT_LOCAL_PATH = 'xbterminal'
DEVICE_KEY_FILE_PATH = os.path.join(PROJECT_LOCAL_PATH, 'device_key')
RUNTIME_PATH = os.path.join(PROJECT_LOCAL_PATH, 'runtime')
LOG_FILE_PATH = os.path.join(RUNTIME_PATH, 'app.log')
QR_IMAGE_PATH = os.path.join(RUNTIME_PATH, 'qr.png')
STATE_FILE_PATH = os.path.join(RUNTIME_PATH, 'local_state')
REMOTE_CONFIG_CACHE_FILE_PATH = os.path.join(RUNTIME_PATH, 'remote_config_cache')
UI_IMAGES_PATH = os.path.join(PROJECT_LOCAL_PATH, 'gui', 'images')
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
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'DEBUG',
    },
}

REMOTE_SERVERS = ('https://xbterminal.io',
                  'https://xbterminal.com',
                    )
REMOTE_CONFIG_UPDATE_CYCLE = 60 #seconds between remote config updates

REMOTE_API_ENDPOINTS = {'config': '/api/devices/{device_key}/',
                        'tx_log': '/api/transactions/create/',
                        'receipt': '/api/receipts/{receipt_key}/',
                        'firmware_check': '/api/device/{device_key}/firmware/',
                        'firmware_download': '/api/device/{device_key}/firmware/{firmware_hash}',
                        'firmware_updated': '/api/device/{device_key}/firmware_updated/',
                        'payment_init': '/api/payments/init',
                        'payment_response': '/api/payments/{payment_uid}/response',
                        'payment_check': '/api/payments/{payment_uid}/check',
                        }
EXTERNAL_CALLS_TIMEOUT = 15
EXTERNAL_CALLS_REQUEST_HEADERS = {'User-Agent': 'XBTerminal type 1',
                                  'Origin': 'terminal #{serial_number}', #initiated in configs helper
                                  }

TRANSACTION_TIMEOUT = 900 #in person transaction timeout in seconds
TRANSACTION_CANCELLED_MESSAGE_TIMEOUT = 60 #if transaction cancelled - how long to show "cancelled" message in seconds

OUTPUT_DEC_PLACES = 2 #fractional decimal places to show on screen
OUTPUT_TOTAL_PLACES = 7 #total decimal places to show on screen

EXCHANGE_RATE_DEC_PLACES = 3 #fractional decimal places for exchange rate to show on screen

BITCOIN_SCALE_DIVIZER = 1000 #1 for BTC, 1000 for mBTC, 1000000 for uBTC
BITCOIN_OUTPUT_DEC_PLACES = 2

SATOSHI_FACTOR = Decimal(100000000) #satoshis per BTC
FIAT_DEC_PLACES = Decimal('0.00000000')
BTC_DEC_PLACES  = Decimal('0.00000000')
BTC_DEFAULT_FEE = Decimal('0.00010000') #typical transaction expected to be less than 1024 bytes
BTC_MIN_OUTPUT  = Decimal('0.00005460') #minimal tx output
