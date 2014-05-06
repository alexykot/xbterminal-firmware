# -*- coding: utf-8 -*-
from decimal import Decimal
import requests


import xbterminal
from xbterminal import defaults
from xbterminal.exceptions import NetworkError, CurrencyNotRecognized
from xbterminal.helpers.misc import log


BIPS_CREATE_INVOICE_API_URL = "https://bips.me/api/v2/invoice"
BIPS_CHECK_INVOICE_API_URL = "https://bips.me/api/v2/invoice/{}"

def createInvoice(amount, currency_code, speed):
    headers = defaults.EXTERNAL_CALLS_REQUEST_HEADERS
    headers['Content-type'] = 'application/json'

    response = requests.post(url=BIPS_CREATE_INVOICE_API_URL,
                             headers=headers,
                             data={'price': float(amount),
                                   'currency': currency_code,
                                   'transactionSpeed': speed,
                                    },
                             auth=(xbterminal.remote_config['MERCHANT_INSTANTFIAT_API_KEY'], ''))
    response = response.json()
    result = {}
    result['invoice_id'] = response['id']
    result['amount_btc'] = Decimal(response['btcPrice']).quantize(defaults.BTC_DEC_PLACES)
    result['address'] = response['address']

    return result


#API endpoint used here is not implemented yet. need to test this code when this will be done on BIPS side
def isInvoicePaid(invoice_id):
    invoice_url = BIPS_CHECK_INVOICE_API_URL.format(invoice_id)
    result = requests.get(url=invoice_url,
                          headers=defaults.EXTERNAL_CALLS_REQUEST_HEADERS,
                          auth=(xbterminal.remote_config['MERCHANT_INSTANTFIAT_API_KEY'], '')).json()

    if result['status'] == 'paid':
        return True
    else:
        return False



