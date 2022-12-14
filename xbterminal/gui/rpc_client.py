from decimal import Decimal
import time

import requests

from xbterminal.gui import exceptions


class use_cache(object):
    """
    Prevents too frequent RPC calls in loops
    """
    def __init__(self, timeout):
        """
        Accepts:
            timeout: minimum interval between calls
        """
        self.cache = {}
        self.timeout = timeout

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            key = str(args) + str(kwargs)
            timestamp, result = self.cache.get(key, (0, None))
            if timestamp + self.timeout < time.time():
                result = func(*args, **kwargs)
                self.cache[key] = (time.time(), result)
            return result
        return wrapper


class JSONRPCClient(object):

    def _make_request(self, method, **params):
        api_url = 'http://127.0.0.1:8888/'
        payload = {
            'method': method,
            'params': params,
            'jsonrpc': '2.0',
            'id': 0,
        }
        headers = {'content-type': 'application/json'}
        response = requests.post(api_url,
                                 json=payload,
                                 headers=headers)
        data = response.json()
        if 'result' in data:
            return data['result']
        else:
            error_type = data['error']['data']['type']
            error_args = data['error']['data']['args']
            error_class = getattr(exceptions, error_type, Exception)
            raise error_class(*error_args)

    def __getattr__(self, name):
        func = lambda **kwargs: self._make_request(name, **kwargs)  # flake8: noqa
        func.__name__ = name
        return func

    @use_cache(1.5)
    def get_connection_status(self):
        return self._make_request('get_connection_status')

    def create_payment_order(self, fiat_amount):
        result = self._make_request('create_payment_order',
                                    fiat_amount=str(fiat_amount))
        return {
            'uid': result['uid'],
            'btc_amount': Decimal(result['btc_amount']),
            'exchange_rate': Decimal(result['exchange_rate']),
            'payment_uri': result['payment_uri'],
        }

    @use_cache(3.0)
    def get_payment_status(self, uid):
        result = self._make_request('get_payment_status', uid=uid)
        return {
            'status': result['status'],
            'paid_btc_amount': Decimal(result['paid_btc_amount']),
        }

    def create_withdrawal_order(self, fiat_amount):
        result = self._make_request('create_withdrawal_order',
                                    fiat_amount=str(fiat_amount))
        return {
            'uid': result['uid'],
            'btc_amount': Decimal(result['btc_amount']),
            'tx_fee_btc_amount': Decimal(result['tx_fee_btc_amount']),
            'exchange_rate': Decimal(result['exchange_rate']),
            'status': result['status'],
        }

    def get_withdrawal_info(self, uid):
        result = self._make_request('get_withdrawal_info', uid=uid)
        return {
            'uid': result['uid'],
            'fiat_amount': Decimal(result['fiat_amount']),
            'btc_amount': Decimal(result['btc_amount']),
            'tx_fee_btc_amount': Decimal(result['tx_fee_btc_amount']),
            'exchange_rate': Decimal(result['exchange_rate']),
            'address': result['address'],
            'status': result['status'],
        }

    def confirm_withdrawal(self, uid, address):
        result = self._make_request('confirm_withdrawal',
                                    uid=uid,
                                    address=address)
        return {
            'btc_amount': Decimal(result['btc_amount']),
            'exchange_rate': Decimal(result['exchange_rate']),
            'status': result['status'],
        }

    @use_cache(3.0)
    def get_withdrawal_status(self, uid):
        return self._make_request('get_withdrawal_status', uid=uid)

    @use_cache(1.0)
    def get_scanned_address(self):
        return self._make_request('get_scanned_address')

    def host_add_credit(self, fiat_amount):
        result = self._make_request('host_add_credit',
                                    fiat_amount=str(fiat_amount))
        return result

    def host_pay_cash(self, fiat_amount):
        result = self._make_request('host_pay_cash',
                                    fiat_amount=str(fiat_amount))
        return result

    @use_cache(2.0)
    def host_get_payout_status(self):
        result = self._make_request('host_get_payout_status')
        return result

    def host_get_payout_amount(self):
        result = self._make_request('host_get_payout_amount')
        return Decimal(result)

    def host_withdrawal_completed(self, uid, fiat_amount):
        result = self._make_request('host_withdrawal_completed',
                                    uid=uid,
                                    fiat_amount=str(fiat_amount))
        return result
