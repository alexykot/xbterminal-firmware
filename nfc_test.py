#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
import time
import sys
import os
import requests

include_path = os.path.abspath(os.path.join(__file__, os.pardir))
sys.path.insert(0, include_path)

import xbterminal
import xbterminal.defaults

xbterminal.defaults.PROJECT_ABS_PATH = include_path

# nfc_include_path = os.path.abspath(os.path.join(include_path, 'nfcpy'))
# sys.path.insert(0, nfc_include_path)
#

import nfc
import nfc.snep
import threading



# this works.
nfc_thread = None
def init_nfc(run_event, bitcoin_uri):
    clf = nfc.ContactlessFrontend('usb')
    connected = lambda llc: threading.Thread(target=llc.run).start()
    llc = clf.connect(llcp={'on-connect': connected}, run_event=run_event)

    link = nfc.ndef.UriRecord(bitcoin_uri)
    snep = nfc.snep.SnepClient(llc)
    snep.put(nfc.ndef.Message(link))

    clf.close()
    if not run_event.is_set():
        return

try:
    while True:
        if nfc_thread is None or not nfc_thread.isAlive():
            run_event = threading.Event()
            run_event.set()
            nfc_thread = threading.Thread(target=init_nfc, args=(run_event,'bitcoin:1G2bcoCKj8s9GYheqQgU5CHSLCtGjyP9Vz?amount=0.12&label=test%20merchant&message=test%20payment'))
            nfc_thread.start()

        print '!'
        time.sleep(1)
except KeyboardInterrupt:
    run_event.clear()
    nfc_thread.join()



