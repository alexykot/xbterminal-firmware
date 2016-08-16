from collections import deque

from xbterminal.gui import settings


def get_initial_gui_state():
    return {
        'client': None,
        'gui_config': {},
        'remote_config': {},
        'remote_config_last_update': 0,
        'last_activity_timestamp': None,
        'keypad': None,
        'keyboard_events': deque(maxlen=1),  # Only for keyboard driver
        'screen_buttons': {button_name: False for button_name
                           in settings.BUTTONS},
        'CURRENT_STAGE': settings.STAGES['bootup'],
        'payment': {
            # Variables related to payment process
            'uid': None,
            'fiat_amount': None,
            'btc_amount': None,
            'exchange_rate': None,
            'payment_uri': None,
            'receipt_url': None,
        },
        'withdrawal': {
            # Variables related to withdrawal process
            'uid': None,
            'fiat_amount': None,
            'btc_amount': None,
            'exchange_rate': None,
            'address': None,
            'receipt_url': None,
        },
    }

state = get_initial_gui_state()
