# -*- coding: utf-8 -*-
from decimal import Decimal
import requests
import re

from xbterminal import defaults
from xbterminal.exceptions import NetworkError, CurrencyNotRecognized
from xbterminal.helpers.log import write_msg_log


CRYPTOPAY_CREATE_INVOICE_API_URL = "https://cryptopay.me/api/v1/invoices/?api_key={}"
CRYPTOPAY_INVOICE_DATA_URL = "https://cryptopay.me/api/v1/invoices/{}?api_key={}"

def createInvoice(amount):
    headers = defaults.EXTERNAL_CALLS_REQUEST_HEADERS
    headers['Content-type'] = 'application/json'
    invoice_url = CRYPTOPAY_CREATE_INVOICE_API_URL.format(defaults.MERCHANT_INSTANTFIAT_API_KEY)

    response = requests.post(url=invoice_url,
                             headers=headers,
                             data={'price': float(amount),
                                   'currency': defaults.MERCHANT_CURRENCY,
                                   'description': defaults.MERCHANT_TRANSACTION_DESCRIPTION,
                                    },
                             )
    response = response.json()
    result = {}
    result['invoice_id'] = response['uuid']
    result['amount_btc'] = Decimal(response['btc_price']).quantize(defaults.BTC_DEC_PLACES)
    result['address'] = response['btc_address']

    return result


def isInvoicePaid(invoice_id):
    invoice_status_url = CRYPTOPAY_CREATE_INVOICE_API_URL.format(invoice_id, defaults.MERCHANT_INSTANTFIAT_API_KEY)
    response = requests.get(url=invoice_status_url,
                            headers=defaults.EXTERNAL_CALLS_REQUEST_HEADERS,
                            ).json()

    if response['status'] == 'paid':
        return True
    else:
        return False

