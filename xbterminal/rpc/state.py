def get_initial_rpc_state():
    return {
        'device_key': None,
        'rpc_config': {},
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

state = get_initial_rpc_state()
