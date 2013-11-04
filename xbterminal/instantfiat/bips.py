# -*- coding: utf-8 -*-
from decimal import Decimal
import requests

from xbterminal import defaults
from xbterminal.exceptions import NetworkError, CurrencyNotRecognized
from xbterminal.helpers.log import write_msg_log


BIPS_CREATE_INVOICE_API_URL = "https://bips.me/api/v2/invoice"
BIPS_CHECK_INVOICE_API_URL = "https://bitpay.com/api/invoice/{}"

def createInvoice(amount):
    headers = defaults.EXTERNAL_CALLS_REQUEST_HEADERS
    headers['Content-type'] = 'application/json'
    response = requests.post(url=BIPS_CREATE_INVOICE_API_URL,
                             headers=headers,
                             data={'price':float(amount),
                                   'currency':defaults.MERCHANT_CURRENCY,
                                   'transactionSpeed': defaults.MERCHANT_INSTANTFIAT_TRANSACTION_SPEED
                                    },
                             auth=(defaults.MERCHANT_INSTANTFIAT_API_KEY, ''))
    response = response.json()
    result = {}
    result['invoice_id'] = response['id']
    result['amount_btc'] = Decimal(response['btcPrice']).quantize(defaults.BTC_DEC_PLACES)
    result['address'] = response['address']

    return result


def isInvoicePaid(invoice_id):
    invoice_url = BIPS_CHECK_INVOICE_API_URL.format(invoice_id)
    headers = defaults.EXTERNAL_CALLS_REQUEST_HEADERS
    headers['Content-type'] = 'application/json'
    requests.get(url=invoice_url,
                 headers=headers,
                 auth=(defaults.MERCHANT_INSTANTFIAT_API_KEY, ''))

    return True


