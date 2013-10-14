from decimal import Decimal

from nfc_terminal import defaults
from nfc_terminal import exchange_servers


class NotImplemented(Exception):
    exchange_name = None
    strerror = u'not implemented'


def getTransactionAddress():
    raise NotImplemented()


def getBtcSharesAmounts(total_fiat_amount):
    total_fiat_amount = Decimal(total_fiat_amount).quantize(defaults.FIAT_DEC_PLACES)
    our_fee_fiat_amount = total_fiat_amount * defaults.OUR_FEE_SHARE
    instantfiat_fiat_amount = total_fiat_amount * defaults.INSTANT_FIAT_SHARE
    merchants_btc_fiat_amount = total_fiat_amount - instantfiat_fiat_amount - our_fee_fiat_amount

    our_fee_btc_amount = exchange_servers.bitcoinaverage.convertToBtc(our_fee_fiat_amount, defaults.MERCHANT_CURRENCY)
    instantfiat_btc_amount = getattr(exchange_servers, defaults.INSTANT_FIAT_EXCHANGE_SERVICE).convertToBtc(instantfiat_fiat_amount, defaults.MERCHANT_CURRENCY)
    merchants_btc_fiat_amount = exchange_servers.bitcoinaverage.convertToBtc(merchants_btc_fiat_amount, defaults.MERCHANT_CURRENCY)

    return our_fee_btc_amount, instantfiat_btc_amount, merchants_btc_fiat_amount

def getInstantFiatBtcAddress(instantfiat_fiat_amount):
    pass

def getMerchantBtcAddress(instantfiat_fiat_amount):
    global nfc_terminal

    return nfc_terminal.config['merchant_btc_address']
