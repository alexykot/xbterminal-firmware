# -*- coding: utf-8 -*-
from decimal import Decimal
import json
import os
import socket
import subprocess
import time
import logging

import psutil
import requests
import simplejson

import xbterminal
from xbterminal import defaults
from xbterminal.exceptions import NotEnoughFunds, PrivateKeysMissing

logger = logging.getLogger(__name__)

BITCOINJ_SERVER_ABSPATH = os.path.join(defaults.PROJECT_ABS_PATH, 'bitcoinj_server', 'server.py')
BITCOINJ_HOST = '127.0.0.1'
if xbterminal.remote_config['BITCOIN_NETWORK'] == 'testnet':
    BITCOINJ_PORT = 18333
else:
    BITCOINJ_PORT = 8333

bitcoinj_url = 'http://{host}:{port}/'.format(host=BITCOINJ_HOST, port=BITCOINJ_PORT)

def init():
    global bitcoinj_url

    try:
        getInfo()
    except requests.exceptions.ConnectionError:
        if xbterminal.local_state.get("manage_bitcoinj_process", True):
            _start_bitcoinj()
        else:
            logger.warning("bitcoinj not started, ignoring")
    else:
        logger.debug('bitcoinj init done')


def _start_bitcoinj():
    global bitcoinj_url, xbterminal

    logger.debug('bitcoinj starting')
    command = [BITCOINJ_SERVER_ABSPATH, ]
    if xbterminal.remote_config['BITCOIN_NETWORK'] == 'testnet':
        command.append('--testnet')

    logfile_system = os.path.join(defaults.PROJECT_ABS_PATH,
                                  defaults.RUNTIME_PATH,
                                  'bitcoinj_console.system.log')
    logfile_error = os.path.join(defaults.PROJECT_ABS_PATH,
                                 defaults.RUNTIME_PATH,
                                 'bitcoinj_console.error.log')

    logfile_system = open(logfile_system, 'ab')
    logfile_error = open(logfile_error, 'ab')
    subprocess.Popen(command, stdout=logfile_system, stderr=logfile_error)
    while True:
        try:
            bitcoinj_info_url = bitcoinj_url + 'getInfo'
            result = requests.get(bitcoinj_info_url)
            break
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    logger.debug('bitcoinj started')


def kill_bitcoinj():
    logger.warning("killing bitcoinj...")
    for p in psutil.process_iter():
        if p.exe().startswith(BITCOINJ_SERVER_ABSPATH):
            p.kill()
            logger.warning("bitcoinj killed (pid: {0})".format(p.pid()))
            break


def getAddressBalance(address):
    result = requests.get(bitcoinj_url + 'getAddressBalance?address={}'.format(address))

    balance_satoshis = Decimal(result.json())
    balance = Decimal(balance_satoshis / defaults.SATOSHI_FACTOR).quantize(defaults.BTC_DEC_PLACES)

    return balance


def getFreshAddress():
    result = requests.get(bitcoinj_url + 'getFreshAddress')
    new_address = result.json()

    return new_address


def getLastUnspentTransactionId(from_address):
    transactions = getUnspentTransactions(from_address)
    return transactions[len(transactions)-1]['txid']


def getUnspentTransactions(from_address):
    address_tx_list = []
    result = requests.get(bitcoinj_url + 'getUnspentTransactions')
    try:
        unspent_tx_list = result.json()
    except simplejson.JSONDecodeError:
        logger.debug('getUnspentTransactions json error, json body: {}'.format(result.body))
        return []

    for transaction in unspent_tx_list:
        if from_address in transaction['addresses']:
            transaction['vout'] = 0 #hack for compatibility with bitcoind
            transaction['amount'] = Decimal(Decimal(transaction['amount']) / defaults.SATOSHI_FACTOR).quantize(defaults.BTC_DEC_PLACES)
            address_tx_list.append(transaction)

    return address_tx_list


def getInfo():
    response = requests.get(bitcoinj_url + "getInfo", timeout=5)
    return response.json()


def getTransactionConfidence(transaction_hash):
    response = requests.get(
        bitcoinj_url + "getTransactionConfidence?transaction_hash={}".format(transaction_hash))
    data = response.json()
    confidence_type = data['confidence_type']
    broadcast_peers = int(data['broadcast_peers'])
    return confidence_type, broadcast_peers


# Sends transaction from given address using all currently unspent inputs for that address.
# by default all change is sent to fees address
def sendRawTransaction(inputs, outputs):
    integer_outputs = {}
    for output_address in outputs:
        integer_outputs[output_address] = int(Decimal(outputs[output_address]) * defaults.SATOSHI_FACTOR)

    data = {'inputs': inputs,
            'outputs': integer_outputs}

    result = requests.post(bitcoinj_url + 'sendRawTransaction', json.dumps(data))
    return result.json()


