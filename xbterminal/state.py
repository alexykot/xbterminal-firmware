from collections import deque

from xbterminal import defaults


def get_initial_state():
    return {
        'device_key': None,
        'local_config': {},
        'remote_server': None,
        'remote_config': {},
        'remote_config_last_update': 0,
        'last_activity_timestamp': None,
        'keypad': None,
        'keyboard_events': deque(maxlen=1),  # Only for keyboard driver
        'host_system': None,
        'bluetooth_server': None,
        'nfc_server': None,
        'qr_scanner': None,
        'screen_buttons': {button_name: False for button_name
                           in defaults.BUTTONS},
        'init': {
            'clock_synchronized': False,
            'registration': False,
            'remote_config': False,
        },
        'CURRENT_STAGE': defaults.STAGES['bootup'],
        'payment': {
            # Variables related to payment process
            'fiat_amount': None,
            'order': None,
            'qr_image_path': None,
            'receipt_url': None,
        },
        'withdrawal': {
            # Variables related to withdrawal process
            'fiat_amount': None,
            'order': None,
            'address': None,
            'receipt_url': None,
            'qr_image_path': None,
        },
        # For API
        'payments': {},
        'withdrawals': {},
    }

state = get_initial_state()
