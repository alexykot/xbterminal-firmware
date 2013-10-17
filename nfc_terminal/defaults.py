# coding=utf-8
from decimal import Decimal

import nfc_terminal.helpers
import nfc_terminal.helpers.misc


#########################################
# to be moved to online config
MERCHANT_CURRENCY = 'GBP'
MERCHANT_CURRENCY_SIGN_PREFIX = u'£'
MERCHANT_CURRENCY_SIGN_POSTFIX = ''
OUR_FEE_SHARE = 0.005 #0.5%
INSTANT_FIAT_SHARE = 0.8 #80% converted to fiat instantly
INSTANT_FIAT_EXCHANGE_SERVICE = 'bitcoinaverage'
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
CONFIG_FILE_PATH = 'nfc_terminal/config.json'
LOG_FILE_PATH = 'nfc_terminal/runtime/app.log'
LOG_MESSAGE_TYPES = {'DEBUG':'DEBUG',
                     'ERROR':'ERROR',
                     'WARNING':'WARNING',
                     }
LOG_LEVELS = {'DEBUG':'DEBUG',
              'PRODUCTION':'PRODUCTION',
                     }

EXTERNAL_CALLS_TIMEOUT = 15
EXTERNAL_CALLS_REQUEST_HEADERS = {'User-Agent': 'nfc_post query bot',
                                  'Origin': 'nfc_post',
                                  }
OUTPUT_DEC_PLACES = 2 #fractional decimal places to show on screen
OUTPUT_TOTAL_PLACES = 9 #total decimal places to show on screen
OUTPUT_DEC_FRACTIONAL_SPLIT = '.'
OUTPUT_DEC_THOUSANDS_SPLIT = ','
#OUTPUT_DEFAULT_VALUE = nfc_terminal.helpers.misc.formatDefaultAmountOutput(OUTPUT_DEC_PLACES, OUTPUT_DEC_FRACTIONAL_SPLIT)

DISPLAY_DEFAULT_VALUE = None
DISPLAY_RUN_VALUE = None

FIAT_DEC_PLACES = Decimal('0.0000')
BTC_DEC_PLACES = Decimal('0.00000000')



