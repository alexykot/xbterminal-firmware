# -*- coding: utf-8 -*-
from decimal import Decimal
import logging
import requests

import xbterminal
from xbterminal.helpers.misc import strrepeat, splitThousands, strpad
from xbterminal import defaults

logger = logging.getLogger(__name__)


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
    elif key_code in range(10):
        if len(display_value_unformatted) + 1 <= defaults.OUTPUT_TOTAL_PLACES:
            display_value_unformatted = str(display_value_unformatted) + str(key_code)
    elif key_code == '00':
        if len(display_value_unformatted) + 2 <= defaults.OUTPUT_TOTAL_PLACES:
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


def clearPaymentRuntime(run, ui, clear_amounts=True):
    ui.showScreen('load_indefinite')
    logger.debug('clearing payment runtime')
    if clear_amounts:
        run['display_value_unformatted'] = ''
        run['display_value_formatted'] = formatInput(run['display_value_unformatted'],
                                                     defaults.OUTPUT_DEC_PLACES)
        ui.setText('amount_input', run['display_value_formatted'])

    run['amounts']['amount_to_pay_btc'] = None
    run['amounts']['amount_to_pay_fiat'] = None
    run['effective_rate_btc'] = None
    run['transactions_addresses'] = None

    ui.setText('fiat_amount', "0")
    ui.setText('btc_amount', "0")
    ui.setText('exchange_rate_amount', "0")

    ui.setText('fiat_amount_qr', "0")
    ui.setText('btc_amount_qr', "0")
    ui.setText('exchange_rate_qr', "0")
    ui.setImage('qr_image', None)
    ui.setImage("receipt_qr_image", None)

    ui.setText('fiat_amount_nfc', "0")
    ui.setText('btc_amount_nfc', "0")
    ui.setText('exchange_rate_nfc', "0")


class Payment(object):

    def __init__(self, uid, btc_amount, exchange_rate, payment_uri, request):
        self.uid = uid
        self.btc_amount = btc_amount
        self.exchange_rate = exchange_rate
        self.payment_uri = payment_uri
        self.request = request

    @classmethod
    def create_order(cls, fiat_amount, bt_mac):
        """
        Accepts:
            fiat_amount: amount to pay (Decimal)
            bt_mac: mac address
        Returns:
            class instance or None
        """
        payment_init_url = xbterminal.runtime['remote_server'] + defaults.REMOTE_API_ENDPOINTS['payment_init']
        payload = {
            'device_key': xbterminal.device_key,
            'amount': float(fiat_amount),
            'bt_mac': bt_mac,
        }
        try:
            response = requests.post(payment_init_url, data=payload)
            response.raise_for_status()
            result = response.json()
        except (requests.exceptions.RequestException, ValueError) as error:
            logger.error("create payment order: {0}".\
                format(error.__class__.__name__))
            return None
        # Parse result
        instance = cls(result['payment_uid'],
                       Decimal(result['btc_amount']),
                       Decimal(result['exchange_rate']),
                       result['payment_uri'],
                       result['payment_request'].decode('base64'))
        logger.info("created payment order {0}".format(instance.uid))
        return instance

    def send(self, message):
        """
        Accepts:
            message: pb2-encoded Payment message
        Returns:
            payment_ack: pb2-encoded PaymentACK message
        """
        payment_response_url = xbterminal.runtime['remote_server'] + defaults.REMOTE_API_ENDPOINTS['payment_response']
        headers = defaults.EXTERNAL_CALLS_REQUEST_HEADERS.copy()
        headers['Content-Type'] = 'application/bitcoin-payment'
        try:
            response = requests.post(
                url=payment_response_url.format(payment_uid=self.uid),
                headers=headers,
                data=message)
        except requests.exceptions.RequestException as error:
            return None
        payment_ack = response.content
        return payment_ack

    def check(self):
        """
        Returns:
            receipt_url: url or None
        """
        payment_check_url = xbterminal.runtime['remote_server'] + defaults.REMOTE_API_ENDPOINTS['payment_check']
        try:
            response = requests.get(payment_check_url.format(payment_uid=self.uid))
            result = response.json()
        except (requests.exceptions.RequestException, ValueError) as error:
            return None
        if result['paid'] == 1:
            return result['receipt_url']
