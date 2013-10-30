# -*- coding: utf-8 -*-
from decimal import Decimal
import bitcoinrpc

from nfc_terminal import defaults


connection = None

def init():
    global connection

    if connection is None:
        if defaults.BITCOIND_HOST == 'localhost':
            connection = bitcoinrpc.connect_to_local()
        else:
            connection = bitcoinrpc.connect_to_remote(defaults.BITCOIND_USER,
                                                      defaults.BITCOIND_PASS,
                                                      defaults.BITCOIND_HOST,
                                                      defaults.BITCOIND_PORT)


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

    connection.createrawtransaction()

    hash = connection.sendmany(fromaccount='',
                               todict=todict,
                               minconf=0)

    return hash
