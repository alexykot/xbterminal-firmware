# -*- coding: utf-8 -*-
from decimal import Decimal, ROUND_FLOOR

from xbterminal.defaults import (
    OUTPUT_DEC_PLACES,
    BITCOIN_SCALE_DIVIZER,
    BITCOIN_OUTPUT_DEC_PLACES)
from xbterminal.state import gui_state as state


FIAT_AMOUNT_TEMPLATE = u'{prefix}{integer}{dsep}{frac}'
BTC_AMOUNT_TEMPLATE = (
    u'<html><head/><body>'
    u'{prefix}{integer}{dsep}{frac1}'
    u'<span style="font-size: {frac2_size};">{frac2}</span>'
    u'</body></html>')
EXCHANGE_RATE_TEMPLATE = u'1 BTC = {rate}'


def format_fiat_amount_pretty(value, prefix=False):
    quantum = Decimal(1) / 10 ** OUTPUT_DEC_PLACES
    integer_part = value.quantize(0, ROUND_FLOOR)
    fractional_part = (value - integer_part).quantize(quantum)
    thousand_sep = state['remote_config']['language']['thousands_split']
    decimal_sep = state['remote_config']['language']['fractional_split']
    currency_prefix = state['remote_config']['currency']['prefix']
    return FIAT_AMOUNT_TEMPLATE.format(
        prefix=currency_prefix if prefix else '',
        integer=format(integer_part, thousand_sep),
        dsep=decimal_sep,
        frac=str(fractional_part)[2:])


def format_btc_amount_pretty(value, prefix=False, frac2_size='small'):
    value_scaled = value * BITCOIN_SCALE_DIVIZER
    quantum = Decimal(1) / 10 ** BITCOIN_OUTPUT_DEC_PLACES
    integer_part = value_scaled.quantize(0, ROUND_FLOOR)
    fractional_part = (value_scaled - integer_part).quantize(quantum)
    thousand_sep = state['remote_config']['language']['thousands_split']
    decimal_sep = state['remote_config']['language']['fractional_split']
    return BTC_AMOUNT_TEMPLATE.format(
        prefix=u'm฿' if prefix else '',
        integer=format(integer_part, thousand_sep),
        dsep=decimal_sep,
        frac1=str(fractional_part)[2:4],
        frac2=str(fractional_part)[4:7],
        frac2_size=frac2_size)


def format_exchange_rate_pretty(value):
    return EXCHANGE_RATE_TEMPLATE.format(
        rate=format_fiat_amount_pretty(value, prefix=True))
