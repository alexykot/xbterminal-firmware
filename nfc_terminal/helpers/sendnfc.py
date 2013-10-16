# -*- coding: utf-8 -*-
import nfc
import nfc.snep
import threading
import nfc_terminal


def send_ndef_message(llc):
    sp = nfc.ndef.UriRecord("http://google.com")
    snep = nfc.snep.SnepClient(llc)
    snep.put( nfc.ndef.Message(sp) )

def connected(llc):
    threading.Thread(target=nfc_terminal.helpers.sendnfc.send_ndef_message, args=(llc,)).start()
    return True

clf = nfc.ContactlessFrontend("usb")
clf.connect(llcp={'on-connect': connected})
