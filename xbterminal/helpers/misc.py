# -*- coding: utf-8 -*-
from decimal import Decimal

import xbterminal
import xbterminal.defaults


def splitThousands(number, separator):
    if len(number) <= 3:
        return number
    return splitThousands(number[:-3], separator) + separator + number[-3:]

def strrepeat(string_to_expand, length):
    return (string_to_expand * ((length/len(string_to_expand))+1))[:length]

def strpad(string_to_pad, chars_to_pad, length_to_pad, pad_left=False, pad_right=False):
    if len(string_to_pad) >= length_to_pad:
        return string_to_pad

    pad_length = length_to_pad - len(string_to_pad)
    pad_string = strrepeat(chars_to_pad, pad_length)
    if pad_left:
        return pad_string + string_to_pad
    elif pad_right:
        return string_to_pad + pad_string
    else:
        return string_to_pad

def satoshi2BTC(satoshi):
    satoshi = Decimal(satoshi)
    btc = satoshi / Decimal('100000000')
    return btc.quantize(xbterminal.defaults.BTC_DEC_PLACES)

def BTC2satoshi(btc):
    satoshi = btc * Decimal('100000000')
    return int(satoshi)
