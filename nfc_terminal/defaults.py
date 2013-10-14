from decimal import Decimal

STAGES = ('standby',
          'enter_amount',
          'pay_nfc',
          'pay_qr',
          'payment_successful',
          'payment_cancelled',
            )
CURRENT_STAGE = None
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
GUI_STATE = 'inactive'
ENTERED_AMOUNT = None

EXTERNAL_CALLS_TIMEOUT = 15
EXTERNAL_CALLS_REQUEST_HEADERS = {'User-Agent': 'nfc_post query bot',
                                  'Origin': 'nfc_post',
                                  }
DEC_PLACES = Decimal('0.0000')


#########################################
# to be moved to online config
MERCHANT_CURRENCY = 'GBP'
OUR_FEE_SHARE = Decimal(0.005).quantize(DEC_PLACES)  #0.5%
INSTANT_FIAT_SHARE = Decimal(0.8).quantize(DEC_PLACES)  #80% converted to fiat instantly
INSTANT_FIAT_EXCHANGE_SERVICE = 'bitcoinaverage'
