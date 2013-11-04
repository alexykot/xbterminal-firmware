# -*- coding: utf-8 -*-
from decimal import Decimal
import requests

from xbterminal import defaults
from xbterminal.exceptions import NetworkError, CurrencyNotRecognized
from xbterminal.helpers.log import write_msg_log


BITPAY_CREATE_INVOICE_API_URL = "https://bitpay.com/api/invoice"
BITPAY_CHECK_INVOICE_API_URL = "<waiting for implementation>"

def createInvoice(amount):
    headers = defaults.EXTERNAL_CALLS_REQUEST_HEADERS
    headers['Content-type'] = 'application/json'
    response = requests.post(url=BITPAY_CREATE_INVOICE_API_URL,
                             headers=headers,
                             data={'price': float(amount),
                                   'currency': defaults.MERCHANT_CURRENCY,
                                   'transactionSpeed': defaults.MERCHANT_INSTANTFIAT_TRANSACTION_SPEED
                                    },
                             auth=(defaults.MERCHANT_INSTANTFIAT_API_KEY, ''))
    response = response.json()
    result = {}
    result['invoice_id'] = response['invoice_id']
    result['amount_btc'] = Decimal(response['amount']).quantize(defaults.BTC_DEC_PLACES)
    result['address'] = response['address']

    return result


def isInvoicePaid(invoice_id):
    #@TODO
    return True


