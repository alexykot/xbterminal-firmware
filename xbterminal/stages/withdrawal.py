from decimal import Decimal
import logging
import re

import xbterminal
from xbterminal.helpers import api

logger = logging.getLogger(__name__)


def get_bitcoin_address(message):
    match = re.match(r'(bitcoin:)?([a-zA-Z0-9]{26,35})(\?|$)', message)
    if match:
        return match.group(2)


class Withdrawal(object):

    def __init__(self, uid, btc_amount, exchange_rate):
        self.uid = uid
        self.btc_amount = btc_amount
        self.exchange_rate = exchange_rate

    @classmethod
    def create_order(cls, fiat_amount):
        """
        Accepts:
            fiat_amount: amount to withdraw (Decimal)
        Returns:
            class instance or None
        """
        url = api.get_url('withdrawal_init')
        payload = {
            'device': xbterminal.runtime['device_key'],
            'amount': str(fiat_amount),
        }
        response = api.send_request('post', url, payload, signed=True)
        result = response.json()
        # Parse result
        instance = cls(result['uid'],
                       Decimal(result['btc_amount']),
                       Decimal(result['exchange_rate']))
        logger.info('created withdrawal order {0}'.format(instance.uid))
        return instance

    def confirm(self, customer_address):
        """
        Accepts:
            customer address: string
        """
        url = api.get_url('withdrawal_confirm', uid=self.uid)
        payload = {'address': customer_address}
        try:
            response = api.send_request('post', url, payload, signed=True)
            result = response.json()
        except Exception as error:
            return None
        logger.info('confirmed withdrawal order {0}'.format(self.uid))

    def check(self):
        """
        Returns:
            receipt_url or None
        """
        url = api.get_url('withdrawal_check', uid=self.uid)
        try:
            response = api.send_request('get', url)
            result = response.json()
        except Exception as error:
            return None
        if result['status'] == 'completed':
            return api.get_url('receipt', receipt_key=self.uid)
