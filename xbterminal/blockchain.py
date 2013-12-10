# -*- coding: utf-8 -*-
from decimal import Decimal
import os
import socket
import subprocess
import bitcoinrpc
import bitcoinrpc.connection
import time

import xbterminal
from xbterminal import defaults
from xbterminal.exceptions import NotEnoughFunds, PrivateKeysMissing
from xbterminal.helpers.log import log

connection = None

class BitcoinConnection(bitcoinrpc.connection.BitcoinConnection):
    def sendrawtransaction(self, hex_raw_tx):
        self.proxy.sendrawtransaction(hex_raw_tx)

def init():
    global connection

    if connection is None:
        connection_test = BitcoinConnection(user=defaults.BITCOIND_USER,
                                               password=defaults.BITCOIND_PASS,
                                               host=defaults.BITCOIND_HOST,
                                               port=defaults.BITCOIND_PORT,
                                               use_https=False)
        try:
            connection_test.getinfo()
        except socket.error:
             _start_bitcoind(connection_test)

def _start_bitcoind(connection_test):
    global xbterminal

    if 'last_started' not in xbterminal.local_state or xbterminal.local_state['last_started'] + defaults.BITCOIND_MAX_BLOCKCHAIN_AGE < time.time():
        _presync_blockchain()

    log('bitcoind starting', xbterminal.defaults.LOG_MESSAGE_TYPES['DEBUG'])
    subprocess.Popen("bitcoind")
    while True:
        try:
            test = connection_test.getinfo()
            break
        except socket.error:
            time.sleep(1)
    log('bitcoind started', xbterminal.defaults.LOG_MESSAGE_TYPES['DEBUG'])


def _presync_blockchain():
    blocks_sync_successful = False
    chainstate_sync_successful = False
    for blockchain_server in defaults.BITCOIND_BLOCKCHAIN_SERVERS:
        key_file_path = os.path.join(defaults.BITCOIND_BLOCKCHAIN_SERVERS_KEYS_PATH,
                                     '{name}_{user}_rsa'.format(name=blockchain_server['name'],
                                                                user=blockchain_server['user']))

        if not os.path.exists(key_file_path):
            log('{key_file} - key missing'.format(key_file=key_file_path), xbterminal.defaults.LOG_MESSAGE_TYPES['ERROR'])
            continue

        if not blocks_sync_successful:
            log('blocks rsync started from {blockchain_server_name}'.format(blockchain_server_name=blockchain_server['name']),
                xbterminal.defaults.LOG_MESSAGE_TYPES['DEBUG'])
            command_blocks = []
            command_blocks.append("rsync")
            command_blocks.append('-e "ssh -p {port} -i {key_file_path}"'.format(port=blockchain_server['port'],
                                                                                 key_file_path=key_file_path))
            command_blocks.append("-aqz --delete")
            command_blocks.append("{user}@{addr}:{path}/blocks/".format(user=blockchain_server['user'],
                                                                         addr=blockchain_server['addr'],
                                                                         path=blockchain_server['path']))
            command_blocks.append("/root/.bitcoin/blocks")
            command_blocks = ' '.join(command_blocks)
            try:
                output = subprocess.check_output(command_blocks, shell=True)
            except subprocess.CalledProcessError:
                output = 'fail'

            if output == '':
                blocks_sync_successful = True
            else:
                log('blocks rsync failed, output: {rsync_output}'.format(rsync_output=output),
                    xbterminal.defaults.LOG_MESSAGE_TYPES['ERROR'])

        if not chainstate_sync_successful:
            log('chainstate rsync started from {blockchain_server_name}'.format(blockchain_server_name=blockchain_server['name']),
                xbterminal.defaults.LOG_MESSAGE_TYPES['DEBUG'])
            command_chainstate = []
            command_chainstate.append("rsync")
            command_chainstate.append('-e "ssh -p {port} -i {key_file_path}"'.format(port=blockchain_server['port'],
                                                                                  key_file_path=key_file_path))
            command_chainstate.append("-aqz --delete")
            command_chainstate.append("{user}@{addr}:{path}/chainstate/".format(user=blockchain_server['user'],
                                                                               addr=blockchain_server['addr'],
                                                                               path=blockchain_server['path']))
            command_chainstate.append("/root/.bitcoin/chainstate")
            command_chainstate = ' '.join(command_chainstate)
            try:
                output = subprocess.check_output(command_chainstate, shell=True)
            except subprocess.CalledProcessError:
                output = 'fail'

            if output == '':
                blocks_sync_successful = True
            else:
                log('chainstate rsync failed, output: {rsync_output}'.format(rsync_output=output),
                    xbterminal.defaults.LOG_MESSAGE_TYPES['ERROR'])
        if blocks_sync_successful and chainstate_sync_successful:
            break


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

    tx_hash = connection.sendmany(fromaccount='',
                                  todict=todict,
                                  minconf=0)

    return tx_hash


# Sends transaction from given address using all currently unspent inputs for that address.
# by default all change is sent to fees address
def sendRawTransaction(outputs, from_addr, change_addr=None):
    global connection

    transaction_hash = None

    if change_addr is None:
        change_addr = xbterminal.remote_config['OUR_FEE_BITCOIN_ADDRESS']

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
        change_amount = outputs[change_addr] + (total_available_to_spend - total_to_pay - defaults.BTC_DEFAULT_FEE)
        if change_amount > 0:
            outputs[change_addr] = change_amount
        float_outputs[change_addr] = float(outputs[change_addr])

    nonempty_float_outputs = {}

    for address in float_outputs:
        if float_outputs[address] > 0:
            nonempty_float_outputs[address] = float_outputs[address]

    raw_transaction_unsigned_hex = connection.createrawtransaction(inputs=inputs, outputs=nonempty_float_outputs)
    raw_transaction_signed = connection.signrawtransaction(raw_transaction_unsigned_hex)
    if raw_transaction_signed['complete']:
        raw_transaction_signed_hex = raw_transaction_signed['hex']
    else:
        raise PrivateKeysMissing()

    transaction_hash = connection.proxy.sendrawtransaction(raw_transaction_signed_hex)

    return transaction_hash

