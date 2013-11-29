# -*- coding: utf-8 -*-
from decimal import Decimal
import urllib2

import xbterminal
from xbterminal.helpers.misc import strrepeat, splitThousands, strpad
import xbterminal.instantfiat
import xbterminal.helpers.misc as misc_helpers
from xbterminal import bitcoinaverage
from xbterminal import defaults
from xbterminal import blockchain


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


def getOurFeeBtcAmount(total_fiat_amount, btc_exchange_rate):
    total_fiat_amount = Decimal(total_fiat_amount).quantize(defaults.BTC_DEC_PLACES)
    our_fee_fiat_amount = total_fiat_amount * Decimal(defaults.OUR_FEE_SHARE).quantize(defaults.BTC_DEC_PLACES)
    our_fee_btc_amount = our_fee_fiat_amount / btc_exchange_rate
    our_fee_btc_amount = Decimal(our_fee_btc_amount).quantize(defaults.BTC_DEC_PLACES)

    if our_fee_btc_amount < defaults.BTC_MIN_OUTPUT:
        our_fee_btc_amount = Decimal(0).quantize(defaults.BTC_DEC_PLACES)

    return our_fee_btc_amount


def getMerchantBtcAmount(total_fiat_amount, btc_exchange_rate):
    total_fiat_amount = Decimal(total_fiat_amount).quantize(defaults.BTC_DEC_PLACES)
    our_fee_fiat_amount = total_fiat_amount * Decimal(defaults.OUR_FEE_SHARE).quantize(defaults.BTC_DEC_PLACES)
    instantfiat_fiat_amount = total_fiat_amount * Decimal(defaults.MERCHANT_INSTANTFIAT_SHARE).quantize(defaults.BTC_DEC_PLACES)
    merchants_fiat_amount = total_fiat_amount - instantfiat_fiat_amount - our_fee_fiat_amount
    merchants_btc_amount = merchants_fiat_amount / btc_exchange_rate
    merchants_btc_amount = Decimal(merchants_btc_amount).quantize(defaults.BTC_DEC_PLACES)

    if merchants_btc_amount < defaults.BTC_MIN_OUTPUT:
        merchants_btc_amount = defaults.BTC_MIN_OUTPUT.quantize(defaults.BTC_DEC_PLACES)

    return merchants_btc_amount


def createInvoice(total_fiat_amount):
    global xbterminal

    total_fiat_amount = Decimal(total_fiat_amount).quantize(defaults.BTC_DEC_PLACES)
    instantfiat_fiat_amount = total_fiat_amount * Decimal(defaults.MERCHANT_INSTANTFIAT_SHARE).quantize(defaults.BTC_DEC_PLACES)

    invoice_data = getattr(xbterminal.instantfiat, defaults.MERCHANT_INSTANTFIAT_EXCHANGE_SERVICE).createInvoice(instantfiat_fiat_amount)

    exchange_rate = invoice_data['amount_btc'] / total_fiat_amount

    return invoice_data['amount_btc'], invoice_data['invoice_id'], invoice_data['address'], exchange_rate


def inputToDecimal(display_value_unformatted):
    amount_input = float(display_value_unformatted) / 10 * defaults.OUTPUT_DEC_PLACES
    return Decimal(amount_input).quantize(defaults.FIAT_DEC_PLACES)

def processKeyInput(display_value_unformatted, key_code):
    display_value_unformatted = str(display_value_unformatted)
    if key_code == 'A':
        if display_value_unformatted is not '' and len(display_value_unformatted) >= 2:
            display_value_unformatted = display_value_unformatted[:-1]
        else:
            display_value_unformatted = ''
    elif isinstance(key_code, (int, long)):
        if len(display_value_unformatted) < defaults.OUTPUT_TOTAL_PLACES:
            display_value_unformatted = str(display_value_unformatted) + str(key_code)

    return display_value_unformatted

def formatInput(display_value_unformatted, decimal_places):
    if display_value_unformatted == '':
        return "{}{}{}".format('0', defaults.OUTPUT_DEC_FRACTIONAL_SPLIT, strrepeat('0', decimal_places))
    else:
        fractional_part = int(display_value_unformatted) % (10**decimal_places)
        decimal_part = (int(display_value_unformatted) - fractional_part) / (10**decimal_places)
        decimal_part = str(int(decimal_part))
        fractional_part = strpad(string_to_pad=str(int(fractional_part)),
                                 chars_to_pad='0',
                                 length_to_pad=decimal_places,
                                 pad_left=True
                                    )

        decimal_part = splitThousands(decimal_part, defaults.OUTPUT_DEC_THOUSANDS_SPLIT)

        display_value_formatted = '{}{}{}'.format(decimal_part, defaults.OUTPUT_DEC_FRACTIONAL_SPLIT, fractional_part)
        return display_value_formatted

def formatDecimal(amount_decimal, decimal_places):
    amount = float(amount_decimal)
    amount_int = int(amount * (10**decimal_places))

    fractional_part = amount_int % (10**decimal_places)
    decimal_part = (amount_int - fractional_part) / (10**decimal_places)
    decimal_part = str(int(decimal_part))
    fractional_part = strpad(string_to_pad=str(int(fractional_part)),
                             chars_to_pad='0',
                             length_to_pad=decimal_places,
                             pad_left=True
                                )

    decimal_part = splitThousands(decimal_part, defaults.OUTPUT_DEC_THOUSANDS_SPLIT)

    display_value_formatted = '{}{}{}'.format(decimal_part, defaults.OUTPUT_DEC_FRACTIONAL_SPLIT, fractional_part)
    return display_value_formatted


# bitcoin:1G2bcoCKj8s9GYheqQgU5CHSLCtGjyP9Vz?amount=0.001&label=test%20payment&message=this%20is%20a%20test
def getBitcoinURI(payment_addr, amount_btc):
    amount_btc = str(Decimal(amount_btc).quantize(defaults.BTC_DEC_PLACES))
    uri = 'bitcoin:{}?amount={}&label={}&message={}'.format(payment_addr,
                                                            amount_btc,
                                                            urllib2.quote(str(defaults.MERCHANT_NAME)).encode('utf8'),
                                                            urllib2.quote(str(defaults.MERCHANT_TRANSACTION_DESCRIPTION)).encode('utf8'),
                                                                )
    return uri


#longest fitting into 57 blocks sized QR code
# bitcoin:1G2bcoCKj8s9GYheqQgU5CHSLCtGjyP9Vz?amount=0.001&message=this%20is%20a%20test1G%202bcoCKj%208s9%20GYheqQgU%205CHSLCtGj%20yP9Vz%2017srxna%20p4ikefG4hCn%201x6%207MUQjoQfqv%20qUwb1JV9nFhxot%20VYyUD26%20BbZB2ak1Yur8Z%20y7x%20w13dHs7s%20L7QdtLV%20i7hG8hWE3Fhasfeggryur5