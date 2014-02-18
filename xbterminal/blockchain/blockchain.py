# -*- coding: utf-8 -*-
from decimal import Decimal
import importlib
import os
import socket
import subprocess
import bitcoinrpc
import bitcoinrpc.connection
import time

import xbterminal
import xbterminal.blockchain.drivers
from xbterminal import defaults
from xbterminal.exceptions import NotEnoughFunds, PrivateKeysMissing
from xbterminal.helpers.misc import log


driver = None

def init():
    global driver

    if driver is None:
        # from xbterminal.blockchain.drivers import bitcoind as driver
        driver = importlib.import_module('.{}'.format(defaults.BLOCKCHAIN_DRIVER), 'xbterminal.blockchain.drivers')

    driver.init()

    log('blockchain driver {} init done'.format(defaults.BLOCKCHAIN_DRIVER))


def getAddressBalance(address):
    global driver

    return driver.getAddressBalance(address)


def getFreshAddress():
    global driver

    return driver.getFreshAddress()


def getLastUnspentTransaction(address):
    global driver

    return driver.getLastUnspentTransaction(address)


# Sends transaction from given address using all currently unspent inputs for that address.
# by default all change is sent to fees address
def sendTransaction(outputs, from_addr, change_addr=None):
    global driver

    if change_addr is None:
        change_addr = xbterminal.remote_config['OUR_FEE_BITCOIN_ADDRESS']

    float_outputs = {}
    total_to_pay = Decimal(0).quantize(defaults.BTC_DEC_PLACES)
    for output_address in outputs:
        total_to_pay = total_to_pay + outputs[output_address]
        float_outputs[output_address] = float(outputs[output_address])

    unspent_tx_list = driver.getUnspentTransactions(from_addr)
    total_available_to_spend = Decimal(0).quantize(defaults.BTC_DEC_PLACES)
    inputs = []
    for transaction in unspent_tx_list:
        total_available_to_spend = total_available_to_spend + transaction['amount']
        inputs.append({'txid': transaction['txid'],
                       'vout': transaction['vout'],
                         })

    total_to_pay_with_fee = Decimal(total_to_pay + defaults.BTC_DEFAULT_FEE).quantize(defaults.BTC_DEC_PLACES)

    if total_available_to_spend < total_to_pay_with_fee:
        raise NotEnoughFunds(total_available_to_spend, total_to_pay_with_fee)

    if total_available_to_spend > total_to_pay_with_fee:
        if change_addr not in outputs:
            outputs[change_addr] = Decimal(0).quantize(defaults.BTC_DEC_PLACES)
        change_amount = outputs[change_addr] + (total_available_to_spend - total_to_pay - defaults.BTC_DEFAULT_FEE)
        if change_amount > 0:
            outputs[change_addr] = change_amount
        float_outputs[change_addr] = float(outputs[change_addr])

    nonempty_float_outputs = {}

    for address in float_outputs:
        if float_outputs[address] > 0:
            nonempty_float_outputs[address] = float_outputs[address]

    return driver.sendRawTransaction(inputs=inputs, outputs=nonempty_float_outputs)





