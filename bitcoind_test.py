#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
from decimal import Decimal
import json
import sys
import os

include_path = os.path.abspath(os.path.join(__file__, os.pardir))
sys.path.insert(0, include_path)

import nfc_terminal
import nfc_terminal.defaults

nfc_terminal.defaults.PROJECT_ABS_PATH = include_path

import time
import bitcoinrpc





conn = bitcoinrpc.connect_to_remote('root', 'password', host='192.168.51.136', port=8332)
# print conn.getinfo()

conn.sendmany(fromaccount='',
              todict={'1G2bcoCKj8s9GYheqQgU5CHSLCtGjyP9Vz': 0.0001,
                      '1BcYr49mxKRoC3i2B84GMMKLEpUKG17H6r': 0.0002,
                      },
              minconf=0)

print conn.getreceivedbyaddress('18eqyW3koAAeEuQSEFdCeAtPE3V4pb6YdP', minconf=0)
#
# address = conn.getnewaddress()
# print address
#
# received = False
# while not received:
#     balance = conn.getbalance(address)
#     print balance
#     if balance > 0:
#         received = True
#
#     time.sleep(1)
#
# conn.sendmany('')
