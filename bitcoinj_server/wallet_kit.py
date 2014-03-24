# -*- coding: utf-8 -*-
from decimal import Decimal
import sys
import os
import threading
import time

include_path = os.path.abspath(os.path.join(__file__, os.pardir))
sys.path.append(os.path.join(include_path, 'jar', 'bitcoinj-0.11-bundled.jar'))
sys.path.append(os.path.join(include_path, 'jar', 'slf4j-simple-1.7.6.jar'))


from com.google.bitcoin.core import (PeerAddress,
                                     NetworkParameters,
                                     ECKey,
                                     AbstractWalletEventListener,
                                     AbstractPeerEventListener,
                                     Utils,
                                     Address,
                                     Transaction,
                                     TransactionInput,
                                     Utils)
from com.google.bitcoin.kits import WalletAppKit
from com.google.bitcoin.params import MainNetParams, TestNet3Params
from java.io import File
from java.math import BigInteger
from java.net import InetAddress


WALLET_FRESH_ADDRESS_WORKAROUND_ACTIVE = True #shall we apply
WALLET_FRESH_ADDRESS_WORKAROUND_QTY = 100 #how many addresses to have for reuse

if '--testnet' in sys.argv:
    bitcoin_network_params = TestNet3Params.get()
else:
    bitcoin_network_params = MainNetParams.get()
TRUSTED_PEERS_LIST = [
                      # PeerAddress(InetAddress.getByName('127.0.0.1'),
                      #             bitcoin_network_params.getPort(),
                      #             bitcoin_network_params.PROTOCOL_VERSION),
                      # PeerAddress(InetAddress.getByName('46.105.173.28'),
                      #             bitcoin_network_params.getPort(),
                      #             bitcoin_network_params.PROTOCOL_VERSION),
                        ]
MAX_PEER_CONNECTIONS = 10
wallet = None

class XBTerminalWalletKit(WalletAppKit):
    def onSetupCompleted(self):
        global wallet, bitcoin_network_params, TRUSTED_PEERS_LIST, MAX_PEER_CONNECTIONS
        print 'wallet started'

        wallet = self.wallet()
        wallet.allowSpendingUnconfirmedTransactions()
        wallet.addEventListener(CoinsReceivedListener())

        keys_list = wallet.getKeys()
        if WALLET_FRESH_ADDRESS_WORKAROUND_ACTIVE and len(keys_list) < WALLET_FRESH_ADDRESS_WORKAROUND_QTY:
            for i in xrange(WALLET_FRESH_ADDRESS_WORKAROUND_QTY-len(keys_list)):
                wallet.addKey(ECKey())

        peer_group = self.peerGroup()
        peer_group.addEventListener(PeerConnectedListener())
        peer_group.setMaxConnections(MAX_PEER_CONNECTIONS)
        for peer_address in TRUSTED_PEERS_LIST:
            peer_group.addAddress(peer_address)

class PeerConnectedListener(AbstractPeerEventListener):
    def onPeerConnected(self, peer, peerCount):
        print '>>>onPeerConnected', peer

class CoinsReceivedListener(AbstractWalletEventListener):
    def onCoinsReceived(self, wallet, transaction, prevBalance, newBalance):
        print '>>>onPeerConnected', transaction, newBalance-prevBalance

class WalletKitThread(threading.Thread):
    def __init__(self, wallet_kit):
        self.terminate = False
        self.wallet_kit = wallet_kit
        super(WalletKitThread, self).__init__()

    def run(self):
        self.wallet_kit.startAndWait()
