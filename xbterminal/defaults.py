# coding=utf-8
from decimal import Decimal

import xbterminal.helpers
import xbterminal.helpers.misc


#########################################
# to be moved to online config
MERCHANT_NAME = 'Test Merchant'
MERCHANT_TRANSACTION_DESCRIPTION = 'Test merchant'
MERCHANT_CURRENCY = 'GBP'
MERCHANT_CURRENCY_SIGN_PREFIX = u'£'
MERCHANT_CURRENCY_SIGN_POSTFIX = ''
MERCHANT_BITCOIN_ADDRESS = '1G2bcoCKj8s9GYheqQgU5CHSLCtGjyP9Vz' #my default main address in bitcoinqt wallet
MERCHANT_DEVICE_NAME = "bitcointerminal"
OUR_FEE_SHARE = 0.005 #0.5%
OUR_FEE_BITCOIN_ADDRESS = '1FCrwY2CsLJgsmbogSunECwCa6WswBBrfz' #test address for fees in my bitcoinqt wallet
MERCHANT_INSTANTFIAT_SHARE = 0.0 #converted to fiat instantly
MERCHANT_INSTANTFIAT_EXCHANGE_SERVICE = 'bips'
#MERCHANT_INSTANTFIAT_API_KEY = 'f8dafc7f7bbc000cfe4e01c604770f0e' #bips test API key
MERCHANT_INSTANTFIAT_API_KEY = 'yIPgOATBZ1WHvhvKE6tpOqOuzBh8PGeDN5JZBP46eCc' #bitpay test API key
MERCHANT_INSTANTFIAT_TRANSACTION_SPEED = 'high'
#########################################

STAGES = ('standby',
          'enter_amount',
          'pay_nfc',
          'pay_qr',
          'payment_successful',
          'payment_cancelled',
          'application_halt',
            )
PROJECT_ABS_PATH = '' #initialized in bootstrap.py
CONFIG_FILE_PATH = 'xbterminal/config.json'
QR_IMAGE_PATH = '' #initialised in bootstrap.py
LOG_FILE_PATH = 'xbterminal/runtime/app.log'
LOG_MESSAGE_TYPES = {'DEBUG':'DEBUG',
                     'ERROR':'ERROR',
                     'WARNING':'WARNING',
                     }
LOG_LEVELS = {'DEBUG':'DEBUG',
              'PRODUCTION':'PRODUCTION',
                     }

TRANSACTION_TIMEOUT = 300 #in person transaction timeout in seconds
TRANSACTION_CANCELLED_MESSAGE_TIMEOUT = 10 #if transaction cancelled - how long to show "cancelled" message in seconds


EXTERNAL_CALLS_TIMEOUT = 15
EXTERNAL_CALLS_REQUEST_HEADERS = {'User-Agent': 'XBTerminal query bot',
                                  'Origin': 'XBTerminal device',
                                  }
OUTPUT_DEC_PLACES = 2 #fractional decimal places to show on screen
OUTPUT_TOTAL_PLACES = 7 #total decimal places to show on screen
OUTPUT_DEC_FRACTIONAL_SPLIT = '.'
OUTPUT_DEC_THOUSANDS_SPLIT = ','

FIAT_DEC_PLACES = Decimal('0.00000000')
BTC_DEC_PLACES  = Decimal('0.00000000')
BTC_DEFAULT_FEE = Decimal('0.00010000') #typical transaction expected to be less than 1024 bytes
BTC_MIN_OUTPUT  = Decimal('0.00005460') #minimal tx output

BITCOIND_HOST = '127.0.0.1'  #set to 'localhost' to use localhost with no login/pass
BITCOIND_PORT = 8332
BITCOIND_USER = 'root'
BITCOIND_PASS = 'password'


