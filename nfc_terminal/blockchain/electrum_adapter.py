# -*- coding: utf-8 -*-
import random
import sys
from decimal import Decimal
from electrum import Interface
from electrum import Wallet, WalletStorage, SimpleConfig, Transaction, Network, bitcoin


from nfc_terminal import defaults
from nfc_terminal.helpers.misc import satoshi2BTC


WALLET_PATH = '/root/.electrum/electrum.dat'
MASTER_PUBLIC_KEY = 'public_key'
MASTER_CHAIN = 'chain'

network = None
wallet = None

def _init():
    global network, wallet

    config = SimpleConfig({'wallet_path':WALLET_PATH})

    if network is None:
        network = Network(config)
        network.start(wait=True)
        network.start_interfaces()

    if wallet is None:
        storage = WalletStorage(config)
        wallet = Wallet(storage)
        if not storage.file_exists:
            wallet.seed = ''
            wallet.create_watching_only_wallet(MASTER_CHAIN,MASTER_PUBLIC_KEY)

        wallet.synchronize = lambda: None # prevent address creation by the wallet
        wallet.start_threads(network)

def _get_transaction( tx_hash, tx_height):
    global network

    raw_tx = network.synchronous_get([('blockchain.transaction.get', [tx_hash, tx_height])])[0]
    tx = Transaction(raw_tx)
    return tx


def get_history(addr):
    global network

    transactions = network.synchronous_get([('blockchain.address.get_history', [addr])])[0]
    transactions.sort(key=lambda x: x["height"])
    return [(i["tx_hash"], i["height"]) for i in transactions]


def _get_addr_balance(address):
    global network

    prevout_values = {}
    h = get_history(address)
    if h == ['*']:
        return 0, 0
    c = u = 0
    received_coins = []   # list of coins received at address
    transactions = {}

    # fetch transactions
    for tx_hash, tx_height in h:
        transactions[(tx_hash, tx_height)] = _get_transaction(tx_hash, tx_height)

    for tx_hash, tx_height in h:
        tx = transactions[(tx_hash, tx_height)]
        if not tx:
            continue
        _update_tx_outputs(tx, prevout_values)
        for i, (addr, value) in enumerate(tx.outputs):
            if addr == address:
                key = tx_hash + ':%d' % i
                received_coins.append(key)

    for tx_hash, tx_height in h:
        tx = transactions[(tx_hash, tx_height)]
        if not tx:
            continue
        v = 0

        for item in tx.inputs:
            addr = item.get('address')
            if addr == address:
                key = item['prevout_hash'] + ':%d' % item['prevout_n']
                value = prevout_values.get(key)
                if key in received_coins:
                    v -= value
        for i, (addr, value) in enumerate(tx.outputs):
            key = tx_hash + ':%d' % i
            if addr == address:
                v += value
        if tx_height:
            c += v
        else:
            u += v
    return c, u


def _update_tx_outputs(tx, prevout_values):
    for i, (addr, value) in enumerate(tx.outputs):
        key = tx.hash() + ':%d' % i
        prevout_values[key] = value

def _make_transaction(outputs, fee=None, from_addr=None, source_addr=None):
    global wallet

    total = 0
    final_outputs = []
    for to_address, amount in outputs:
        amount = int(100000000*amount)
        total = total + amount
        final_outputs.append((to_address, amount))

    if fee: fee = int(100000000*fee)
    return wallet.mktx(final_outputs, None, fee, from_addr, source_addr)


def getAddressBalance(address, exclude_unconfirmed=False):
    _init()
    global network

    c, u = _get_addr_balance(address)
    balance = satoshi2BTC(c)
    unconfirmed = satoshi2BTC(u)
    if not exclude_unconfirmed:
        balance = balance + unconfirmed

    return balance


def getFreshAddress():
    _init()
    global network, wallet

    account = wallet.accounts[0]
    address = account.get_address(0, int(random.random()*1000))

    return address


def sendTransaction(outputs, from_addr=None, fee=None, change_addr=None):
    _init()
    global network, wallet

    if fee is None:
        fee = float(defaults.BTC_DEFAULT_FEE)


    tx = _make_transaction(outputs, fee, from_addr, change_addr)
    r, h = wallet.sendtx(tx)
    return r, h