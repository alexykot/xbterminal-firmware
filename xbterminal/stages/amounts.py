from decimal import Decimal, ROUND_FLOOR

import xbterminal
from xbterminal.defaults import (
    OUTPUT_DEC_PLACES,
    OUTPUT_TOTAL_PLACES,
    BITCOIN_SCALE_DIVIZER,
    BITCOIN_OUTPUT_DEC_PLACES)


def process_key_input(amount, key=None):
    """
    Update amount according to pressed key
    Accepts:
        amount: Decimal
        key: number, '00' or 'backspace'
    """
    quantum = Decimal(1) / 10 ** OUTPUT_DEC_PLACES
    n_digits = len(str(amount.quantize(quantum))) - 1
    if key == 'backspace' and n_digits > 0:
        amount = amount / 10
    elif key in range(10) and n_digits + 1 <= OUTPUT_TOTAL_PLACES:
        amount = amount * 10 + quantum * key
    elif key == '00' and n_digits + 2 <= OUTPUT_TOTAL_PLACES:
        amount = amount * 100
    return amount.quantize(quantum, ROUND_FLOOR)


def format_amount(amount, dec_places=OUTPUT_DEC_PLACES):
    quantum = Decimal(1) / 10 ** dec_places
    integer_part = amount.quantize(0, ROUND_FLOOR)
    fractional_part = (amount - integer_part).quantize(quantum)
    thousand_sep = xbterminal.remote_config['OUTPUT_DEC_THOUSANDS_SPLIT']
    decimal_sep = xbterminal.remote_config['OUTPUT_DEC_FRACTIONAL_SPLIT']
    return '{0}{1}{2}'.format(format(integer_part, thousand_sep),
                              decimal_sep,
                              str(fractional_part)[2:])


def format_btc_amount(amount):
    amount_scaled = amount * BITCOIN_SCALE_DIVIZER
    return format_amount(amount_scaled, BITCOIN_OUTPUT_DEC_PLACES)
