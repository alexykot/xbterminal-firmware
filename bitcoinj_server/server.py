#!/opt/jython/jython -Dorg.slf4j.simpleLogger.defaultLogLevel=error
# -*- coding: utf-8 -*-
from decimal import Decimal
import json
import sys
import os
import BaseHTTPServer
import hashlib

import wallet_kit as wallet_kit_module
from java.io import File


include_path = os.path.abspath(os.path.join(__file__, os.pardir))

print 'script started'
if '--testnet' in sys.argv:
    SERVER_PORT = 18333
else:
    SERVER_PORT = 8333

class BitcoinjServerException(Exception):
    pass

class NoContentLengthException(BitcoinjServerException):
    http_code = 411

class PostEmptyException(BitcoinjServerException):
    http_code = 400

class NotFoundException(BitcoinjServerException):
    http_code = 404

class BitcoinjRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(501, self.responses[501])
    def do_PUT(self):
        self.send_response(501, self.responses[501])
    def do_DELETE(self):
        self.send_response(501, self.responses[501])
    def do_OPTIONS(self):
        self.send_response(501, self.responses[501])
    def do_bitcoinaverageTRACE(self):
        self.send_response(501, self.responses[501])
    def do_CONNECT(self):
        self.send_response(501, self.responses[501])

    def _send_response(self, code, data):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Content-length', len(data))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        try:
            local_call_name, params = self._parsePath()
        except BitcoinjServerException as error:
            self._send_response(error.http_code, json.dumps(self.responses[error.http_code]))

        response_body = ''
        local_call_full_name = '_get_{call}'.format(call=local_call_name)
        if hasattr(self, local_call_full_name):
            response_body = getattr(self, local_call_full_name)(**params)
        else:
            self._send_response(404, json.dumps(self.responses[404]))
            return


        self._send_response(200, json.dumps(response_body))

    def do_POST(self):
        try:
            local_call_name, params = self._parsePath()
            raw_post_contents = self._getPostData()
            post_data = json.loads(raw_post_contents)
            params = dict(params.items() + post_data.items())
        except BitcoinjServerException as error:
            self._send_response(error.http_code, json.dumps(self.responses[error.http_code]))

        response_body = ''
        if hasattr(self, '_post_{call}'.format(call=local_call_name)):
            response_body = getattr(self, '_post_{call}'.format(call=local_call_name))(**params)
        else:
            self._send_response(404, json.dumps(self.responses[404]))
            return

        self._send_response(200, json.dumps(response_body))

    def _getPostData(self):
        try:
            post_length = int(self.headers['Content-Length'])
        except KeyError:
            raise NoContentLengthException()
        post_data = self.rfile.read(post_length)

        if post_length == 0 or len(post_data) == 0:
            raise PostEmptyException()

        return post_data

    def _parsePath(self):
        result = self.path.split('?')
        params = {}
        try:
            local_call_name, params_temp_list = result
            params = {}
            params_temp_list = params_temp_list.split('&')
            for param in params_temp_list:
                param_item = param.split('=')
                try:
                    params[param_item[0]] = param_item[1]
                except IndexError:
                    params[param_item[0]] = ''
        except ValueError:
            if len(result) == 1:
                local_call_name = result[0]
            else:
                raise NotFoundException()
        local_call_name = local_call_name.strip('/\\')

        return local_call_name, params


    def _get_getAddressBalance(self, address):
        global wallet_kit_module

        wallet = wallet_kit_module.wallet
        transactions_list = wallet_kit_module.wallet.getTransactions(False)
        total_balance = Decimal(0)
        for transaction in transactions_list:
            if not transaction.isEveryOwnedOutputSpent(wallet):
                outputs = transaction.getOutputs()
                for output in outputs:
                    if (output.isMine(wallet)
                        and output.isAvailableForSpending()
                        and output.getScriptPubKey().isSentToAddress()
                        and output.getScriptPubKey().getToAddress(wallet_kit_module.bitcoin_network_params).toString() == address):
                        total_balance = total_balance + Decimal(str(output.getValue()))

        return str(total_balance)

    def _get_getFreshAddress(self):
        global wallet_kit_module

        address_str = None
        if wallet_kit_module.WALLET_FRESH_ADDRESS_WORKAROUND_ACTIVE:
            keys_list = wallet_kit_module.wallet.getKeys()
            for key in keys_list:
                address_str = str(key.toAddress(wallet_kit_module.bitcoin_network_params))
                if int(self._get_getAddressBalance(address_str)) == 0:
                    break
        else:
            key = wallet_kit_module.ECKey()
            wallet_kit_module.wallet.addKey(key)
            address_str = str(key.toAddress(wallet_kit_module.bitcoin_network_params))

        return address_str

    def _get_getAddressList(self):
        global wallet_kit_module

        keys_list = wallet_kit_module.wallet.getKeys()
        addresses_list = []
        for key in keys_list:
            addresses_list.append(str(key.toAddress(wallet_kit_module.bitcoin_network_params)))

        return addresses_list

    def _get_getUnspentTransactions(self):
        global wallet_kit_module

        all_transactions_list = wallet_kit_module.wallet.getTransactions(False)
        address_tx_list = []

        for transaction in all_transactions_list:
            addresses_list = []
            if not transaction.isEveryOwnedOutputSpent(wallet_kit_module.wallet):
                outputs = transaction.getOutputs()
                outputs_total = Decimal(0)
                for output in outputs:
                    if output.isMine(wallet_kit_module.wallet) and output.isAvailableForSpending():
                        addresses_list.append(output.getScriptPubKey().getToAddress(wallet_kit_module.bitcoin_network_params).toString())
                        outputs_total = outputs_total + Decimal(str(output.getValue()))

                address_tx_list.append({'txid': str(transaction.getHash()),
                                        'amount': str(outputs_total),
                                        'addresses': addresses_list,
                                        })
        return address_tx_list


    def _get_getInfo(self):
        global wallet_kit_module

        data = {"version" : None,
                "protocolversion" : None,
                "walletversion" : None,
                "balance" : None,
                "blocks" : None,
                "timeoffset" : None,
                "connections" : str(wallet_kit.peerGroup().numConnectedPeers()),
                "difficulty" : None,
                "testnet" : False,
                "keypoololdest" : None,
                "keypoolsize" : None,
                "errors" : ""
        }
        if '--testnet' in sys.argv:
            data['testnet'] = True
        try:
            data['walletversion'] = str(wallet_kit_module.wallet.getVersion())
            data['balance'] = str(wallet_kit_module.wallet.getBalance())
        except AttributeError:
            pass

        return data

    def _post_sendRawTransaction(self, inputs, outputs):
        global wallet_kit_module

        outgoing_transaction = wallet_kit_module.Transaction(wallet_kit_module.bitcoin_network_params)
        for output_address in outputs:
            output_amount = wallet_kit_module.BigInteger(str(outputs[output_address]))
            output_address = wallet_kit_module.Address(wallet_kit_module.bitcoin_network_params, output_address)
            outgoing_transaction.addOutput(output_amount, output_address)

        all_transactions_list = wallet_kit_module.wallet.getTransactions(False)
        for transaction in all_transactions_list:
            if not transaction.isEveryOwnedOutputSpent(wallet_kit_module.wallet):
                transaction_hash = transaction.getHash()
                for input_item in inputs:
                    if transaction_hash == input_item['txid']:
                        outputs = transaction.getOutputs()
                        for output in outputs:
                            if (output.isMine(wallet_kit_module.wallet)
                                and output.isAvailableForSpending()):
                                outgoing_transaction.addInput(output)

        request = wallet_kit_module.wallet.SendRequest.forTx(outgoing_transaction)
        wallet_kit_module.wallet.sendCoins(request)

        return str(outgoing_transaction.getHash())

if '--testnet' in sys.argv:
    wallet_file_path =  os.path.join(include_path, 'runtime', 'testnet3')
else:
    wallet_file_path =  os.path.join(include_path, 'runtime')

wallet_kit = wallet_kit_module.XBTerminalWalletKit(wallet_kit_module.bitcoin_network_params, File(wallet_file_path), '')
#wallet_kit.connectToLocalHost()
wallet_kit_thread = wallet_kit_module.WalletKitThread(wallet_kit)
wallet_kit_thread.start()

server_address = ('127.0.0.1', SERVER_PORT)
bitcoinj_server = BaseHTTPServer.HTTPServer(server_address, BitcoinjRequestHandler)
print 'server started'
bitcoinj_server.serve_forever()






