# -*- coding: utf-8 -*-

class CurrencyNotRecognized(Exception):
    exchange_name = None
    strerror = u'currency code not recognized'

class NetworkError(Exception):
    exchange_name = None
    strerror = u'network error while retrieving price'

class NotEnoughFunds(Exception):
    exchange_name = None
    strerror = u'not enough funds for transaction'

class PrivateKeysMissing(Exception):
    exchange_name = None
    strerror = u'private keys required for transaction signing are missing'
