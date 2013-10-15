from decimal import Decimal


def formatDefaultAmountOutput():
    global OUTPUT_DEC_PLACES, OUTPUT_DEC_FRACTIONAL_SPLIT

    def strrepeat(string_to_expand, length):
        return (string_to_expand * ((length/len(string_to_expand))+1))[:length]

    decimal_part = '_'
    fractional_part = strrepeat('_', OUTPUT_DEC_PLACES)

    default_amount_output = '%s%s%s' % (decimal_part, OUTPUT_DEC_FRACTIONAL_SPLIT, fractional_part)
    return default_amount_output


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
OUTPUT_DEC_FRACTIONAL_SPLIT = '.'
OUTPUT_DEC_THOUSANDS_SPLIT = ','
OUTPUT_DEFAULT_VALUE = formatDefaultAmountOutput()

FIAT_DEC_PLACES = Decimal('0.0000')
BTC_DEC_PLACES = Decimal('0.00000000')


#########################################
# to be moved to online config
MERCHANT_CURRENCY = 'GBP'
OUR_FEE_SHARE = Decimal(0.005).quantize(BTC_DEC_PLACES)  #0.5%
INSTANT_FIAT_SHARE = Decimal(0.8).quantize(BTC_DEC_PLACES)  #80% converted to fiat instantly
INSTANT_FIAT_EXCHANGE_SERVICE = 'bitcoinaverage'


