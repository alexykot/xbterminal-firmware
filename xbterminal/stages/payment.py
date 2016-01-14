# -*- coding: utf-8 -*-
from decimal import Decimal
import logging

import xbterminal
from xbterminal import defaults
from xbterminal.helpers import api

logger = logging.getLogger(__name__)


class Payment(object):

    def __init__(self, uid, btc_amount, exchange_rate, payment_uri, request):
        self.uid = uid
        self.btc_amount = btc_amount
        self.exchange_rate = exchange_rate
        self.payment_uri = payment_uri
        self.request = request.decode('base64') if request else None

    @classmethod
    def create_order(cls, fiat_amount, bt_mac):
        """
        Accepts:
            fiat_amount: amount to pay (Decimal)
            bt_mac: mac address
        Returns:
            class instance or None
        """
        payment_init_url = api.get_url('payment_init')
        payload = {
            'device_key': xbterminal.runtime['device_key'],
            'amount': float(fiat_amount),
            'bt_mac': bt_mac,
        }
        try:
            response = api.send_request('post', payment_init_url, data=payload)
            result = response.json()
        except Exception as error:
            return None
        # Parse result
        instance = cls(
            result['payment_uid'],
            Decimal(result['btc_amount']).quantize(defaults.BTC_DEC_PLACES),
            Decimal(result['exchange_rate']).quantize(defaults.BTC_DEC_PLACES),
            result['payment_uri'],
            result.get('payment_request'))
        logger.info("created payment order {0}".format(instance.uid))
        return instance

    def send(self, message):
        """
        Accepts:
            message: pb2-encoded Payment message
        Returns:
            payment_ack: pb2-encoded PaymentACK message
        """
        payment_response_url = api.get_url('payment_response',
                                           uid=self.uid)
        headers = {'Content-Type': 'application/bitcoin-payment'}
        try:
            response = api.send_request(
                'post',
                url=payment_response_url,
                data=message,
                headers=headers)
        except Exception as error:
            return None
        payment_ack = response.content
        return payment_ack

    def check(self):
        """
        Returns:
            receipt_url: url or None
        """
        payment_check_url = api.get_url('payment_check', uid=self.uid)
        try:
            response = api.send_request('get', payment_check_url)
            result = response.json()
        except Exception as error:
            return None
        if result['paid'] == 1:
            return api.get_url('receipt', receipt_key=self.uid)
