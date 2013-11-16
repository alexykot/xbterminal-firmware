# -*- coding: utf-8 -*-
import nfc
import nfc.snep
import threading


nfc_thread = None
run_event = None
def init_nfcpy(run_event, uri_to_send):
    clf = nfc.ContactlessFrontend('usb')
    connected = lambda llc: threading.Thread(target=llc.run).start()
    llc = clf.connect(run_event=run_event, llcp={'on-connect': connected})

    link_obj = nfc.ndef.UriRecord(uri_to_send)
    snep = nfc.snep.SnepClient(llc)
    snep.put(nfc.ndef.Message(link_obj))

    clf.close()

def start(bitcoin_uri):
    global nfc_thread, run_event

    if nfc_thread is not None and nfc_thread.isAlive():
        stop()

    run_event = threading.Event()
    run_event.set()
    nfc_thread = threading.Thread(target=init_nfcpy, args=(run_event, bitcoin_uri,))
    nfc_thread.start()

def stop():
    global nfc_thread, run_event

    if run_event is not None and run_event.isSet():
        run_event.clear()
        nfc_thread.join()

    nfc_thread = None
    run_event = None

