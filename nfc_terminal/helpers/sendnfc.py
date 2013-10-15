import nfc
import nfc.snep
import threading


class NFCClient():

    def send_ndef_message(self, llc):
        sp = nfc.ndef.UriRecord("http://google.com")
        snep = nfc.snep.SnepClient(llc)
        snep.put( nfc.ndef.Message(sp) )

    def connected(self, llc):
        threading.Thread(target=self.send_ndef_message, args=(llc,)).start()
        return True

    clf = nfc.ContactlessFrontend("usb")
    clf.connect(llcp={'on-connect': connected})