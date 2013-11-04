#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import sys
import os
import requests

include_path = os.path.abspath(os.path.join(__file__, os.pardir))
sys.path.insert(0, include_path)

import xbterminal
import xbterminal.defaults

xbterminal.defaults.PROJECT_ABS_PATH = include_path

API_KEY = 'yIPgOATBZ1WHvhvKE6tpOqOuzBh8PGeDN5JZBP46eCc'

# response = requests.post(url='https://bitpay.com/api/invoice',
#                          data={'price':0.01,
#                                'currency':'GBP'},
#                          auth=(API_KEY, ''))
#
# result = response.json()
# print result
#
# invoice_id = result['id']
#

invoice_id = 'GH6wwb1zD2FDvGZWexPgBY'
invoice_url = "https://bitpay.com/api/invoice/{}".format(invoice_id)
headers = {'Content-type' : 'application/json'}
response =  requests.get(url=invoice_url,
                         headers=headers,
                         auth=(API_KEY, ''))
print response.text
