#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
from decimal import Decimal
import json
import sys
import os
import time
import datetime
import requests

include_path = os.path.abspath(os.path.join(__file__, os.pardir))
sys.path.insert(0, include_path)

import xbterminal
import xbterminal.defaults
import xbterminal.blockchain
import xbterminal.stages
import xbterminal.exceptions
import xbterminal.helpers
import xbterminal.helpers.nfcpy
import xbterminal.main

xbterminal.defaults.PROJECT_ABS_PATH = include_path

xbterminal.helpers.configs.load_local_state()
xbterminal.helpers.configs.load_remote_config()
xbterminal.blockchain.init()

# amount_btc = '0.0002'
# payment_local_addr = xbterminal.blockchain.getFreshAddress()
# payment_remote_addr = '1FCrwY2CsLJgsmbogSunECwCa6WswBBrfz'
#
#
#
# while True:
#     if not xbterminal.helpers.nfcpy.is_active():
#         bitcoin_uri = xbterminal.stages.getBitcoinURI(payment_local_addr, amount_btc)
#         xbterminal.helpers.nfcpy.start(bitcoin_uri)
#         print 'NFC activated'
#
#     current_balance = xbterminal.blockchain.getAddressBalance(payment_local_addr)
#     if current_balance > 0:
#         print 'balance received'
#         xbterminal.helpers.nfcpy.stop()
#         outputs = {payment_remote_addr: Decimal(0.0001)}
#         try:
#             result = xbterminal.blockchain.sendRawTransaction(outputs, from_addr=payment_local_addr)
#             print 'payment forwarded'
#             exit()
#         except xbterminal.exceptions.NotEnoughFunds as error:
#             print "NotEnoughFunds"
#             print error.amount_available
#             print error.amount_to_spend
#             exit()
#
#     time.sleep(0.2)
#
#

# xbterminal.runtime = {'remote_server' : 'http://151.248.122.78'}
# print xbterminal.stages.logTransaction('1FCrwY2CsLJgsmbogSunECwCa6WswBBrfz', '1FCrwY2CsLJgsmbogSunECwCa6WswBBrfz', '1FCrwY2CsLJgsmbogSunECwCa6WswBBrfz',
#                    '09945115fd481dc008cf265bac82cc57c8e2846a280d05efcbac604afb17de5c', '09945115fd481dc008cf265bac82cc57c8e2846a280d05efcbac604afb17de5c',
#                    0,
#                    0.12, 0.0001, 0, 0, 0.0005,
#                    'GBP', 0.512)


