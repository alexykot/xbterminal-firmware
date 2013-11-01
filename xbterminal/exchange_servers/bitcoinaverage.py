# -*- coding: utf-8 -*-
from decimal import Decimal
from eventlet.green import urllib2
from eventlet.timeout import Timeout
import json
import simplejson
import socket
from eventlet.green import httplib
import sys

from xbterminal import defaults
from xbterminal.exceptions import NetworkError, CurrencyNotRecognized
from xbterminal.helpers.log import write_msg_log


BA_TICKER_API_URL = "https://api.bitcoinaverage.com/ticker/all"

def getPaymentAddress(amount):
    return '1G2bcoCKj8s9GYheqQgU5CHSLCtGjyP9Vz' #my default main address in bitcoinqt wallet

def getExchangeRate(currency_code):
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
        write_msg_log('exception %s occured while retrieving price from bitcoinaverage.com' % exc_type, 'ERROR')
        raise NetworkError()

    try:
        return Decimal(ticker_result[currency_code]['last'])
    except KeyError:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        write_msg_log('exception %s occured while retrieving price from bitcoinaverage.com' % exc_type, 'ERROR')
        raise CurrencyNotRecognized()

def convertToBtc(price_fiat, currency_code):
    rate_btc = getExchangeRate(currency_code)
    price_fiat = Decimal(price_fiat).quantize(defaults.FIAT_DEC_PLACES)
    price_btc = Decimal(price_fiat / rate_btc).quantize(defaults.BTC_DEC_PLACES)
    return price_btc

def convertToFiat(price_btc, currency_code):
    rate_btc = getExchangeRate(currency_code)
    price_btc = Decimal(price_btc).quantize(defaults.BTC_DEC_PLACES)
    price_fiat = Decimal(price_btc * rate_btc).quantize(defaults.FIAT_DEC_PLACES)
    return price_fiat
