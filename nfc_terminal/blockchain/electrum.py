from decimal import Decimal
from electrum import bitcoin, Transaction, Network

from nfc_terminal import defaults


network = None

def _init_electrum():
    global network

    network = Network()
    network.start(wait=True)

def _get_transaction(network, tx_hash, tx_height):
    raw_tx = network.synchronous_get([(
        'blockchain.transaction.get', [tx_hash, tx_height])])[0]
    tx = Transaction(raw_tx)
    return tx

def _get_history(network, addr):
    transactions = network.synchronous_get([(
        'blockchain.address._get_history', [addr])])[0]
    transactions.sort(key=lambda x: x["height"])
    return [(i["tx_hash"], i["height"]) for i in transactions]

def _update_tx_outputs(tx, prevout_values):
    for i, (addr, value) in enumerate(tx.outputs):
        key = tx.hash() + ':%d' % i
        prevout_values[key] = value

def _get_addr_balance(network, address):
    prevout_values = {}
    h = _get_history(network, address)
    if h == ['*']:
        return 0, 0
    c = u = 0
    received_coins = [] # list of coins received at address
    transactions = {}

    # fetch transactions
    for tx_hash, tx_height in h:
        transactions[(tx_hash, tx_height)] = _get_transaction(
            network, tx_hash, tx_height)

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

def getAddressBalance(address, exclude_unconfirmed=False):
    global network

    confirmed_satoshis, unconfirmed_satoshis = _get_addr_balance(network, address)
    confirmed_btc = Decimal(confirmed_satoshis).quantize(defaults.BTC_DEC_PLACES) / Decimal(100000000)
    unconfirmed_btc = Decimal(unconfirmed_satoshis).quantize(defaults.BTC_DEC_PLACES) / Decimal(100000000)

    result = confirmed_btc
    if not exclude_unconfirmed:
        result = result + unconfirmed_btc

    return result

