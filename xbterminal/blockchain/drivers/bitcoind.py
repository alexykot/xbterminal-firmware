# -*- coding: utf-8 -*-
from decimal import Decimal
import os
import socket
import subprocess
import time
import logging

import xbterminal
from xbterminal import defaults
from xbterminal.exceptions import PrivateKeysMissing

import bitcoin
import bitcoin.rpc
from bitcoin.core import COIN, x, b2x, b2lx, CTransaction

logger = logging.getLogger(__name__)

BITCOIND_HOST = 'node.xbterminal.io'
BITCOIND_USER = 'root'
BITCOIND_PASS = 'password'

try:
    from xbterminal.bitcoind_auth import BITCOIND_USER, BITCOIND_PASS
except:
    pass

connection = None


def init():
    global connection
    if connection is None:
        bitcoin.SelectParams(xbterminal.remote_config['BITCOIN_NETWORK'])
        service_url = "https://{user}:{password}@{host}:{port}".format(
            user=BITCOIND_USER,
            password=BITCOIND_PASS,
            host=BITCOIND_HOST,
            port=bitcoin.params.RPC_PORT)
        connection = bitcoin.rpc.Proxy(service_url)
    try:
        getInfo()
    except Exception as error:
        logger.exception(error)
    else:
        logger.debug('bitcoind init done')


def getAddressBalance(address):
    time.sleep(0.3) #hack required for slow machines like RPi
    minconf = 0
    balance = connection.getreceivedbyaddress(address, minconf)
    balance = Decimal(balance).quantize(defaults.BTC_DEC_PLACES)
    return balance


def getFreshAddress():
    address = connection.getnewaddress()
    return str(address)


def getLastUnspentTransactionId(address):
    txouts = connection.listunspent(minconf=0, addrs=[address])
    most_recent_tx_id = None
    most_recent_tx_timereceived = 0
    for out in txouts:
        txid = out['outpoint'].hash
        tx_details = connection.gettransaction(txid)
        if most_recent_tx_timereceived < tx_details['timereceived']:
            most_recent_tx_id = tx_details['txid']
    return most_recent_tx_id


def getUnspentTransactions(address):
    txouts = connection.listunspent(minconf=0, addrs=[address])
    transactions = []
    for out in txouts:
        transactions.append({
            'txid': b2lx(out['outpoint'].hash),
            'vout': out['outpoint'].n,
            'amount': Decimal(out['amount']) / COIN,
        })
    return transactions


def getInfo():
    server_info = connection.getinfo()
    data = {
        'connections': server_info['connections'],
    }
    return data


def sendRawTransaction(inputs, outputs):
    raw_transaction_unsigned_hex = connection.createrawtransaction(inputs, outputs)
    raw_transaction_unsigned = CTransaction.deserialize(x(raw_transaction_unsigned_hex))
    result = connection.signrawtransaction(raw_transaction_unsigned)
    if result.get('complete') != 1:
        raise PrivateKeysMissing()
    tx_id = connection.sendrawtransaction(result['tx'])
    return b2x(tx_id)
