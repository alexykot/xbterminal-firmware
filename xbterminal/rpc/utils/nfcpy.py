
"""
http://nfcpy.readthedocs.org/en/latest/
"""
import logging
import threading

import nfc
import nfc.snep
import nfc.llcp

logger = logging.getLogger(__name__)

READER_PATH = 'usb'


class BitcoinSender(threading.Thread):

    def __init__(self, uri):
        super(BitcoinSender, self).__init__()
        self.daemon = True
        self.terminate = False
        self.uri = uri

    def on_connect(self, llc):
        """
        A function that is be called when peer to peer communication was established.
        Receives the connected LogicalLinkController instance as parameter
        """
        comm_thread = threading.Thread(target=send_uri,
                                       args=(llc, self.uri))
        comm_thread.start()
        return True

    def terminate_callback_function(self):
        return self.terminate

    def run(self):
        while not self.terminate:
            clf = nfc.ContactlessFrontend(READER_PATH)
            clf.connect(llcp={'on-connect': self.on_connect},
                        terminate=lambda: self.terminate)
            clf.close()


def send_uri(llc, uri):
    snep = nfc.snep.SnepClient(llc)
    try:
        snep.put(nfc.ndef.Message(nfc.ndef.UriRecord(uri)))
    except (nfc.snep.SnepError,
            nfc.llcp.Error) as error:
        logger.exception(error)


class NFCServer(object):

    def __init__(self):
        self._nfc_thread = None
        try:
            nfc.ContactlessFrontend(READER_PATH)
        except IOError:
            self.is_available = False
        else:
            self.is_available = True

    def is_active(self):
        return self._nfc_thread is not None and self._nfc_thread.is_alive()

    def start(self, uri):
        if not self.is_available:
            # Do nothing if device is not available
            return

        self._nfc_thread = BitcoinSender(uri)
        self._nfc_thread.start()
        logger.info('NFC activated')

    def stop(self):
        if not self.is_available:
            # Do nothing if device is not available
            return

        if self.is_active():
            self._nfc_thread.terminate = True
            self._nfc_thread.join()
        self._nfc_thread = None
        logger.info('NFC deactivated')
