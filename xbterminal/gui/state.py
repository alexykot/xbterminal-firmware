from collections import deque
import time

from xbterminal.gui import settings


def get_initial_gui_state():
    return {
        'client': None,
        'gui_config': {},
        'remote_config': {},
        'remote_config_last_update': 0,
        'last_activity_timestamp': time.time(),
        'keypad': None,
        'keyboard_events': deque(maxlen=1),  # Only for keyboard driver
        'screen_buttons': {button_name: False for button_name
                           in settings.BUTTONS},
        'is_suspended': False,
        'CURRENT_STAGE': settings.STAGES['bootup'],
        'errors': set(),
        'timeout': False,
        'payment': {
            # Variables related to payment process
            'uid': None,
            'fiat_amount': None,
            'btc_amount': None,
            'exchange_rate': None,
            'payment_uri': None,
            'receipt_url': None,
            'qrcode': None,
        },
        'withdrawal': {
            # Variables related to withdrawal process
            'uid': None,
            'fiat_amount': None,
            'btc_amount': None,
            'tx_fee_btc_amount': None,
            'exchange_rate': None,
            'address': None,
            'receipt_url': None,
            'qrcode': None,
        },
    }

state = get_initial_gui_state()
