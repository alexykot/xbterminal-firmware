# -*- coding: utf-8 -*-
from decimal import Decimal
import httplib
import json
import logging
import socket
import subprocess
import urllib2
import datetime
import requests
import time
import sys
import simplejson

import xbterminal
import xbterminal.instantfiat
from xbterminal.helpers.log import log
from xbterminal.helpers.misc import strrepeat, splitThousands, strpad
from xbterminal import defaults
from xbterminal.blockchain import blockchain


def createOutgoingTransaction(addresses, amounts):
    outputs = {}
    outputs[addresses['fee']] = amounts['fee']
    if amounts['merchant'] > 0:
        outputs[addresses['merchant']] = amounts['merchant']
    if amounts['instantfiat'] > 0:
        outputs[addresses['instantfiat']] = amounts['instantfiat']

    result = blockchain.sendTransaction(outputs, from_addr=addresses['local'])
    if result:
        return result
    else:
        #raise Exception here
        pass


def getOurFeeBtcAmount(total_fiat_amount, btc_exchange_rate):
    total_fiat_amount = Decimal(total_fiat_amount).quantize(defaults.BTC_DEC_PLACES)
    our_fee_fiat_amount = total_fiat_amount * Decimal(xbterminal.remote_config['OUR_FEE_SHARE']).quantize(defaults.BTC_DEC_PLACES)
    our_fee_btc_amount = our_fee_fiat_amount / btc_exchange_rate
    our_fee_btc_amount = Decimal(our_fee_btc_amount).quantize(defaults.BTC_DEC_PLACES)

    if our_fee_btc_amount < defaults.BTC_MIN_OUTPUT:
        log('fee {fee} below dust threshold {dust}, ignoring'.format(fee=our_fee_btc_amount, dust=defaults.BTC_MIN_OUTPUT))
        our_fee_btc_amount = Decimal(0).quantize(defaults.BTC_DEC_PLACES)

    return our_fee_btc_amount


def getMerchantBtcAmount(total_fiat_amount, btc_exchange_rate):
    total_fiat_amount = Decimal(total_fiat_amount).quantize(defaults.BTC_DEC_PLACES)
    our_fee_fiat_amount = total_fiat_amount * Decimal(xbterminal.remote_config['OUR_FEE_SHARE']).quantize(defaults.BTC_DEC_PLACES)
    instantfiat_fiat_amount = total_fiat_amount * Decimal(xbterminal.remote_config['MERCHANT_INSTANTFIAT_SHARE']).quantize(defaults.BTC_DEC_PLACES)
    merchants_fiat_amount = total_fiat_amount - instantfiat_fiat_amount

    merchants_btc_amount = merchants_fiat_amount / btc_exchange_rate
    merchants_btc_amount = Decimal(merchants_btc_amount).quantize(defaults.BTC_DEC_PLACES)

    if merchants_btc_amount < defaults.BTC_MIN_OUTPUT and merchants_btc_amount > 0:
        log('merchant_share {merchant_share} below dust threshold {dust}, ignoring'.format(merchant_share=merchants_btc_amount,
                                                                                           dust=defaults.BTC_MIN_OUTPUT))
        merchants_btc_amount = defaults.BTC_MIN_OUTPUT.quantize(defaults.BTC_DEC_PLACES)

    return merchants_btc_amount


def createInvoice(total_fiat_amount):
    global xbterminal

    total_fiat_amount = Decimal(total_fiat_amount).quantize(defaults.BTC_DEC_PLACES)
    instantfiat_fiat_amount = total_fiat_amount * Decimal(xbterminal.remote_config['MERCHANT_INSTANTFIAT_SHARE']).quantize(defaults.BTC_DEC_PLACES)

    instantfiat_service_name = xbterminal.remote_config['MERCHANT_INSTANTFIAT_EXCHANGE_SERVICE'].lower()
    __import__('xbterminal.instantfiat.{}'.format(instantfiat_service_name))
    invoice_data = (getattr(xbterminal.instantfiat, instantfiat_service_name)
                    .createInvoice(instantfiat_fiat_amount,
                                   xbterminal.remote_config['MERCHANT_CURRENCY'],
                                   xbterminal.remote_config['MERCHANT_INSTANTFIAT_TRANSACTION_SPEED']))

    exchange_rate = instantfiat_fiat_amount / invoice_data['amount_btc']

    return instantfiat_fiat_amount, invoice_data['amount_btc'], invoice_data['invoice_id'], invoice_data['address'], exchange_rate


def inputToDecimal(display_value_unformatted):
    if display_value_unformatted == '':
        amount_input = 0.0
    else:
        amount_input = float(display_value_unformatted) / (10 ** defaults.OUTPUT_DEC_PLACES)

    return Decimal(amount_input).quantize(defaults.FIAT_DEC_PLACES)

def processKeyInput(display_value_unformatted, key_code):
    display_value_unformatted = str(display_value_unformatted)
    if key_code == 'backspace':
        if display_value_unformatted is not '' and len(display_value_unformatted) >= 2:
            display_value_unformatted = display_value_unformatted[:-1]
        else:
            display_value_unformatted = ''
    elif isinstance(key_code, (int, long)):
        if len(display_value_unformatted) < defaults.OUTPUT_TOTAL_PLACES:
            display_value_unformatted = str(display_value_unformatted) + str(key_code)

    return display_value_unformatted

def formatInput(display_value_unformatted, decimal_places):
    global xbterminal

    if display_value_unformatted == '':
        return "{}{}{}".format('0', xbterminal.remote_config['OUTPUT_DEC_FRACTIONAL_SPLIT'], strrepeat('0', decimal_places))
    else:
        fractional_part = int(display_value_unformatted) % (10**decimal_places)
        decimal_part = (int(display_value_unformatted) - fractional_part) / (10**decimal_places)
        decimal_part = str(int(decimal_part))
        fractional_part = strpad(string_to_pad=str(int(fractional_part)),
                                 chars_to_pad='0',
                                 length_to_pad=decimal_places,
                                 pad_left=True
                                    )

        decimal_part = splitThousands(decimal_part, xbterminal.remote_config['OUTPUT_DEC_THOUSANDS_SPLIT'])

        display_value_formatted = '{}{}{}'.format(decimal_part, xbterminal.remote_config['OUTPUT_DEC_FRACTIONAL_SPLIT'], fractional_part)
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

    decimal_part = splitThousands(decimal_part, xbterminal.remote_config['OUTPUT_DEC_THOUSANDS_SPLIT'])

    display_value_formatted = '{}{}{}'.format(decimal_part, xbterminal.remote_config['OUTPUT_DEC_FRACTIONAL_SPLIT'], fractional_part)
    return display_value_formatted


def formatBitcoin(amount_bitcoin):
    amount_bitcoin_scaled = amount_bitcoin * defaults.BITCOIN_SCALE_DIVIZER
    return formatDecimal(amount_bitcoin_scaled, defaults.BITCOIN_OUTPUT_DEC_PLACES)


def logTransaction(local_addr, instantfiat_addr, dest_addr,
                   tx_id1, tx_id2, instantfiat_invoice_id,
                   fiat_amount, btc_amount, instantfiat_fiat_amount, instantfiat_btc_amount, fee_btc_amount,
                   fiat_currency, exchange_rate):
    global xbterminal

    headers = defaults.EXTERNAL_CALLS_REQUEST_HEADERS
    headers['Content-type'] = 'application/json'

    fiat_amount = str(fiat_amount.quantize(defaults.FIAT_DEC_PLACES))
    btc_amount = str(btc_amount.quantize(defaults.BTC_DEC_PLACES))
    instantfiat_fiat_amount = str(instantfiat_fiat_amount.quantize(Decimal('0.00'))) #two dec places forced for fiat
    instantfiat_btc_amount = str(instantfiat_btc_amount.quantize(defaults.BTC_DEC_PLACES))
    fee_btc_amount = str(fee_btc_amount.quantize(defaults.BTC_DEC_PLACES))
    exchange_rate = str(exchange_rate.quantize(defaults.FIAT_DEC_PLACES))

    tx_log_url = xbterminal.runtime['remote_server'] + defaults.REMOTE_API_ENDPOINTS['tx_log']
    data = {"device": xbterminal.device_key,
            "hop_address": local_addr,
            "dest_address": dest_addr,
            "instantfiat_address" : instantfiat_addr,
            "bitcoin_transaction_id_1": tx_id1,
            "bitcoin_transaction_id_2": tx_id2,
            "fiat_amount": fiat_amount,
            "fiat_currency": fiat_currency,
            "btc_amount": btc_amount,
            "instantfiat_fiat_amount": instantfiat_fiat_amount,
            "instantfiat_btc_amount": instantfiat_btc_amount,
            "fee_btc_amount": fee_btc_amount,
            "instantfiat_invoice_id": instantfiat_invoice_id,
            "effective_exchange_rate": exchange_rate,
            "time": datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%dT%H:%M:%S%z'),
            }
    data = json.dumps(data)

    receipt_url = None
    try:
        response = requests.post(url=tx_log_url, headers=headers, data=data)
        response_data = response.json()
        receipt_url = xbterminal.runtime['remote_server'] + defaults.REMOTE_API_ENDPOINTS['receipt'].format(receipt_key=response_data['receipt_key'])
    except (KeyError,
            TypeError,
            ValueError,
            simplejson.decoder.JSONDecodeError,
            socket.error,
            urllib2.URLError,
            httplib.BadStatusLine,
            httplib.IncompleteRead) as error:
        logging.exception(error)
        log('reconciliation API failed, error: {error}'.format(error))

    return receipt_url

def clearPaymentRuntime(clear_amounts=True):
    global xbterminal

    if clear_amounts:
        xbterminal.runtime['display_value_unformatted'] = ''
        xbterminal.runtime['display_value_formatted'] = formatInput(xbterminal.runtime['display_value_unformatted'],
                                                                        defaults.OUTPUT_DEC_PLACES)
        xbterminal.gui.runtime['main_win'].ui.amount_input.setText(xbterminal.runtime['display_value_formatted'])

    xbterminal.runtime['amounts']['amount_to_pay_btc'] = None
    xbterminal.runtime['amounts']['amount_to_pay_fiat'] = None
    xbterminal.runtime['effective_rate_btc'] = None
    xbterminal.runtime['transactions_addresses'] = None

    xbterminal.gui.runtime['main_win'].ui.fiat_amount.setText("0")
    xbterminal.gui.runtime['main_win'].ui.btc_amount.setText("0")
    xbterminal.gui.runtime['main_win'].ui.exchange_rate_amount.setText("0")

    xbterminal.gui.runtime['main_win'].ui.fiat_amount_qr.setText("0")
    xbterminal.gui.runtime['main_win'].ui.btc_amount_qr.setText("0")
    xbterminal.gui.runtime['main_win'].ui.exchange_rate_qr.setText("0")

    xbterminal.gui.runtime['main_win'].ui.fiat_amount_nfc.setText("0")
    xbterminal.gui.runtime['main_win'].ui.btc_amount_nfc.setText("0")
    xbterminal.gui.runtime['main_win'].ui.exchange_rate_nfc.setText("0")


def getBitcoinURI(payment_addr, amount_btc):
    amount_btc = str(Decimal(amount_btc).quantize(defaults.BTC_DEC_PLACES))
    uri = 'bitcoin:{}?amount={}&label={}&message={}'.format(payment_addr,
                                                            amount_btc,
                                                            urllib2.quote(str(xbterminal.remote_config['MERCHANT_NAME'])).encode('utf8'),
                                                            urllib2.quote(str(xbterminal.remote_config['MERCHANT_TRANSACTION_DESCRIPTION'])).encode('utf8'),
                                                                )
    return uri


def gracefullExit(system_halt=False, system_reboot=False):
    xbterminal.helpers.configs.save_local_state()
    xbterminal.helpers.nfcpy.stop()
    xbterminal.helpers.misc.log('application halted')
    if system_halt:
        xbterminal.helpers.misc.log('system halt command sent')
        subprocess.Popen(['halt', ])
    if system_reboot:
        xbterminal.helpers.misc.log('system reboot command sent')
        subprocess.Popen(['reboot', ])
    sys.exit()

