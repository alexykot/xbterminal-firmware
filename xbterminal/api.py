from decimal import Decimal
from jsonrpc import Dispatcher

from xbterminal.state import state
from xbterminal.stages.payment import Payment
from xbterminal.stages.withdrawal import Withdrawal, get_bitcoin_address
from xbterminal.helpers import configs

dispatcher = Dispatcher()


@dispatcher.add_method
def get_connection_status(**kwargs):
    is_connected = state['watcher'].internet
    return {'status': 'online' if is_connected else 'offline'}


@dispatcher.add_method
def get_activation_status(**kwargs):
    # Return 'loading' if remote_config is not loaded yet
    status = state['remote_config'].get('status', 'loading')
    return {'status': status}


@dispatcher.add_method
def get_activation_code(**kwargs):
    activation_code = state['local_config'].get('activation_code')
    return {'activation_code': activation_code}


@dispatcher.add_method
def get_device_config(**kwargs):
    state['remote_config'] = configs.load_remote_config()
    result = {'remote_server': state['remote_server']}
    result.update(state['remote_config'])
    return result


@dispatcher.add_method
def create_payment_order(**kwargs):
    order = Payment.create_order(state['device_key'],
                                 kwargs['fiat_amount'],
                                 state['bluetooth_server'].mac_address)
    state['payments'][order.uid] = order
    result = {
        'uid': order.uid,
        'btc_amount': str(order.btc_amount),
        'exchange_rate': str(order.exchange_rate),
        'payment_uri': order.payment_uri,
    }
    return result


@dispatcher.add_method
def check_payment_order(**kwargs):
    order_uid = kwargs['uid']
    order = state['payments'][order_uid]
    status = order.check()
    return {'status': status}


@dispatcher.add_method
def cancel_payment_order(**kwargs):
    order_uid = kwargs['uid']
    order = state['payments'][order_uid]
    result = order.cancel()
    return {'result': result}


@dispatcher.add_method
def get_payment_receipt(**kwargs):
    order_uid = kwargs['uid']
    order = state['payments'][order_uid]
    return {'receipt_url': order.receipt_url}


@dispatcher.add_method
def create_withdrawal_order(**kwargs):
    fiat_amount = kwargs['fiat_amount']
    order = Withdrawal.create_order(state['device_key'], fiat_amount)
    state['withdrawals'][order.uid] = order
    result = {
        'uid': order.uid,
        'btc_amount': str(order.btc_amount),
        'exchange_rate': str(order.exchange_rate),
    }
    return result


@dispatcher.add_method
def confirm_withdrawal_order(**kwargs):
    order_uid = kwargs['uid']
    address = kwargs['address']
    order = state['withdrawals'][order_uid]
    order.confirm(address)
    result = {
        'btc_amount': str(order.btc_amount),
        'exchange_rate': str(order.exchange_rate),
    }
    return result


@dispatcher.add_method
def check_withdrawal_order(**kwargs):
    order_uid = kwargs['uid']
    order = state['withdrawals'][order_uid]
    status = order.check()
    return {'status': status}


@dispatcher.add_method
def cancel_withdrawal_order(**kwargs):
    order_uid = kwargs['uid']
    order = state['withdrawals'][order_uid]
    result = order.cancel()
    return {'result': result}


@dispatcher.add_method
def get_withdrawal_receipt(**kwargs):
    order_uid = kwargs['uid']
    order = state['withdrawals'][order_uid]
    return {'receipt_url': order.receipt_url}


@dispatcher.add_method
def start_bluetooth_server(**kwargs):
    payment_uid = kwargs['payment_uid']
    payment = state['payments'][payment_uid]
    state['bluetooth_server'].start(payment)
    return {'result': True}


@dispatcher.add_method
def stop_bluetooth_server(**kwargs):
    state['bluetooth_server'].stop()
    return {'result': True}


@dispatcher.add_method
def start_nfc_server(**kwargs):
    message = kwargs['message']
    state['nfc_server'].start(message)
    return {'result': True}


@dispatcher.add_method
def stop_nfc_server(**kwargs):
    state['nfc_server'].stop()
    return {'result': True}


@dispatcher.add_method
def start_qr_scanner(**kwargs):
    state['qr_scanner'].start()
    return {'result': True}


@dispatcher.add_method
def get_scanned_address(**kwargs):
    address = get_bitcoin_address(state['qr_scanner'].get_data() or '')
    return {'address': address}


@dispatcher.add_method
def stop_qr_scanner(**kwargs):
    state['qr_scanner'].stop()
    return {'result': True}


@dispatcher.add_method
def host_add_credit(**kwargs):
    amount = Decimal(kwargs['fiat_amount'])
    state['host_system'].add_credit(amount)
    return {'result': True}


@dispatcher.add_method
def host_withdraw(**kwargs):
    amount = Decimal(kwargs['fiat_amount'])
    state['host_system'].withdraw(amount)
    return {'result': True}


@dispatcher.add_method
def host_get_payout(**kwargs):
    current_credit = state['host_system'].get_payout()
    return {'current_credit': str(current_credit)}
