# -*- coding: utf-8 -*-
from decimal import Decimal
import logging
from eventlet.green import urllib2
from eventlet.timeout import Timeout
import json
import simplejson
import socket
from eventlet.green import httplib
import sys

from xbterminal import defaults
from xbterminal.exceptions import NetworkError, CurrencyNotRecognized
from xbterminal.helpers.misc import log


BA_TICKER_API_URL = "https://api.bitcoinaverage.com/ticker/{currency_code}/last"

def getExchangeRate(currency_code):
    try:
        with Timeout(defaults.EXTERNAL_CALLS_TIMEOUT):
            ticker_result = urllib2.urlopen(urllib2.Request(url=BA_TICKER_API_URL.format(currency_code=currency_code),
                                                       headers=defaults.EXTERNAL_CALLS_REQUEST_HEADERS)).read()
    except (KeyError,
            ValueError,
            socket.error,
            simplejson.decoder.JSONDecodeError,
            urllib2.URLError,
            httplib.BadStatusLine) as error:
        logging.exception(error)
        raise NetworkError()

    return Decimal(ticker_result)
