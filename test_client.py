#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import hashlib
import json
import requests
import base58

# result = requests.post('http://127.0.0.1:8000', data=json.dumps({'data_piece': 'something of meaning'}))


# result = requests.get('http://127.0.0.1:18333/getAddressList')
# print result.status_code
# print result.text


result = requests.get('http://127.0.0.1:18333/getAddressBalance?address=mph2EM4bKEaQQkpHw8rSjoQut1zGShk2Xm')
print result.status_code
print result.text

result = requests.get('http://127.0.0.1:18333/getAddressList')
print result.status_code
print result.text

result = requests.get('http://127.0.0.1:18333/getUnspentTransactions')
print result.status_code
print result.text
