# -*- coding: utf-8 -*-
from decimal import Decimal
import logging
import requests

import xbterminal
from xbterminal import defaults

logger = logging.getLogger(__name__)


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
            logger.error("create payment order: {0}".format(error.__class__.__name__))
            return None
        # Parse result
        instance = cls(
            result['payment_uid'],
            Decimal(result['btc_amount']).quantize(defaults.BTC_DEC_PLACES),
            Decimal(result['exchange_rate']).quantize(defaults.BTC_DEC_PLACES),
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
