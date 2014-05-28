import logging
import unicodedata

logger = logging.getLogger(__name__)

import xbterminal
from xbterminal import defaults

import xbterminal.blockchain.blockchain
import xbterminal.helpers.configs
import xbterminal.helpers.wireless

# Globals
run = None
ui = None


def init():
    """
    Initialize global variables in this module
    """
    run = xbterminal.runtime
    ui = run['main_window'].ui
    return "bootup"


def bootup():
    return "bootup"


def idle():
    return None
