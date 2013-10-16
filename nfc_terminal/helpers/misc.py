# -*- coding: utf-8 -*-

import nfc_terminal
import nfc_terminal.defaults


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

def formatDefaultAmountOutput(decimal_places, fractional_split):
    decimal_part = '_'
    fractional_part = strrepeat('_', decimal_places)

    default_amount_output = '%s%s%s' % (decimal_part, fractional_split, fractional_part)
    return default_amount_output

