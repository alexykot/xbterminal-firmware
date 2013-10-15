from decimal import Decimal

from nfc_terminal import defaults
import exchange_servers
from exchange_servers import bitcoinaverage


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

    our_fee_btc_amount = bitcoinaverage.convertToBtc(our_fee_fiat_amount, defaults.MERCHANT_CURRENCY)
    instantfiat_btc_amount = getattr(exchange_servers, defaults.INSTANT_FIAT_EXCHANGE_SERVICE).convertToBtc(instantfiat_fiat_amount, defaults.MERCHANT_CURRENCY)
    merchants_btc_fiat_amount = exchange_servers.bitcoinaverage.convertToBtc(merchants_btc_fiat_amount, defaults.MERCHANT_CURRENCY)

    return our_fee_btc_amount, instantfiat_btc_amount, merchants_btc_fiat_amount

def getInstantFiatBtcAddress(instantfiat_fiat_amount):
    pass

def getMerchantBtcAddress(instantfiat_fiat_amount):
    global nfc_terminal

    return nfc_terminal.config['merchant_btc_address']

def processAmountKeyInput(current_text, key_code):
    def splitThousands(number, separator):
        if len(number) <= 3:
            return number
        return splitThousands(number[:-3], separator) + separator + number[-3:]

    global nfc_terminal

    key_code = str(key_code)
    current_text = current_text.split(defaults.OUTPUT_DEC_FRACTIONAL_SPLIT)
    if len(current_text) != 2:
        return defaults.OUTPUT_DEFAULT_VALUE

    decimal_part = current_text[0]
    fractional_part = current_text[1]

    if key_code == '.':
        nfc_terminal.runtime['current_text_piece'] = 'fractional'
        return current_text
    elif key_code == 'A':
        if nfc_terminal.runtime['current_text_piece'] == 'decimal':
            decimal_part = decimal_part[:-1]
        elif nfc_terminal.runtime['current_text_piece'] == 'fractional':

        nfc_terminal.runtime['entered_text'] = nfc_terminal.runtime['entered_text'][:-1]
    elif key_code == 'B':
        return defaults.OUTPUT_DEFAULT_VALUE
    else:
        if nfc_terminal.runtime['current_text_piece'] == 'decimal':
            decimal_part = '%s%s' % (decimal_part, key_code)

        if nfc_terminal.runtime['current_text_piece'] == 'fractional':
            fractional_part = fractional_part.rstrip('0')
            if len(fractional_part < 2):
                fractional_part = '%s%s' % (fractional_part, key_code)

    resulting_text = '%s.%s' % (decimal_part, fractional_part)
    return resulting_text

