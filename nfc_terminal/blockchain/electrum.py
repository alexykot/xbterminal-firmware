# -*- coding: utf-8 -*-
from decimal import Decimal
import json
from subprocess import Popen, PIPE

from nfc_terminal import defaults


def _callElectrum(params):
    params.insert(0, 'electrum')
    stdout, stderr = Popen(params, stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate()
    try:
        parsed_output = stdout
        # electrum often outputs unpredictable crap along with JSON, and we need to cut it out
        JSON_start_obj = parsed_output.find('{')
        JSON_start_list = parsed_output.find('[')
        if JSON_start_list == -1 or (JSON_start_obj != -1 and JSON_start_list != -1 and JSON_start_obj < JSON_start_list):
            JSON_end = parsed_output.rfind('}')+1
            parsed_output = parsed_output[JSON_start_obj:JSON_end]
        else:
            JSON_end = parsed_output.rfind(']')+1
            parsed_output = parsed_output[JSON_start_list:JSON_end]
        result = json.loads(parsed_output)
    except ValueError:
        print stdout

    return result

def getAddressBalance(address, exclude_unconfirmed=False):
    result = _callElectrum(["getaddressbalance", address])
    print result
    balance = Decimal(0).quantize(defaults.BTC_DEC_PLACES)
    if 'confirmed' in result:
        balance = balance + Decimal(result['confirmed']).quantize(defaults.BTC_DEC_PLACES)
    if 'unconfirmed' in result and not exclude_unconfirmed:
        balance = balance + Decimal(result['unconfirmed']).quantize(defaults.BTC_DEC_PLACES)
    return balance

def getFreshAddress():
    result = _callElectrum(["listaddresses", '-ab'])
    for address_entry in result:
        balance = Decimal(address_entry['balance'])
        if balance != 0:
            continue
        #additional balance check needed to check unconfirmed balances also
        balance = getAddressBalance(address_entry['address'])
        if balance == 0:
            return address_entry['address']
    return None


def getSendTransaction():
    pass
