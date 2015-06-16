from decimal import Decimal
import logging
import re
import requests

import xbterminal
from xbterminal.defaults import REMOTE_API_ENDPOINTS
from xbterminal.helpers import crypto

logger = logging.getLogger(__name__)


def get_bitcoin_address(message):
    match = re.match(r'(bitcoin:)?([a-zA-Z0-9]{26,35})(\?|$)', message)
    if match:
        return match.group(2)


def get_api_url(endpoint_name, **kwargs):
    url = (xbterminal.runtime['remote_server'] +
           REMOTE_API_ENDPOINTS[endpoint_name])
    if not kwargs:
        return url
    else:
        return url.format(**kwargs)


def send_signed_request(url, data):
    """
    Create and send signed POST request
    with X-Signature header
    Returns:
        response
    """
    # Create
    req = requests.Request('POST', url, data=data)
    prepared_req = req.prepare()
    signature = crypto.create_signature(prepared_req.body)
    prepared_req.headers['X-Signature'] = signature
    # Send
    session = requests.Session()
    return session.send(prepared_req)


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
        url = get_api_url('withdrawal_init')
        payload = {
            'device': xbterminal.device_key,
            'amount': str(fiat_amount),
        }
        try:
            response = send_signed_request(url, payload)
            response.raise_for_status()
            result = response.json()
        except Exception as error:
            logger.exception(error)
            return None
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
        url = get_api_url('withdrawal_confirm', uid=self.uid)
        payload = {'address': customer_address}
        try:
            response = send_signed_request(url, payload)
            response.raise_for_status()
            result = response.json()
        except Exception as error:
            logger.exception(error)
            return None
        logger.info('confirmed withdrawal order {0}'.format(self.uid))

    def check(self):
        """
        Returns:
            receipt_url or None
        """
        url = get_api_url('withdrawal_check', uid=self.uid)
        try:
            response = requests.get(url)
            response.raise_for_status()
            result = response.json()
        except Exception as error:
            logger.exception(error)
            return None
        if result['status'] == 'completed':
            return get_api_url('receipt', receipt_key=self.uid)
