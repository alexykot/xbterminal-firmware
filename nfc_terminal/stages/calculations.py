from decimal import Decimal

from nfc_terminal import defaults
from nfc_terminal import exchange_servers


class NotImplemented(Exception):
    exchange_name = None
    strerror = u'not implemented'


def getTransactionAddress():
    raise NotImplemented()


def getTotalBtcAmount(total_fiat_amount):
    total_fiat_amount = Decimal(total_fiat_amount).quantize(defaults.DEC_PLACES)
    our_fee_fiat_amount = total_fiat_amount * defaults.OUR_FEE_SHARE
    instanttofiat_fiat_amount = total_fiat_amount * defaults.INSTANT_FIAT_SHARE
    merchants_btc_fiat_amount = total_fiat_amount - instanttofiat_fiat_amount - our_fee_fiat_amount

    our_fee_btc_amount = exchange_servers.bitcoinaverage.convertToBtc(our_fee_fiat_amount, defaults.MERCHANT_CURRENCY)
    instanttofiat_btc_amount = getattr(exchange_servers, defaults.INSTANT_FIAT_EXCHANGE_SERVICE).convertToBtc(instanttofiat_fiat_amount, defaults.MERCHANT_CURRENCY)
    merchants_btc_fiat_amount = exchange_servers.bitcoinaverage.convertToBtc(merchants_btc_fiat_amount, defaults.MERCHANT_CURRENCY)

    total_btc_amount = our_fee_btc_amount + instanttofiat_btc_amount + merchants_btc_fiat_amount
    return total_btc_amount


