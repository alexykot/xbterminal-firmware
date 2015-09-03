
"""
http://nfcpy.readthedocs.org/en/latest/
"""
import logging
import subprocess
import threading
import time

import nfc
import nfc.snep
import nfc.llcp

logger = logging.getLogger(__name__)

READER_PATH = 'usb'


class BitcoinSender(threading.Thread):

    def __init__(self, uri):
        super(BitcoinSender, self).__init__()
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
        clf = nfc.ContactlessFrontend(READER_PATH)
        clf.connect(llcp={'on-connect': self.on_connect},
                    terminate=self.terminate_callback_function)
        clf.close()


def send_uri(llc, uri):
    snep = nfc.snep.SnepClient(llc)
    try:
        snep.put(nfc.ndef.Message(nfc.ndef.UriRecord(uri)))
    except (nfc.snep.SnepError,
            nfc.llcp.Error) as error:
        logger.exception(error)


def reset_usb_hub():
    logger.warning("USB HUB: RESETTING...")
    bind_cmd = "echo usb1 > /sys/bus/usb/drivers/usb/bind"
    unbind_cmd = "echo usb1 > /sys/bus/usb/drivers/usb/unbind"
    # Unbind #1
    subprocess.check_call(unbind_cmd, shell=True)
    time.sleep(2)
    # Bind #1 -> power-off
    subprocess.check_call(bind_cmd, shell=True)
    logger.warning("USB HUB: POWER OFF")
    time.sleep(5)
    # Unbind #2 -> power on
    subprocess.check_call(unbind_cmd, shell=True)
    logger.warning("USB HUB: POWER ON")
    time.sleep(10)
    # Bind #2
    subprocess.check_call(bind_cmd, shell=True)
    time.sleep(10)


class NFCServer(object):

    def __init__(self):
        self._nfc_thread = None
        try:
            clf = nfc.ContactlessFrontend(READER_PATH)
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

        if self.is_active():
            self.stop()

        time.sleep(0.3)  # required to free up device before reusing

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
