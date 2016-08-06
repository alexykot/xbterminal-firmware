import requests

from xbterminal import exceptions


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
            raise getattr(exceptions, error_type)

    def __getattr__(self, name):
        func = lambda **kwargs: self._make_request(name, **kwargs)  # flake8: noqa
        func.__name__ = name
        return func
