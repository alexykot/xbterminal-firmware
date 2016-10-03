def get_initial_rpc_state():
    return {
        'device_key': None,
        'rpc_config': {},
        'remote_server': None,
        'remote_config': {},
        'bsp_interface': None,
        'bluetooth_server': None,
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
