import requests


class JSONRPCClient(object):

    def _make_request(self, method, params=None):
        api_url = 'http://127.0.0.1:8888/'
        payload = {
            'method': method,
            'params': params or {},
            'jsonrpc': '2.0',
            'id': 0,
        }
        headers = {'content-type': 'application/json'}
        response = requests.post(api_url,
                                 json=payload,
                                 headers=headers)
        data = response.json()
        return data['result']

    def __getattr__(self, name):
        func = lambda *args: self._make_request(name, *args)  # flake8: noqa
        func.__name__ = name
        return func
