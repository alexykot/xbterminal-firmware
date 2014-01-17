# -*- coding: utf-8 -*-
import os
import time
from decimal import Decimal
from email import utils

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

def log(message_text, message_type=None):
    global xbterminal
    if message_type is None:
        message_type = xbterminal.defaults.LOG_MESSAGE_TYPES['DEBUG']

    timestamp = utils.formatdate(time.time())

    log_abs_path = os.path.abspath(os.path.join(xbterminal.defaults.PROJECT_ABS_PATH, xbterminal.defaults.LOG_FILE_PATH))

    if (message_type == xbterminal.defaults.LOG_MESSAGE_TYPES['DEBUG']
        and hasattr(xbterminal, 'remote_config')
        and 'LOG_LEVEL' in xbterminal.remote_config
        and xbterminal.remote_config['LOG_LEVEL'] != xbterminal.defaults.LOG_LEVELS['DEBUG']):
        return

    with open(log_abs_path, 'a') as log_file:
        log_string = '%s; %s: %s' % (timestamp, message_type, message_text)
        if (not hasattr(xbterminal, 'remote_config')
            or 'LOG_LEVEL' not in xbterminal.remote_config
            or xbterminal.remote_config['LOG_LEVEL'] == xbterminal.defaults.LOG_LEVELS['DEBUG']):
            print log_string
        log_file.write(log_string+'\n')


