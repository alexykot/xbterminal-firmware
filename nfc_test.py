#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import sys
import os
import requests

include_path = os.path.abspath(os.path.join(__file__, os.pardir))
sys.path.insert(0, include_path)

import xbterminal
import xbterminal.defaults

xbterminal.defaults.PROJECT_ABS_PATH = include_path

nfc_include_path = os.path.abspath(os.path.join(include_path, 'nfcpy'))
sys.path.insert(0, nfc_include_path)

# import nfc, nfc.snep, threading
# clf = nfc.ContactlessFrontend('usb')
#
# def connected(llc):
#     threading.Thread(target=llc.run()).start()
#
# llc = clf.connect(llcp={'on-connect': connected})
#
# snep = nfc.snep.SnepClient(llc)
# snep.put(nfc.ndef.Message(nfc.ndef.SmartPosterRecord("http://nfcpy.org")))
#
# clf.close()
#

print bytearray.fromhex('01676F6F676C652E636F6D2F').decode()
print bytearray.fromhex('2531473262636F434B6A3873394759686571516755354348534C4374476A795039567A').decode()
print bytearray.fromhex('25626974636F696E3A31473262636F434B6A3873394759686571516755354348534C4374476A795039567A').decode()
print bytearray.fromhex('626974636F696E3A31473262636F434B6A3873394759686571516755354348534C4374476A795039567A').decode()


# byte[] uriField = "example.com".getBytes(Charset.forName("US-ASCII"));
# byte[] payload = new byte[uriField.length + 1];              //add 1 for the URI Prefix
# byte payload[0] = 0x01;                                      //prefixes http://www. to the URI
# System.arraycopy(uriField, 0, payload, 1, uriField.length);  //appends URI to payload
# NdefRecord rtdUriRecord = new NdefRecord(
# NdefRecord.TNF_WELL_KNOWN, NdefRecord.RTD_URI, new byte[0], payload);