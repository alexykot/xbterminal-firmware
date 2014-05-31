# -*- coding: utf-8 -*-
from decimal import Decimal
import os
import socket
import subprocess
import bitcoinrpc
import bitcoinrpc.connection
import time
import logging

import xbterminal
from xbterminal import defaults
from xbterminal.exceptions import NotEnoughFunds, PrivateKeysMissing

logger = logging.getLogger(__name__)

BITCOIND_HOST = 'node.xbterminal.com'
if xbterminal.remote_config['BITCOIN_NETWORK'] == 'testnet':
    BITCOIND_PORT = 18332
else:
    BITCOIND_PORT = 8332
BITCOIND_USER = 'root'
BITCOIND_PASS = 'password'
BITCOIND_HTTPS = True

connection = None


class BitcoinConnection(bitcoinrpc.connection.BitcoinConnection):

    def sendrawtransaction(self, hex_raw_tx):
        self.proxy.sendrawtransaction(hex_raw_tx)


def init():
    global connection

    if connection is None:
        connection = BitcoinConnection(user=BITCOIND_USER,
                                       password=BITCOIND_PASS,
                                       host=BITCOIND_HOST,
                                       port=BITCOIND_PORT,
                                       use_https=BITCOIND_HTTPS)
    try:
        getInfo()
    except Exception as error:
        logger.exception(error)
    else:
        logger.debug('bitcoind init done')


def getAddressBalance(address):
    global connection

    time.sleep(0.3) #hack required for slow machines like RPi
    balance = connection.getreceivedbyaddress(address, minconf=0)
    balance = Decimal(balance).quantize(defaults.BTC_DEC_PLACES)

    return balance


def getFreshAddress():
    global connection

    address = connection.getnewaddress()

    return address


def getLastUnspentTransactionId(address):
    global connection

    unspent_list = connection.listunspent(minconf=0)
    most_recent_tx_details = None
    for transaction in unspent_list:
        if transaction.address == address:
            tx_details = connection.gettransaction(transaction.txid)
            if most_recent_tx_details is None or most_recent_tx_details['timereceived'] < tx_details['timereceived']:
                most_recent_tx_details = tx_details

    return most_recent_tx_details.txid


def getUnspentTransactions(address):
    global connection

    address_tx_list = []
    unspent_tx_list = connection.listunspent(minconf=0)
    for transaction in unspent_tx_list:
        if transaction.address == address:
            address_tx_list.append({'txid': transaction.txid,
                                    'vout': transaction.vout,
                                    'amount': transaction.amount,
                                    })

    return address_tx_list


def getInfo():
    server_info = connection.getinfo()
    data = {
        'connections': server_info.connections,
    }
    return data


def sendRawTransaction(inputs, outputs):
    global connection

    raw_transaction_unsigned_hex = connection.createrawtransaction(inputs=inputs, outputs=outputs)
    raw_transaction_signed = connection.signrawtransaction(raw_transaction_unsigned_hex)
    if raw_transaction_signed['complete']:
        raw_transaction_signed_hex = raw_transaction_signed['hex']
    else:
        raise PrivateKeysMissing()

    return connection.proxy.sendrawtransaction(raw_transaction_signed_hex)


