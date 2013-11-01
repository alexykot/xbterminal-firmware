# -*- coding: utf-8 -*-
from decimal import Decimal
import urllib2

import xbterminal
import xbterminal.helpers
from xbterminal.helpers.log import write_msg_log
import xbterminal.helpers.misc as misc_helpers
import xbterminal.exchange_servers
from xbterminal import defaults
from xbterminal.exchange_servers import bitcoinaverage
from xbterminal.helpers.log import write_msg_log
from xbterminal import blockchain


def getTransactionAddresses(instantfiat_amout, merchants_amount, fee_amount):
    local_addr = blockchain.getFreshAddress()
    merchant_addr = defaults.MERCHANT_BITCOIN_ADDRESS
    instantfiat_addr = None
    if instantfiat_amout > 0:
        instantfiat_addr = getattr(xbterminal.exchange_servers, defaults.INSTANT_FIAT_EXCHANGE_SERVICE).getPaymentAddress(instantfiat_amout)

    fee_addr = defaults.OUR_FEE_BITCOIN_ADDRESS

    return local_addr, instantfiat_addr, merchant_addr, fee_addr

def createOutgoingTransaction(addresses, amounts):
    outputs = {}
    outputs[addresses['fee']] = amounts['fee']
    if amounts['merchant'] > 0:
        outputs[addresses['merchant']] = amounts['merchant']
    if amounts['instantfiat'] > 0:
        outputs[addresses['instantfiat']] = amounts['instantfiat']


    # result = blockchain.sendTransaction(outputs)
    result = blockchain.sendRawTransaction(outputs, from_addr=addresses['local'])
    if result:
        return result
    else:
        #raise Exception here
        pass

def getBtcSharesAmounts(total_fiat_amount):
    global xbterminal, bitcoinaverage

    total_fiat_amount = Decimal(total_fiat_amount).quantize(defaults.FIAT_DEC_PLACES)
    our_fee_fiat_amount = total_fiat_amount * Decimal(defaults.OUR_FEE_SHARE).quantize(defaults.FIAT_DEC_PLACES)
    our_fee_fiat_amount = Decimal(our_fee_fiat_amount).quantize(defaults.FIAT_DEC_PLACES)
    instantfiat_fiat_amount = total_fiat_amount * Decimal(defaults.INSTANT_FIAT_SHARE).quantize(defaults.BTC_DEC_PLACES)
    merchants_btc_fiat_amount = total_fiat_amount - instantfiat_fiat_amount - our_fee_fiat_amount

    our_fee_btc_amount = bitcoinaverage.convertToBtc(our_fee_fiat_amount, defaults.MERCHANT_CURRENCY)
    our_fee_btc_amount = Decimal(our_fee_btc_amount).quantize(defaults.BTC_DEC_PLACES)
    our_fee_btc_amount = our_fee_btc_amount

    instantfiat_btc_amount = getattr(xbterminal.exchange_servers,
                                     defaults.INSTANT_FIAT_EXCHANGE_SERVICE).convertToBtc(instantfiat_fiat_amount,
                                                                                          defaults.MERCHANT_CURRENCY)

    merchants_btc_fiat_amount = bitcoinaverage.convertToBtc(merchants_btc_fiat_amount, defaults.MERCHANT_CURRENCY)

    if our_fee_btc_amount < defaults.BTC_MIN_OUTPUT:
        our_fee_btc_amount = defaults.BTC_MIN_OUTPUT
    if instantfiat_btc_amount > 0 and instantfiat_btc_amount < defaults.BTC_MIN_OUTPUT:
        instantfiat_btc_amount = defaults.BTC_MIN_OUTPUT
    if merchants_btc_fiat_amount > 0 and merchants_btc_fiat_amount < defaults.BTC_MIN_OUTPUT:
        merchants_btc_fiat_amount = defaults.BTC_MIN_OUTPUT

    return our_fee_btc_amount, instantfiat_btc_amount, merchants_btc_fiat_amount

def getInstantFiatBtcAddress(instantfiat_fiat_amount):
    pass

def getMerchantBtcAddress(instantfiat_fiat_amount):
    global xbterminal

    return xbterminal.config['merchant_btc_address']

''' Keeping for now for reference purposes
def processAmountKeyInput(current_text, key_code):
    global xbterminal, misc_helpers

    key_code = str(key_code)
    current_text_split = current_text.split(defaults.OUTPUT_DEC_FRACTIONAL_SPLIT)
    if len(current_text_split) != 2:
        return defaults.OUTPUT_DEFAULT_VALUE

    decimal_part = current_text_split[0]
    decimal_part = decimal_part.replace(defaults.OUTPUT_DEC_THOUSANDS_SPLIT, '')
    fractional_part = current_text_split[1]

    if key_code == '.':
        xbterminal.runtime['current_text_piece'] = 'fractional'
        return current_text

    elif key_code == 'A':
        if xbterminal.runtime['current_text_piece'] == 'fractional':
            fractional_part = fractional_part.rstrip('_')
            if len(fractional_part) == 0:
                xbterminal.runtime['current_text_piece'] = 'decimal'
            else:
                fractional_part = fractional_part[:-1]
        if xbterminal.runtime['current_text_piece'] == 'decimal':
            fractional_part = fractional_part.lstrip('_')
            decimal_part = decimal_part[:-1]

    elif key_code == 'B':
        xbterminal.gui.runtime['main_win'].ui.continue_lbl.setText("")
        xbterminal.runtime['current_text_piece'] = 'decimal'
        return defaults.OUTPUT_DEFAULT_VALUE
    else:

        xbterminal.gui.runtime['main_win'].ui.continue_lbl.setText("press enter to continue")

        if xbterminal.runtime['current_text_piece'] == 'decimal':
            decimal_part = decimal_part.lstrip('_')
            if len(decimal_part) < (defaults.OUTPUT_TOTAL_PLACES - defaults.OUTPUT_DEC_PLACES):
                decimal_part = '{}{}'.format(decimal_part, key_code)

        if xbterminal.runtime['current_text_piece'] == 'fractional':
            fractional_part = fractional_part.rstrip('_')
            if len(fractional_part) < defaults.OUTPUT_DEC_PLACES:
                fractional_part = '{}{}'.format(fractional_part, key_code)

    decimal_part = misc_helpers.strpad(decimal_part, '_', 1, pad_left=True)
    fractional_part = misc_helpers.strpad(fractional_part, '_', defaults.OUTPUT_DEC_PLACES, pad_right=True)
    decimal_part = misc_helpers.splitThousands(decimal_part, defaults.OUTPUT_DEC_THOUSANDS_SPLIT)
    resulting_text = '{}{}{}'.format(decimal_part, defaults.OUTPUT_DEC_FRACTIONAL_SPLIT, fractional_part)
    return resulting_text
'''

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
    resulting_text = '{}{}{}'.format(decimal_part, defaults.OUTPUT_DEC_FRACTIONAL_SPLIT, fractional_part)
    return resulting_text



def formatTextEntered(current_text):
    if current_text is '':
        return "0.00"
    else:
        new_text = float(current_text)/100
        return "{0:.2f}".format(new_text)


def processKeyInput(current_text, key_code):

    if current_text is '' and key_code != 'A' and key_code != 'B':
        current_text = str(key_code)
        return current_text

    if key_code == 'A':
        if current_text is not '' and len(current_text) >= 2:
            current_text = current_text[:-1]
            return current_text
        else:
            return ''


    elif key_code == 'B':
        return ''

    else:
        v = str(current_text)
        k = str(key_code)
        current_text = v + k

    return current_text



def getBitcoinURI(payment_addr, amount_btc):

    amount_btc = str(Decimal(amount_btc).quantize(defaults.BTC_DEC_PLACES))
    uri = 'bitcoin:{}?amount={}X8&label={}&message={}'.format(payment_addr,
                                                              amount_btc,
                                                              urllib2.quote(str(defaults.MERCHANT_NAME).encode('utf8')),
                                                              urllib2.quote(str(defaults.MERCHANT_TRANSACTION_DESCRIPTION)).encode('utf8'),
                                                                )
    return uri
