# coding=utf-8
import os
from decimal import Decimal

import xbterminal.helpers
import xbterminal.helpers.misc


STAGES = {'payment': {'enter_amount': 'enter_amount',
                      'pay_nfc': 'pay_nfc',
                      'pay_qr': 'pay_qr',
                      'pay_qr_addr_only': 'pay_qr_addr_only',
                      'payment_successful': 'payment_successful',
                      'payment_cancelled': 'payment_cancelled',
                      'prepare_payment': 'prepare_payment',
                        },
          'wifi': {'choose_ssid': 'choose_ssid',
                   'enter_passkey': 'enter_passkey',
                   'connected': 'connected',
                    },
          'default': 'standby',
          'application_halt': 'application_halt',
          }

PROJECT_ABS_PATH = '' #initialized in bootstrap.py
PROJECT_LOCAL_PATH = 'xbterminal/'
DEVICE_KEY_FILE_PATH = os.path.join(PROJECT_LOCAL_PATH,'device_key')
RUNTIME_PATH = os.path.join(PROJECT_LOCAL_PATH,'runtime')
LOG_FILE_PATH = os.path.join(RUNTIME_PATH,'app.log')
QR_IMAGE_PATH = os.path.join(RUNTIME_PATH,'qr.png')
STATE_FILE_PATH = os.path.join(RUNTIME_PATH,'local_state')
REMOTE_CONFIG_CACHE_FILE_PATH = os.path.join(RUNTIME_PATH,'remote_config_cache')

LOG_MESSAGE_TYPES = {'DEBUG':'DEBUG',
                     'ERROR':'ERROR',
                     'WARNING':'WARNING',
                     }
LOG_LEVELS = {'DEBUG':'DEBUG',
              'PRODUCTION':'PRODUCTION',
                     }

REMOTE_SERVERS = ('xbterminal.com',)
REMOTE_SERVER_CONFIG_URL_TEMPLATE = 'http://{server_address}/config.json?device_key={device_key}'

TRANSACTION_TIMEOUT = 300 #in person transaction timeout in seconds
TRANSACTION_CANCELLED_MESSAGE_TIMEOUT = 10 #if transaction cancelled - how long to show "cancelled" message in seconds

EXTERNAL_CALLS_TIMEOUT = 15
EXTERNAL_CALLS_REQUEST_HEADERS = {'User-Agent': 'XBTerminal query bot',
                                  'Origin': 'XBTerminal device',
                                  }
OUTPUT_DEC_PLACES = 2 #fractional decimal places to show on screen
OUTPUT_TOTAL_PLACES = 7 #total decimal places to show on screen

FIAT_DEC_PLACES = Decimal('0.00000000')
BTC_DEC_PLACES  = Decimal('0.00000000')
BTC_DEFAULT_FEE = Decimal('0.00010000') #typical transaction expected to be less than 1024 bytes
BTC_MIN_OUTPUT  = Decimal('0.00005460') #minimal tx output

BITCOIND_HOST = '127.0.0.1'
BITCOIND_PORT = 8332
BITCOIND_USER = 'root'
BITCOIND_PASS = 'password'
BITCOIND_BLOCKCHAIN_SERVERS_KEYS_PATH = '/root/.ssh'
BITCOIND_BLOCKCHAIN_SERVERS = ({'name': 'BBB',
                                'addr': '192.168.51.122',
                                'port': '22',
                                'user': 'root',
                                'pass': 'root',
                                'path': '/root/.bitcoin',
                                }, )
BITCOIND_MAX_BLOCKCHAIN_AGE = 3600 #if is blockchain more than X seconds old - we do rsync to trusted blockchain servers to download blocks and index and catch up quickly