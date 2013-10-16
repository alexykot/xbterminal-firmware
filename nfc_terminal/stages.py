# -*- coding: utf-8 -*-
from decimal import Decimal

import nfc_terminal
import nfc_terminal.helpers
import nfc_terminal.helpers.misc as misc_helpers
import nfc_terminal.exchange_servers
from nfc_terminal import defaults
from nfc_terminal.exchange_servers import bitcoinaverage


def getTransactionAddress(amount_to_pay_fiat):
    return '1G2bcoCKj8s9GYheqQgU5CHSLCtGjyP9Vz'

def getBtcSharesAmounts(total_fiat_amount):
    global nfc_terminal, bitcoinaverage

    total_fiat_amount = Decimal(total_fiat_amount).quantize(defaults.FIAT_DEC_PLACES)
    our_fee_fiat_amount = total_fiat_amount * Decimal(defaults.OUR_FEE_SHARE).quantize(defaults.BTC_DEC_PLACES)
    instantfiat_fiat_amount = total_fiat_amount * Decimal(defaults.INSTANT_FIAT_SHARE).quantize(defaults.BTC_DEC_PLACES)
    merchants_btc_fiat_amount = total_fiat_amount - instantfiat_fiat_amount - our_fee_fiat_amount

    our_fee_btc_amount = bitcoinaverage.convertToBtc(our_fee_fiat_amount, defaults.MERCHANT_CURRENCY)
    instantfiat_btc_amount = getattr(nfc_terminal.exchange_servers, defaults.INSTANT_FIAT_EXCHANGE_SERVICE).convertToBtc(instantfiat_fiat_amount, defaults.MERCHANT_CURRENCY)
    merchants_btc_fiat_amount = bitcoinaverage.convertToBtc(merchants_btc_fiat_amount, defaults.MERCHANT_CURRENCY)

    return our_fee_btc_amount, instantfiat_btc_amount, merchants_btc_fiat_amount

def checkTransactionDone(transaction_address, amount_to_pay_btc):
    #not implemented
    return False

def getInstantFiatBtcAddress(instantfiat_fiat_amount):
    pass

def getMerchantBtcAddress(instantfiat_fiat_amount):
    global nfc_terminal

    return nfc_terminal.config['merchant_btc_address']

def processAmountKeyInput(current_text, key_code):
    global nfc_terminal, misc_helpers

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
            if len(decimal_part) < (defaults.OUTPUT_TOTAL_PLACES - defaults.OUTPUT_DEC_PLACES):
                decimal_part = '%s%s' % (decimal_part, key_code)

        if nfc_terminal.runtime['current_text_piece'] == 'fractional':
            fractional_part = fractional_part.rstrip('_')
            if len(fractional_part) < defaults.OUTPUT_DEC_PLACES:
                fractional_part = '%s%s' % (fractional_part, key_code)

    decimal_part = misc_helpers.strpad(decimal_part, '_', 1, pad_left=True)
    fractional_part = misc_helpers.strpad(fractional_part, '_', defaults.OUTPUT_DEC_PLACES, pad_right=True)
    decimal_part = misc_helpers.splitThousands(decimal_part, defaults.OUTPUT_DEC_THOUSANDS_SPLIT)
    resulting_text = '%s%s%s' % (decimal_part, defaults.OUTPUT_DEC_FRACTIONAL_SPLIT, fractional_part)
    return resulting_text


def amountInputToDecimal(amount_input):
    amount_input = amount_input.replace(defaults.OUTPUT_DEC_THOUSANDS_SPLIT, '')
    amount_input = amount_input.replace(defaults.OUTPUT_DEC_FRACTIONAL_SPLIT, '.')
    amount_input = amount_input.replace('_', '0')
    return Decimal(amount_input).quantize(defaults.FIAT_DEC_PLACES)

def amountDecimalToOutput(amount_decimal):
    output_precision = '0.'+misc_helpers.strrepeat('0', defaults.OUTPUT_DEC_PLACES)
    amount_decimal = amount_decimal.quantize(Decimal(output_precision))
    amount_decimal_str = str(amount_decimal)
    amount_decimal_list = amount_decimal_str.split('.')
    decimal_part = amount_decimal_list[0]
    fractional_part = amount_decimal_list[1]
    decimal_part = misc_helpers.splitThousands(decimal_part, defaults.OUTPUT_DEC_THOUSANDS_SPLIT)
    resulting_text = '%s%s%s' % (decimal_part, defaults.OUTPUT_DEC_FRACTIONAL_SPLIT, fractional_part)
    return resulting_text
