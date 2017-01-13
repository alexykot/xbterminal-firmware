# -*- coding: utf-8 -*-
from decimal import Decimal
import logging

from xbterminal.rpc.utils import api

logger = logging.getLogger(__name__)


class Payment(object):

    def __init__(self, uid, btc_amount, paid_btc_amount, exchange_rate,
                 status, payment_uri, request):
        self.uid = uid
        self.btc_amount = btc_amount
        self.paid_btc_amount = paid_btc_amount
        self.exchange_rate = exchange_rate
        self.status = status
        self.payment_uri = payment_uri
        self.request = request.decode('base64') if request else None

    @classmethod
    def create_order(cls, device_key, fiat_amount, bt_mac):
        """
        Accepts:
            device_key: device key, string
            fiat_amount: amount to pay (Decimal)
            bt_mac: mac address
        Returns:
            class instance or None
        """
        payment_init_url = api.get_url('payment_init')
        payload = {
            'device': device_key,
            'amount': str(fiat_amount),
            'bt_mac': bt_mac,
        }
        response = api.send_request('post', payment_init_url, data=payload)
        result = response.json()
        # Parse result
        instance = cls(
            result['uid'],
            Decimal(result['btc_amount']),
            Decimal(result['paid_btc_amount']),
            Decimal(result['exchange_rate']),
            result['status'],
            result['payment_uri'],
            result.get('payment_request'))
        logger.info('created payment order {0}'.format(instance.uid))
        return instance

    def cancel(self):
        url = api.get_url('payment_cancel', uid=self.uid)
        try:
            api.send_request('post', url)
        except Exception as error:
            logger.exception(error)
            return False
        else:
            logger.info('cancelled payment order {0}'.format(self.uid))
            return True

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
        except Exception:
            return None
        payment_ack = response.content
        return payment_ack

    def check(self):
        """
        Returns:
            status: payment status or None in case of error
        """
        payment_check_url = api.get_url('payment_check', uid=self.uid)
        try:
            response = api.send_request('get', payment_check_url)
            result = response.json()
        except Exception:
            pass
        else:
            if self.status != result['status']:
                logger.info('order status changed, {0} -> {1}'.format(
                    self.status, result['status']))
            self.paid_btc_amount = Decimal(result['paid_btc_amount'])
            self.status = result['status']

    @property
    def receipt_url(self):
        return api.get_url('payment_receipt', uid=self.uid)
