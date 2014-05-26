# -*- coding: utf-8 -*-

class CurrencyNotRecognized(Exception):
    exchange_name = None
    strerror = u'currency code not recognized'

class NetworkError(Exception):
    exchange_name = None
    strerror = u'network error while retrieving price'

class NotEnoughFunds(Exception):
    amount_available = None
    amount_to_spend = None
    strerror = u'not enough funds for transaction'
    def __init__(self, amount_available, amount_to_spend):
        self.amount_available = amount_available
        self.amount_to_spend = amount_to_spend
        super(NotEnoughFunds, self).__init__()


class PrivateKeysMissing(Exception):
    exchange_name = None
    strerror = u'private keys required for transaction signing are missing'

class ConfigLoadError(Exception):
    exchange_name = None
    strerror = u'configuration load failure'

class DeviceKeyMissingError(Exception):
    exchange_name = None
    strerror = u'device key missing'




class XBTerminalError(Exception):
    pass


class InvalidAddressError(XBTerminalError):

    def __init__(self, name, address):
        super(InvalidAddressError, self).__init__()
        self.name = name
        self.address = address

    def __str__(self):
        return "invalid '{0}' address: {1}".format(self.name, self.address)
