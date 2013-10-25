# -*- coding: utf-8 -*-
from electrum import Wallet, WalletStorage, SimpleConfig, Transaction, Network, bitcoin


from nfc_terminal import defaults
from nfc_terminal.helpers.misc import satoshi2BTC


WALLET_PATH = '/root/.electrum/electrum.dat'
WALLET_GAP_LIMIT = 1

# MASTER_PUBLIC_KEY = 'public_key'
# MASTER_CHAIN = 'chain'

network = None
wallet = None

def _init():
    global network, wallet

    config = SimpleConfig({'wallet_path':WALLET_PATH})

    if network is None:
        network = Network(config)
        if not network.start(wait=True):
            print "Not connected, aborting."
            exit()

        network.start_interfaces()

    if wallet is None:
        storage = WalletStorage(config)
        # if not storage.file_exists:
        #     createWalletFile(storage)
        wallet = Wallet(storage)
        wallet.start_threads(network)
        wallet.update()

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

def _make_transaction(outputs, fee=None, from_addr=None, change_addr=None):
    global wallet

    total = 0
    final_outputs = []
    for to_address, amount in outputs:
        amount = int(100000000*amount)
        total = total + amount
        final_outputs.append((to_address, amount))

    if fee: fee = int(100000000*fee)
    print from_addr
    return wallet.mktx(outputs=final_outputs, password=None, fee=fee, domain=from_addr, change_addr=change_addr)


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

    account = wallet.accounts["m/0'/0"]
    address = account.create_new_address(0)
    wallet.save_accounts()

    return address


def sendTransaction(outputs, from_addr=None, fee=None, change_addr=None):
    _init()
    global network, wallet

    transactions = get_history('17qJqwGw3BtoG2twm7W2PNsRHojPv98ED8')
    print transactions
    exit()


    if fee is None:
        fee = defaults.BTC_DEFAULT_FEE

    if from_addr is not None:
        from_addr = [from_addr]

    tx = _make_transaction(outputs, fee, from_addr, change_addr)
    result, hash = wallet.sendtx(tx)
    print result, hash
    if result:
        return hash
    else:
        return False

# def createWalletFile(storage):
#     global wallet
#
#     wallet = Wallet(storage)
#     wallet.init_seed(None)
#     wallet.save_seed()
#     wallet.create_accounts()
#     wallet.synchronize()
#     wallet.set_fee(defaults.BTC_DEFAULT_FEE*100000000)
#     wallet.change_gap_limit(WALLET_GAP_LIMIT)
