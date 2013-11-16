# -*- coding: utf-8 -*-
from decimal import Decimal
import requests
import re

from xbterminal import defaults
from xbterminal.exceptions import NetworkError, CurrencyNotRecognized
from xbterminal.helpers.log import write_msg_log


BITPAY_CREATE_INVOICE_API_URL = "https://bitpay.com/api/invoice"
BITPAY_INVOICE_PAGE_URL = "https://bitpay.com/invoice?id={}"
BITPAY_CHECK_INVOICE_API_URL = "https://bitpay.com/api/invoice/{}"

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
    result['address'] = _getInvoiceAddress(response['invoice_id'])

    return result


def isInvoicePaid(invoice_id):
    invoice_status_url = BITPAY_CHECK_INVOICE_API_URL.format(invoice_id)
    response = requests.get(url=invoice_status_url,
                            headers=defaults.EXTERNAL_CALLS_REQUEST_HEADERS,
                            auth=(defaults.MERCHANT_INSTANTFIAT_API_KEY, '')).json()

    if response['status'] == 'paid':
        return True
    else:
        return False


#method fetches HTML payment page and parses it to get out payment address
def _getInvoiceAddress(invoice_id):
    invoice_address_url = BITPAY_INVOICE_PAGE_URL.format(invoice_id)
    response = requests.get(url=invoice_address_url,
                            headers=defaults.EXTERNAL_CALLS_REQUEST_HEADERS,
                            )
    response_html = response.text

    bitcoin_uri_regexp = re.compile(r'bitcoin:(1|3)[a-zA-Z0-9]{26,33}\?')
    result = bitcoin_uri_regexp.search(response_html)
    if result is None:
        return

    address = str(result.group())[8:-1]
    return address


