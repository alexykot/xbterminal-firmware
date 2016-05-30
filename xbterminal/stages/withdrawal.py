from decimal import Decimal
import logging
import re

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
        self.confirmed = False

    @classmethod
    def create_order(cls, device_key, fiat_amount):
        """
        Accepts:
            device_key: device key, string
            fiat_amount: amount to withdraw (Decimal)
        Returns:
            class instance or None
        """
        url = api.get_url('withdrawal_init')
        payload = {
            'device': device_key,
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
        api.send_request('post', url, payload, signed=True)
        self.confirmed = True
        logger.info('confirmed withdrawal order {0}'.format(self.uid))

    def cancel(self):
        url = api.get_url('withdrawal_cancel', uid=self.uid)
        try:
            api.send_request('post', url, signed=True)
        except Exception as error:
            return None
        logger.info('cancelled withdrawal order {0}'.format(self.uid))

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
            return self.receipt_url

    @property
    def receipt_url(self):
        return api.get_url('withdrawal_receipt', uid=self.uid)
