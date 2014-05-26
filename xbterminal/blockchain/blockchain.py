# -*- coding: utf-8 -*-
from decimal import Decimal
import importlib
import logging
import time

import xbterminal
import xbterminal.blockchain.drivers
from xbterminal import defaults
from xbterminal.exceptions import (
    NotEnoughFunds,
    PrivateKeysMissing)

logger = logging.getLogger(__name__)

driver = None

def init():
    global driver

    if driver is None:
        # from xbterminal.blockchain.drivers import bitcoind as driver
        driver = importlib.import_module('.{}'.format(defaults.BLOCKCHAIN_DRIVER), 'xbterminal.blockchain.drivers')

    driver.init()

    logger.debug('blockchain driver {} init done'.format(defaults.BLOCKCHAIN_DRIVER))


def getAddressBalance(address):
    global driver

    return driver.getAddressBalance(address)


def getFreshAddress():
    global driver

    return driver.getFreshAddress()


def getLastUnspentTransactionId(address):
    global driver

    return driver.getLastUnspentTransactionId(address)


def getInfo():
    return driver.getInfo()


def getTransactionConfidence(transaction_hash):
    return driver.getTransactionConfidence(transaction_hash)


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


def isValidAddress(address):
    """
    https://en.bitcoin.it/wiki/List_of_address_prefixes
    """
    network = xbterminal.remote_config['BITCOIN_NETWORK']
    if network == "testnet":
        return address.startswith("m") or address.startswith("n")
    else:
        return address.startswith("1") or address.startswith("3")


def updateDriverState(is_running):
    global driver
    if is_running:
        if hasattr(driver, "unavailable_since"):
            del driver.unavailable_since
    else:
        unavailable_since = getattr(driver, "unavailable_since", None)
        if unavailable_since is None:
            driver.unavailable_since = time.time()
        elif time.time() - unavailable_since >= 120:
            if driver.__name__.endswith("bitcoinj"):
                logger.warning("switching to bitcoind driver")
                driver = importlib.import_module(".bitcoind", "xbterminal.blockchain.drivers")
                driver.init()
