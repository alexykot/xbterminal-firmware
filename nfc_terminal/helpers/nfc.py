import nfc
import nfc.snep
import threading

def send_ndef_message(llc):
    sp = nfc.ndef.UriRecord('https://bitcoinaverage.com/')
    snep = nfc.snep.SnepClient(llc)
    snep.put( nfc.ndef.Message(sp) )

def connected(llc):
    threading.Thread(target=send_ndef_message, args=(llc,)).start()
    return True

clf = nfc.ContactlessFrontend("usb")
clf.connect(llcp={'on-connect': connected})