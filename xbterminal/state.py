from collections import deque

from xbterminal import defaults


def get_initial_rpc_state():
    return {
        'device_key': None,
        'local_config': {},
        'remote_server': None,
        'remote_config': {},
        'host_system': None,
        'bluetooth_server': None,
        'nfc_server': None,
        'qr_scanner': None,
        'init': {
            'clock_synchronized': False,
            'registration': False,
            'remote_config': False,
        },
        'payments': {},
        'withdrawals': {},
    }


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
                           in defaults.BUTTONS},
        'CURRENT_STAGE': defaults.STAGES['bootup'],
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

rpc_state = get_initial_rpc_state()

gui_state = get_initial_gui_state()
