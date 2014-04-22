# -*- coding: utf-8 -*-
from decimal import Decimal
import json
import logging
import requests
import re

import xbterminal
from xbterminal.exceptions import NetworkError, CurrencyNotRecognized
from xbterminal.helpers.log import log


CRYPTOPAY_CREATE_INVOICE_API_URL = "https://cryptopay.me/api/v1/invoices/?api_key={api_key}"
CRYPTOPAY_INVOICE_DATA_URL = "https://cryptopay.me/api/v1/invoices/{invoice_id}?api_key={api_key}"

def createInvoice(amount, currency, speed):
    global xbterminal

    headers = xbterminal.defaults.EXTERNAL_CALLS_REQUEST_HEADERS
    headers['Content-type'] = 'application/json'
    invoice_url = CRYPTOPAY_CREATE_INVOICE_API_URL.format(api_key=xbterminal.remote_config['MERCHANT_INSTANTFIAT_API_KEY'])

    response = requests.post(url=invoice_url,
                             headers=headers,
                             data=json.dumps({'price': float(amount),
                                               'currency': currency,
                                               'description': xbterminal.remote_config['MERCHANT_TRANSACTION_DESCRIPTION'],
                                                }),
                             )
    response = response.json()
    result = {}
    result['invoice_id'] = response['uuid']
    result['amount_btc'] = Decimal(response['btc_price']).quantize(xbterminal.defaults.BTC_DEC_PLACES)
    result['amount_btc'] = result['amount_btc'] + Decimal('0.00000001') #adding one satoshi to avoid rounding issues @TODO investigate rounding and remove this
    result['address'] = response['btc_address']
    log('cryptopay invoice created, uuid: {uuid}, amount_btc: {amount_btc}, address: {address}'.format(uuid=result['invoice_id'],
                                                                                                       amount_btc=result['amount_btc'],
                                                                                                       address=result['address']
                                                                                                       ))

    return result


def isInvoicePaid(invoice_id):
    global xbterminal

    invoice_status_url = CRYPTOPAY_INVOICE_DATA_URL.format(invoice_id=invoice_id,
                                                           api_key=xbterminal.remote_config['MERCHANT_INSTANTFIAT_API_KEY'])
    try:
        response = requests.get(url=invoice_status_url,
                                headers=xbterminal.defaults.EXTERNAL_CALLS_REQUEST_HEADERS,
                                ).json()
    except requests.HTTPError as error:
        logging.exception(error)
        return False

    if response['status'] == 'paid':
        return True
    else:
        return False
