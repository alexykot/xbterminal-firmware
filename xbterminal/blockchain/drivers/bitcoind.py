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

BITCOIND_DATADIR = '/root/.bitcoin'
BITCOIND_CONFIG_PATH = os.path.join('configs', 'bitcoin.conf')
BITCOIND_TESTNET = True
BITCOIND_TESTNET_TESTDIR = 'testnet3'
BITCOIND_HOST = '127.0.0.1'
if BITCOIND_TESTNET:
    BITCOIND_PORT = 18332
else:
    BITCOIND_PORT = 8332
BITCOIND_USER = 'root'
BITCOIND_PASS = 'password'


BITCOIND_BLOCKCHAIN_SERVERS_KEYS_PATH = '/root/.ssh'
BITCOIND_BLOCKCHAIN_SERVERS = ({'name': 'chainserver0',
                                'addr': '80.243.176.66',
                                'port': '22',
                                'user': 'bitnumus',
                                'path': '~/chain',
                                'testnet': True,
                                }, )
BITCOIND_MAX_BLOCKCHAIN_AGE = 3600 #if blockchain is more than X seconds old - we do rsync to trusted blockchain servers to download blocks and index and catch up quickly

connection = None

class BitcoinConnection(bitcoinrpc.connection.BitcoinConnection):
    def sendrawtransaction(self, hex_raw_tx):
        self.proxy.sendrawtransaction(hex_raw_tx)

def init():
    global connection

    if connection is None:
        connection_probe = BitcoinConnection(user=BITCOIND_USER,
                                             password=BITCOIND_PASS,
                                             host=BITCOIND_HOST,
                                             port=BITCOIND_PORT,
                                             use_https=False)
        try:
            connection_probe.getinfo()
            connection = connection_probe
        except socket.error:
            connection = _start_bitcoind(connection_probe)

    logger.debug('bitcoind init done')


def _start_bitcoind(connection_probe):
    global xbterminal

    if ('last_started' not in xbterminal.local_state
       or xbterminal.local_state['last_started'] + BITCOIND_MAX_BLOCKCHAIN_AGE < time.time()):
        _presync_blockchain()

    logger.debug('bitcoind starting')
    bitcoind_config_path = os.path.join(defaults.PROJECT_ABS_PATH, BITCOIND_CONFIG_PATH)
    subprocess.Popen(['bitcoind',
                      '-conf={conf_file_path}'.format(conf_file_path=bitcoind_config_path),
                      '-datadir={data_dir}'.format(data_dir=BITCOIND_DATADIR),
                        ])
    while True:
        try:
            connection_probe.getinfo()
            break
        except socket.error:
            time.sleep(1)
    logger.debug('bitcoind started')

    return connection_probe


def _presync_blockchain():
    blocks_sync_successful = False
    chainstate_sync_successful = False
    logger.debug('bitcoind blockchain presync starting')
    for blockchain_server in BITCOIND_BLOCKCHAIN_SERVERS:
        if BITCOIND_TESTNET != blockchain_server['testnet']:
            continue

        key_file_path = os.path.join(BITCOIND_BLOCKCHAIN_SERVERS_KEYS_PATH,
                                     '{name}_{user}_rsa'.format(name=blockchain_server['name'],
                                                                user=blockchain_server['user']))

        if not os.path.exists(key_file_path):
            logger.error('{key_file} - key missing'.format(key_file=key_file_path))
            continue

        if not blocks_sync_successful:
            command_blocks = []
            command_blocks.append("rsync")
            command_blocks.append('-e "ssh -p {port} -i {key_file_path}"'.format(port=blockchain_server['port'],
                                                                                 key_file_path=key_file_path))
            command_blocks.append("-aqz --delete")
            command_blocks.append("{user}@{addr}:{path}/blocks/".format(user=blockchain_server['user'],
                                                                         addr=blockchain_server['addr'],
                                                                         path=blockchain_server['path']))
            if BITCOIND_TESTNET:
                command_blocks.append("{data_dir}/{testnet_dir}/blocks".format(data_dir=BITCOIND_DATADIR,
                                                                                   testnet_dir=BITCOIND_TESTNET_TESTDIR,
                                                                                        ))
            else:
                command_blocks.append("{data_dir}/blocks".format(data_dir=BITCOIND_DATADIR))
            command_blocks = ' '.join(command_blocks)
            logger.debug('blocks rsync started from {blockchain_server_name}'.format(blockchain_server_name=blockchain_server['name']))
            logger.debug('command: {command_blocks}'.format(command_blocks=command_blocks))
            try:
                output = subprocess.check_output(command_blocks, shell=True)
            except subprocess.CalledProcessError:
                output = 'fail while retrieving fail'

            if output == '':
                blocks_sync_successful = True
            else:
                logger.error('blocks rsync failed, output: {rsync_output}'.format(rsync_output=output))

        if not chainstate_sync_successful:
            command_chainstate = []
            command_chainstate.append("rsync")
            command_chainstate.append('-e "ssh -p {port} -i {key_file_path}"'.format(port=blockchain_server['port'],
                                                                                  key_file_path=key_file_path))
            command_chainstate.append("-aqz --delete")
            command_chainstate.append("{user}@{addr}:{path}/chainstate/".format(user=blockchain_server['user'],
                                                                               addr=blockchain_server['addr'],
                                                                               path=blockchain_server['path']))
            if BITCOIND_TESTNET:
                command_chainstate.append("{data_dir}/{testnet_dir}/chainstate".format(data_dir=BITCOIND_DATADIR,
                                                                                       testnet_dir=BITCOIND_TESTNET_TESTDIR,
                                                                                        ))
            else:
                command_chainstate.append("{data_dir}/chainstate".format(data_dir=BITCOIND_DATADIR))
            command_chainstate = ' '.join(command_chainstate)
            logger.debug('chainstate rsync started from {blockchain_server_name}'.format(blockchain_server_name=blockchain_server['name']))
            logger.debug('command: {command_chainstate}'.format(command_chainstate=command_chainstate))
            try:
                output = subprocess.check_output(command_chainstate, shell=True)
            except subprocess.CalledProcessError:
                output = 'fail while retrieving fail'

            if output == '':
                blocks_sync_successful = True
            else:
                logger.error('chainstate rsync failed, output: {rsync_output}'.format(rsync_output=output))

        if blocks_sync_successful and chainstate_sync_successful:
            logger.debug('bitcoind blockchain presync successful')
            return

    logger.debug('bitcoind blockchain presync failed')


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


def sendRawTransaction(inputs, outputs):
    global connection

    raw_transaction_unsigned_hex = connection.createrawtransaction(inputs=inputs, outputs=outputs)
    raw_transaction_signed = connection.signrawtransaction(raw_transaction_unsigned_hex)
    if raw_transaction_signed['complete']:
        raw_transaction_signed_hex = raw_transaction_signed['hex']
    else:
        raise PrivateKeysMissing()

    return connection.proxy.sendrawtransaction(raw_transaction_signed_hex)


