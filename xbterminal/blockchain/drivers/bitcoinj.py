# -*- coding: utf-8 -*-
from decimal import Decimal
import json
import os
import socket
import subprocess
import bitcoinrpc
import bitcoinrpc.connection
import time
import requests

import xbterminal
from xbterminal import defaults
from xbterminal.exceptions import NotEnoughFunds, PrivateKeysMissing
from xbterminal.helpers.misc import log

BITCOINJ_SERVER_ABSPATH = os.path.join(defaults.PROJECT_ABS_PATH, 'bitcoinj_server', 'server.py')
BITCOINJ_HOST = '127.0.0.1'
if defaults.BLOCKCHAIN_USE_TESTNET:
    BITCOINJ_PORT = 18333
else:
    BITCOINJ_PORT = 8333

bitcoinj_url = 'http://{host}:{port}/'.format(host=BITCOINJ_HOST, port=BITCOINJ_PORT)

def init():
    global bitcoinj_url

    try:
        bitcoinj_info_url = bitcoinj_url + 'getInfo'
        print bitcoinj_info_url
        requests.get(bitcoinj_info_url)
    except requests.exceptions.ConnectionError:
        _start_bitcoinj()

    log('bitcoinj init done')


def _start_bitcoinj():
    global bitcoinj_url

    log('bitcoinj starting')
    subprocess.Popen([BITCOINJ_SERVER_ABSPATH, ])
    while True:
        try:
            bitcoinj_info_url = bitcoinj_url + 'getInfo'
            result = requests.get(bitcoinj_info_url)
            break
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    log('bitcoinj started')


def getAddressBalance(address):
    global connection

    result = requests.get(bitcoinj_url + 'getAddressBalance?address={}'.format(address))

    balance_satoshis = Decimal(result.json())
    balance = Decimal(balance_satoshis / defaults.SATOSHI_FACTOR).quantize(defaults.BTC_DEC_PLACES)

    return balance


def getFreshAddress():
    global connection

    result = requests.get(bitcoinj_url + 'getFreshAddress')
    new_address = result.json()

    return new_address


def getLastUnspentTransactionId(from_address):
    global connection

    transactions = getUnspentTransactions(from_address)
    return transactions[len(transactions)-1]['txid']


def getUnspentTransactions(from_address):
    global connection

    address_tx_list = []
    result = requests.get(bitcoinj_url + 'getUnspentTransactions')
    unspent_tx_list = result.json()
    for transaction in unspent_tx_list:
        if from_address in transaction['addresses']:
            transaction['vout'] = 0 #hack for compatibility with bitcoind
            transaction['amount'] = Decimal(Decimal(transaction['amount']) / defaults.SATOSHI_FACTOR).quantize(defaults.BTC_DEC_PLACES)
            address_tx_list.append(transaction)

    return address_tx_list


# Sends transaction from given address using all currently unspent inputs for that address.
# by default all change is sent to fees address
def sendRawTransaction(inputs, outputs):
    global connection

    integer_outputs = {}
    for output_address in outputs:
        integer_outputs[output_address] = int(Decimal(outputs[output_address]) * defaults.SATOSHI_FACTOR)

    data = {'inputs': inputs,
            'outputs': integer_outputs}

    result = requests.post(bitcoinj_url + 'sendRawTransaction', json.dumps(data))
    return result.json()


