# -*- coding: utf-8 -*-
from decimal import Decimal
import json
import sys
import bitcoinrpc
import bitcoinrpc.connection

from xbterminal import defaults
from xbterminal.exceptions import NotEnoughFunds, PrivateKeysMissing


connection = None

class BitcoinConnection(bitcoinrpc.connection.BitcoinConnection):
    def sendrawtransaction(self, hex_raw_tx):

        self.proxy.sendrawtransaction(hex_raw_tx)

def init():
    global connection

    if connection is None:
        connection = BitcoinConnection(user=defaults.BITCOIND_USER,
                                       password=defaults.BITCOIND_PASS,
                                       host=defaults.BITCOIND_HOST,
                                       port=defaults.BITCOIND_PORT,
                                       use_https=False)


def getAddressBalance(address):
    global connection

    balance = connection.getreceivedbyaddress(address, minconf=0)
    balance = Decimal(balance).quantize(defaults.BTC_DEC_PLACES)

    return balance


def getFreshAddress():
    global connection

    address = connection.getnewaddress()

    return address


def sendTransaction(outputs):
    global connection

    todict = {}
    for output_address in outputs:
        todict[output_address] = float(outputs[output_address])

    print 'sending to:'
    print todict

    hash = connection.sendmany(fromaccount='',
                               todict=todict,
                               minconf=0)



    return hash


# Sends transaction from given address using all currently unspent inputs for that address.
# by default all change is sent to fees address
def sendRawTransaction(outputs, from_addr, change_addr=None):
    global connection

    transaction_hash = None

    if change_addr is None:
        change_addr = defaults.OUR_FEE_BITCOIN_ADDRESS

    float_outputs = {}
    total_to_pay = Decimal(0).quantize(defaults.BTC_DEC_PLACES)
    for output_address in outputs:
        total_to_pay = total_to_pay + outputs[output_address]
        float_outputs[output_address] = float(outputs[output_address])


    unspent_tx_list = connection.listunspent(minconf=0)
    total_available_to_spend = Decimal(0).quantize(defaults.BTC_DEC_PLACES)
    inputs = []
    for transaction in unspent_tx_list:
        if transaction.address == from_addr:
            total_available_to_spend = total_available_to_spend + transaction.amount
            inputs.append({'txid': transaction.txid,
                           'vout': transaction.vout,
                             })

    if total_available_to_spend < total_to_pay+defaults.BTC_DEFAULT_FEE:
        raise NotEnoughFunds()

    if total_available_to_spend > total_to_pay+defaults.BTC_DEFAULT_FEE:
        if change_addr not in outputs:
            outputs[change_addr] = Decimal(0).quantize(defaults.BTC_DEC_PLACES)
        outputs[change_addr] = outputs[change_addr] + (total_available_to_spend - total_to_pay - defaults.BTC_DEFAULT_FEE)
        float_outputs[change_addr] = float(outputs[change_addr])


    raw_transaction_unsigned_hex = connection.createrawtransaction(inputs=inputs, outputs=float_outputs)
    raw_transaction_signed = connection.signrawtransaction(raw_transaction_unsigned_hex)
    if raw_transaction_signed['complete']:
        raw_transaction_signed_hex = raw_transaction_signed['hex']
    else:
        raise PrivateKeysMissing()

    transaction_hash = connection.proxy.sendrawtransaction(raw_transaction_signed_hex)

    return transaction_hash