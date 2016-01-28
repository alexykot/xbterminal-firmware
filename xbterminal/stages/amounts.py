from decimal import Decimal, ROUND_FLOOR

import xbterminal
from xbterminal.defaults import (
    OUTPUT_DEC_PLACES,
    BITCOIN_SCALE_DIVIZER,
    BITCOIN_OUTPUT_DEC_PLACES,
    EXCHANGE_RATE_DEC_PLACES)


def format_amount(amount, dec_places=OUTPUT_DEC_PLACES):
    quantum = Decimal(1) / 10 ** dec_places
    integer_part = amount.quantize(0, ROUND_FLOOR)
    fractional_part = (amount - integer_part).quantize(quantum)
    thousand_sep = xbterminal.runtime['remote_config']['language']['thousands_split']
    decimal_sep = xbterminal.runtime['remote_config']['language']['fractional_split']
    return '{0}{1}{2}'.format(format(integer_part, thousand_sep),
                              decimal_sep,
                              str(fractional_part)[2:])


def format_amount_cur(amount):
    quantum = Decimal(1) / 10 ** OUTPUT_DEC_PLACES
    integer_part = amount.quantize(0, ROUND_FLOOR)
    fractional_part = (amount - integer_part).quantize(quantum)
    thousand_sep = xbterminal.runtime['remote_config']['language']['thousands_split']
    decimal_sep = xbterminal.runtime['remote_config']['language']['fractional_split']
    currency_prefix = xbterminal.runtime['remote_config']['currency']['prefix']
    return u'{0}{1}{2}{3}'.format(currency_prefix,
                                  format(integer_part, thousand_sep),
                                  decimal_sep,
                                  str(fractional_part)[2:])


def format_btc_amount(amount):
    amount_scaled = amount * BITCOIN_SCALE_DIVIZER
    return format_amount(amount_scaled, BITCOIN_OUTPUT_DEC_PLACES)


def format_exchange_rate(rate):
    rate_scaled = rate / BITCOIN_SCALE_DIVIZER
    return format_amount(rate_scaled, EXCHANGE_RATE_DEC_PLACES)
