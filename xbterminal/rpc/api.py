from decimal import Decimal
from jsonrpc import Dispatcher

from xbterminal.rpc.state import state
from xbterminal.rpc.payment import Payment
from xbterminal.rpc.withdrawal import Withdrawal, get_bitcoin_address
from xbterminal.rpc.utils import configs

dispatcher = Dispatcher()


@dispatcher.add_method
def get_connection_status(**kwargs):
    is_connected = state['watcher'].internet
    return 'online' if is_connected else 'offline'


@dispatcher.add_method
def get_device_status(**kwargs):
    # Return 'loading' if remote_config is not loaded yet
    status = state['remote_config'].get('status', 'loading')
    return status


@dispatcher.add_method
def get_activation_code(**kwargs):
    activation_code = state['rpc_config'].get('activation_code')
    return activation_code


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
def get_payment_status(**kwargs):
    order_uid = kwargs['uid']
    order = state['payments'][order_uid]
    status = order.check()
    return status


@dispatcher.add_method
def cancel_payment(**kwargs):
    order_uid = kwargs['uid']
    order = state['payments'][order_uid]
    result = order.cancel()
    return result


@dispatcher.add_method
def get_payment_receipt(**kwargs):
    order_uid = kwargs['uid']
    order = state['payments'][order_uid]
    return order.receipt_url


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
def confirm_withdrawal(**kwargs):
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
def get_withdrawal_status(**kwargs):
    order_uid = kwargs['uid']
    order = state['withdrawals'][order_uid]
    status = order.check()
    return status


@dispatcher.add_method
def cancel_withdrawal(**kwargs):
    order_uid = kwargs['uid']
    order = state['withdrawals'][order_uid]
    result = order.cancel()
    return result


@dispatcher.add_method
def get_withdrawal_receipt(**kwargs):
    order_uid = kwargs['uid']
    order = state['withdrawals'][order_uid]
    return order.receipt_url


@dispatcher.add_method
def start_bluetooth_server(**kwargs):
    payment_uid = kwargs['payment_uid']
    payment = state['payments'][payment_uid]
    state['bluetooth_server'].start(payment)
    return True


@dispatcher.add_method
def stop_bluetooth_server(**kwargs):
    state['bluetooth_server'].stop()
    return True


@dispatcher.add_method
def start_nfc_server(**kwargs):
    message = kwargs['message']
    state['nfc_server'].start(message)
    return True


@dispatcher.add_method
def stop_nfc_server(**kwargs):
    state['nfc_server'].stop()
    return True


@dispatcher.add_method
def start_qr_scanner(**kwargs):
    state['qr_scanner'].start()
    return True


@dispatcher.add_method
def get_scanned_address(**kwargs):
    address = get_bitcoin_address(state['qr_scanner'].get_data() or '')
    return address


@dispatcher.add_method
def stop_qr_scanner(**kwargs):
    state['qr_scanner'].stop()
    return True


@dispatcher.add_method
def host_add_credit(**kwargs):
    amount = Decimal(kwargs['fiat_amount'])
    state['host_system'].add_credit(amount)
    return True


@dispatcher.add_method
def host_withdraw(**kwargs):
    amount = Decimal(kwargs['fiat_amount'])
    state['host_system'].withdraw(amount)
    return True


@dispatcher.add_method
def host_get_payout(**kwargs):
    payout = state['host_system'].get_payout()
    if payout:
        return str(payout)
    else:
        return None
