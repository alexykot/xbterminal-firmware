from decimal import Decimal

import nfc_terminal
from nfc_terminal import defaults
from nfc_terminal import exchange_servers


class NotImplemented(Exception):
    exchange_name = None
    strerror = u'not implemented'


def getTransactionAddress():
    raise NotImplemented()


def getBtcSharesAmounts(total_fiat_amount):
    global exchange_servers

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

def processAmountKeyInput(current_text, key_code):
    def splitThousands(number, separator):
        if len(number) <= 3:
            return number
        return splitThousands(number[:-3], separator) + separator + number[-3:]
    def strrepeat(string_to_expand, length):
        return (string_to_expand * ((length/len(string_to_expand))+1))[:length]

    def strpad(string_to_pad, chars_to_pad, length_to_pad, pad_left=False, pad_right=False):
        if len(string_to_pad) >= length_to_pad:
            return string_to_pad

        pad_lendth = length_to_pad - len(string_to_pad)
        pad_string = strrepeat(chars_to_pad, pad_lendth)
        if pad_left:
            return pad_string+string_to_pad
        elif pad_right:
            return string_to_pad+pad_string
        else:
            return string_to_pad

    global nfc_terminal

    key_code = str(key_code)
    current_text_split = current_text.split(defaults.OUTPUT_DEC_FRACTIONAL_SPLIT)
    if len(current_text_split) != 2:
        return defaults.OUTPUT_DEFAULT_VALUE

    decimal_part = current_text_split[0]
    decimal_part = decimal_part.replace(defaults.OUTPUT_DEC_THOUSANDS_SPLIT, '')
    fractional_part = current_text_split[1]

    if key_code == '.':
        nfc_terminal.runtime['current_text_piece'] = 'fractional'
        return current_text
    elif key_code == 'A':
        if nfc_terminal.runtime['current_text_piece'] == 'fractional':
            fractional_part = fractional_part.rstrip('_')
            if len(fractional_part) == 0:
                nfc_terminal.runtime['current_text_piece'] = 'decimal'
            else:
                fractional_part = fractional_part[:-1]
        if nfc_terminal.runtime['current_text_piece'] == 'decimal':
            fractional_part = fractional_part.lstrip('_')
            decimal_part = decimal_part[:-1]
    elif key_code == 'B':
        return defaults.OUTPUT_DEFAULT_VALUE
    else:
        if nfc_terminal.runtime['current_text_piece'] == 'decimal':
            decimal_part = decimal_part.lstrip('_')
            decimal_part = '%s%s' % (decimal_part, key_code)

        if nfc_terminal.runtime['current_text_piece'] == 'fractional':
            fractional_part = fractional_part.rstrip('_')
            if len(fractional_part) < defaults.OUTPUT_DEC_PLACES:
                fractional_part = '%s%s' % (fractional_part, key_code)

    decimal_part = strpad(decimal_part, '_', 1, pad_left=True)
    fractional_part = strpad(fractional_part, '_', defaults.OUTPUT_DEC_PLACES, pad_right=True)
    decimal_part = splitThousands(decimal_part, defaults.OUTPUT_DEC_THOUSANDS_SPLIT)
    resulting_text = '%s%s%s' % (decimal_part, defaults.OUTPUT_DEC_FRACTIONAL_SPLIT, fractional_part)
    return resulting_text

