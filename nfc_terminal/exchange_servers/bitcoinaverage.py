from decimal import Decimal
from eventlet.green import urllib2
from eventlet.timeout import Timeout
import json
import simplejson
import socket
from eventlet.green import httplib
import sys

from nfc_terminal import defaults
from nfc_terminal.helpers.log import write_msg_log


class CurrencyNotRecognized(Exception):
    exchange_name = None
    strerror = u'currency code not recognized'

class NetworkError(Exception):
    exchange_name = None
    strerror = u'network error while retrieving price'


BA_TICKER_API_URL = "https://api.bitcoinaverage.com/ticker/all"

def getExchangeRate(cls, currency_code):
    try:
        with Timeout(defaults.EXTERNAL_CALLS_TIMEOUT):
            response = urllib2.urlopen(urllib2.Request(url=BA_TICKER_API_URL, headers=defaults.EXTERNAL_CALLS_REQUEST_HEADERS)).read()
            ticker_result = json.loads(response)
    except (KeyError,
            ValueError,
            socket.error,
            simplejson.decoder.JSONDecodeError,
            urllib2.URLError,
            httplib.BadStatusLine) as error:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        write_msg_log('exception %s occured while retreiving price from bitcoinaverage.com' % exc_type, 'ERROR')
        raise NetworkError()

    try:
        return Decimal(ticker_result[currency_code]['last'])
    except KeyError:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        write_msg_log('exception %s occured while retreiving price from bitcoinaverage.com' % exc_type, 'ERROR')
        raise CurrencyNotRecognized()

def convertToBtc(self, price_fiat, currency_code):
    rate_btc = self.getExchangeRate(currency_code)
    price_fiat = Decimal(price_fiat).quantize(defaults.FIAT_DEC_PLACES)
    price_btc = price_fiat / rate_btc
    return price_btc

def convertToFiat(self, price_btc, currency_code):
    rate_btc = self.getExchangeRate(currency_code)
    price_btc = Decimal(price_btc).quantize(defaults.BTC_DEC_PLACES)
    price_fiat = price_btc * rate_btc
    return price_fiat
