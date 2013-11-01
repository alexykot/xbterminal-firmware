# -*- coding: utf-8 -*-
__author__ = 'tux'

from xbterminal import defaults


def formatUri(amount):
    uri = 'bitcoin:' + defaults.MERCHANT_BITCOIN_ADDRESS + '?label=' + defaults.MERCHANT_NAME + '&amount=' + str(amount)
    return uri