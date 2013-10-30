# -*- coding: utf-8 -*-
from decimal import Decimal
import random
import sys
import time

from electrum.simple_config import SimpleConfig
from electrum.wallet import Wallet, WalletSynchronizer
from electrum.verifier import WalletVerifier
from electrum.interface import Interface

from nfc_terminal import defaults
from nfc_terminal.helpers.misc import satoshi2BTC, BTC2satoshi


WALLET_PATH = '/root/.electrum/electrum.dat'
WALLET_GAP_LIMIT = 1

wallet = None
synchronizer = None
addresses_subscribed = []


def init():
    global wallet, synchronizer

    config = SimpleConfig({'wallet_path':WALLET_PATH})


    if wallet is None:
        wallet = Wallet(config)
        interface = Interface(config, True)
        interface.start(wait = False)
        interface.send([('server.peers.subscribe',[])])
        wallet.interface = interface

        verifier = WalletVerifier(interface, config)
        verifier.start()
        wallet.set_verifier(verifier)

        synchronizer = WalletSynchronizer(wallet, config)
        synchronizer.start()

        wallet.update()

def stop(halt=False):
    global wallet, synchronizer

    wallet.verifier.stop()
    synchronizer.stop()
    wallet.interface.stop()
    wallet.verifier = None
    wallet.interface = None
    wallet = None
    synchronizer = None
    time.sleep(0.1)
    if halt:
        sys.exit(0)

def restart():
    stop()
    init()

def getAddressBalance(address, exclude_unconfirmed=False):
    global wallet, addresses_subscribed

    if address not in addresses_subscribed:
        wallet.synchronizer.subscribe_to_addresses(address)
        addresses_subscribed.append(address)

    confirmed, unconfirmed = wallet.get_addr_balance(address)
    balance = Decimal(0).quantize(defaults.BTC_DEC_PLACES)
    balance = balance + satoshi2BTC(confirmed)
    if not exclude_unconfirmed:
        balance = balance + satoshi2BTC(unconfirmed)

    return balance


def getFreshAddress():
    global wallet

    address = wallet.create_new_address(0, False)
    wallet.save()
    restart() #this is dirty

    return address


def sendTransaction(outputs, from_addr=None, fee=None, change_addr=None):
    global wallet

    if fee is not None:
        satoshi_fee = BTC2satoshi(fee)

    satoshi_outputs = []
    for address, amount in outputs:
        satoshi_outputs.append((address, BTC2satoshi(amount)))

    transaction = wallet.mktx(outputs=satoshi_outputs,
                              password=None,
                              fee=satoshi_fee,
                              change_addr=change_addr,
                              domain=[from_addr])
    print transaction
    result, hash = wallet.sendtx(transaction)
    print result
    print hash
    wallet.save()

    if result:
        return hash
    else:
        return False
