#!/opt/jython/jython -Dorg.slf4j.simpleLogger.defaultLogLevel=error
# -*- coding: utf-8 -*-
from decimal import Decimal
import sys
import os
import threading
import time

include_path = os.path.abspath(os.path.join(__file__, os.pardir))
sys.path.insert(0, include_path)

# sys.path.append('/usr/share/java/slf4j-api.jar')
# sys.path.append('/usr/share/java/guava-16.0.1.jar')
# sys.path.append('/usr/share/java/protobuf.jar')
# sys.path.append('/usr/share/java/netty-3.2.5.Final.jar')
# sys.path.append('/root/spongycastle-core-1.50.0.0.jar')
# sys.path.append('/root/spongycastle-prov-1.50.0.0.jar')
# sys.path.append('/root/spongycastle-pkix-1.50.0.0.jar')
# sys.path.append('/root/spongycastle-pg-1.50.0.0.jar')


phone_testnet_address = "mx3hsWPoqi8TQfo1rJHTSbZqQPUz2WLsff" # phone test address
bitcoinj_testnet_address = "mqVYRPoMR6e3i61mVnHYMdNWHZqt7DbiT6" # bitcoinj test wallet address

time.sleep(5)

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
                                     TransactionInput)
from com.google.bitcoin.kits import WalletAppKit
from java.io import File
from java.math import BigInteger
from java.net import InetAddress


class TestWalletKit(WalletAppKit):
    def onSetupCompleted(self):
        global wallet, params

        wallet = self.wallet()
        wallet.allowSpendingUnconfirmedTransactions()
        wallet.addEventListener(CoinsReceivedListener())

        peer_group = self.peerGroup()
        peer_group.addEventListener(PeerConnectedListener())
        peer_group.setMaxConnections(25)

class PeerConnectedListener(AbstractPeerEventListener):
    def onPeerConnected(self, peer, peerCount):
        print '>>>onPeerConnected', peer


class CoinsReceivedListener(AbstractWalletEventListener):
    def onCoinsReceived(self, wallet, transaction, prevBalance, newBalance):
        print '>>>onCoinsReceived'

class WalletKitThread(threading.Thread):
    def __init__(self, wallet_kit):
        self.terminate = False
        self.wallet_kit = wallet_kit
        super(WalletKitThread, self).__init__()

    def run(self):
        self.wallet_kit.startAndWait()

wallet = None
params = NetworkParameters.testNet3()
test_wallet_kit = TestWalletKit(params, File('/root/XBTerminal/bitcoinj_server/runtime'), '')

test_kit_thread = WalletKitThread(test_wallet_kit)
test_kit_thread.start()


while True:
    try:
        transactions_list = wallet.getTransactions(False)
        total_balance = Decimal(0)
        for transaction in transactions_list:
            if not transaction.isEveryOwnedOutputSpent(wallet):
                outputs = transaction.getOutputs()
                for output in outputs:
                    if output.isMine(wallet) and output.isAvailableForSpending():
                        output_value = Decimal(str(output.getValue()))
                        print transaction.getHashAsString(), output_value
                        total_balance = total_balance + output_value



            # transaction_value = Decimal(str(transaction.getValue(wallet)))
            # print transaction.getHashAsString(), transaction_value,
            # total_balance = total_balance + transaction_value

        print 'wallet balance: ', total_balance

        if total_balance > 0:
            output_amount = total_balance-Decimal(10000)
            output_amount = BigInteger(str(output_amount))
            target_address = Address(params, phone_testnet_address)
            forwarding_transaction = Transaction(params)
            forwarding_transaction.addOutput(output_amount, target_address)
            request = wallet.SendRequest.forTx(forwarding_transaction)
            wallet.sendCoins(request)

            print '>>>transaction send attempt'


    except AttributeError:
        print 'wallet not initialized yet'

    time.sleep(10)

    # 199440000
    # 199540000