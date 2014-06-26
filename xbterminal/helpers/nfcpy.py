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

nfc_thread = None


class BitcoinSender(threading.Thread):

    def __init__(self, bitcoin_uri):
        super(BitcoinSender, self).__init__()
        self.reader_path = 'usb'
        self.terminate = False
        self.uri = bitcoin_uri

    def on_connect(self, llc):
        """
        A function that is be called when peer to peer communication was established.
        Receives the connected LogicalLinkController instance as parameter
        """
        comm_thread = threading.Thread(target=send_uri,
                                       args=(llc, self.uri))
        comm_thread.start()

    def terminate_callback_function(self):
        return self.terminate

    def run(self):
        try:
            clf = nfc.ContactlessFrontend(self.reader_path)
        except IOError:
            reset_usb_hub()
            clf = nfc.ContactlessFrontend(self.reader_path)
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


def start(bitcoin_uri):
    global nfc_thread

    if nfc_thread is not None and nfc_thread.is_alive():
        stop()

    time.sleep(0.3) #required to free up device before reusing

    nfc_thread = BitcoinSender(bitcoin_uri)
    nfc_thread.start()
    logger.debug('NFC activated')

def is_active():
    global nfc_thread

    return nfc_thread is not None and nfc_thread.is_alive()

def stop():
    global nfc_thread

    if nfc_thread is not None and nfc_thread.is_alive():
        nfc_thread.terminate = True
        nfc_thread.join()

    nfc_thread = None
