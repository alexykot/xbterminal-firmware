#!/opt/jython/jython -Dorg.slf4j.simpleLogger.defaultLogLevel=error
# -*- coding: utf-8 -*-
from decimal import Decimal
import json
import sys
import os
import BaseHTTPServer
import hashlib


include_path = os.path.abspath(os.path.join(__file__, os.pardir))
sys.path.insert(0, include_path)
sys.path.insert(0, '/usr/local/lib/python2.7/dist-packages')

import base58
import wallet_kit as wallet_kit_module
from java.io import File


if wallet_kit_module.USE_TESTNET:
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
    def do_TRACE(self):
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
            post_data = json.loads(self._getPostData())
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

        key = wallet_kit_module.ECKey()
        wallet_kit_module.wallet.addKey(key)

        return str(key.toAddress(wallet_kit_module.bitcoin_network_params))

    def _get_getAddressList(self):
        global wallet_kit_module

        keys_list = wallet_kit_module.wallet.getKeys()
        addresses_list = []
        for key in keys_list:
            addresses_list.append(str(key.toAddress(wallet_kit_module.bitcoin_network_params)))

        return addresses_list

    def _get_getUnspentTransactions(self):
        global wallet_kit_module

        wallet = wallet_kit_module.wallet
        all_transactions_list = wallet_kit_module.wallet.getTransactions(False)
        address_tx_list = []
        for transaction in all_transactions_list:
            if not transaction.isEveryOwnedOutputSpent(wallet):
                outputs = transaction.getOutputs()
                outputs_total = Decimal(0)
                for output in outputs:
                    if (output.isMine(wallet)
                        and output.isAvailableForSpending()):
                        outputs_total = outputs_total + Decimal(str(output.getValue()))

                address_tx_list.append({'txid': str(transaction.getHash()),
                                        'vout': '0', #fake for compartibibility with bitcoind
                                        'amount': str(outputs_total),
                                        })
        return address_tx_list

    def _post_sendRawTransaction(self, inputs, outputs):
        pass

wallet_kit = wallet_kit_module.XBTerminalWalletKit(wallet_kit_module.bitcoin_network_params, File(os.path.join(include_path, 'runtime')), '')
wallet_kit_thread = wallet_kit_module.WalletKitThread(wallet_kit)
wallet_kit_thread.start()

server_address = ('', SERVER_PORT)
bitcoinj_server = BaseHTTPServer.HTTPServer(server_address, BitcoinjRequestHandler)
print 'server started'
bitcoinj_server.serve_forever()



