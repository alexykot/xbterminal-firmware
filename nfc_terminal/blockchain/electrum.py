# -*- coding: utf-8 -*-
from decimal import Decimal
import json
from subprocess import Popen, PIPE

from nfc_terminal import defaults



def _callElectrum(params):
    call_str = 'electrum %s' % params
    stdout, stderr = Popen(call_str, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True).communicate()

    try:
        parsed_output = stdout
        # electrum often outputs unpredictable crap along with JSON, and we need to cut it out
        JSON_start_obj = parsed_output.find('{')
        JSON_start_list = parsed_output.find('[')
        if (JSON_start_list == -1 and JSON_start_obj != -1) or (JSON_start_obj != -1 and JSON_start_list != -1 and JSON_start_obj < JSON_start_list):
            JSON_end = parsed_output.rfind('}')+1
            parsed_output = parsed_output[JSON_start_obj:JSON_end]
        elif JSON_start_list == -1 and JSON_start_obj == -1:
            JSON_start = parsed_output.find('"')
            JSON_end = parsed_output.rfind('"')+1
            parsed_output = parsed_output[JSON_start:JSON_end]
        else:
            JSON_end = parsed_output.rfind(']')+1
            parsed_output = parsed_output[JSON_start_list:JSON_end]
        result = json.loads(parsed_output)
    except ValueError as e:
        print stdout
        print ''
        print stderr
        raise e

    return result

def getAddressBalance(address, exclude_unconfirmed=False):
    call_str = "getaddressbalance %s" % address
    result = _callElectrum(call_str)
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


# recipients should be in format [('address', amount), ('address', amount)...]
def sendTransaction(recipients, source_address=None, change_address=None):
    recipients_str = ''
    for recipient_entry in recipients:
        address = recipient_entry[0]
        amount = recipient_entry[1]
        amount = Decimal(amount).quantize(defaults.BTC_DEC_PLACES)
        amount = str(amount)
        recipients_str = '%s %s %s' % (recipients_str, address, amount)
    recipients_str = recipients_str.strip()

    source_address_str = ''
    if source_address is not None:
        source_address_str = '--fromaddr=%s' % source_address

    change_address_str = ''
    if change_address is not None:
        change_address_str = '--changeaddr=%s' % change_address

    fee_str = '-f %s' % str(defaults.BTC_DEFAULT_FEE)
    tx_id = _callElectrum(['paytomany', fee_str, source_address_str, change_address_str, recipients_str])
    return tx_id
