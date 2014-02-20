#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
from decimal import Decimal
import hashlib
import json
import requests
import time
import daemon
import resource

print resource.__file__
with daemon.DaemonContext():
    result = requests.get('http://127.0.0.1:18333/getInfo')
    print result.status_code
    print result.text

# result = requests.get('http://127.0.0.1:18333/getFreshAddress')
# print result.status_code
# print result.text

# result = requests.get('http://127.0.0.1:18333/getAddressList')
# print result.status_code
# print result.text

# result = requests.get('http://127.0.0.1:18333/getAddressBalance?address=n2ef38MTRCTu7hA7FBzLcCeonimMn8CC6B')
# print result.status_code
# print result.text

# result = requests.get('http://127.0.0.1:18333/getUnspentTransactions')
# print result.status_code
# print result.text

# phone_testnet_address = "mx3hsWPoqi8TQfo1rJHTSbZqQPUz2WLsff"
# transactions_list = result.json()
# inputs_list = []
# output_amount = Decimal(0)
# for transaction in transactions_list:
#     output_amount = output_amount + Decimal(transaction['amount'])
#     inputs_list.append({'txid': transaction['txid']})
#
# data = {'inputs': inputs_list,
#         'outputs': {phone_testnet_address: str(output_amount-Decimal(20000))}}
#
# if output_amount > 0:
#     result = requests.post('http://127.0.0.1:18333/sendRawTransaction', json.dumps(data))
#     print result.status_code
#     print result.text
