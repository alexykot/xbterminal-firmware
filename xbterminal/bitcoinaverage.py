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
