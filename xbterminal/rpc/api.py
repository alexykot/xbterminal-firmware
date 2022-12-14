from decimal import Decimal
from jsonrpc import Dispatcher

from xbterminal.rpc.exceptions import OrderNotFound
from xbterminal.rpc.state import state
from xbterminal.rpc.payment import Payment
from xbterminal.rpc.withdrawal import Withdrawal, parse_address
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
    order = Payment.create(state['device_key'],
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
    try:
        order = state['payments'][order_uid]
    except KeyError:
        raise OrderNotFound
    order.check()
    return {
        'status': order.status,
        'paid_btc_amount': str(order.paid_btc_amount),
    }


@dispatcher.add_method
def cancel_payment(**kwargs):
    order_uid = kwargs['uid']
    try:
        order = state['payments'][order_uid]
    except KeyError:
        raise OrderNotFound
    result = order.cancel()
    return result


@dispatcher.add_method
def get_payment_receipt(**kwargs):
    order_uid = kwargs['uid']
    try:
        order = state['payments'][order_uid]
    except KeyError:
        raise OrderNotFound
    return order.receipt_url


@dispatcher.add_method
def create_withdrawal_order(**kwargs):
    fiat_amount = kwargs['fiat_amount']
    order = Withdrawal.create(state['device_key'], fiat_amount)
    state['withdrawals'][order.uid] = order
    result = {
        'uid': order.uid,
        'btc_amount': str(order.btc_amount),
        'tx_fee_btc_amount': str(order.tx_fee_btc_amount),
        'exchange_rate': str(order.exchange_rate),
        'status': order.status,
    }
    return result


@dispatcher.add_method
def get_withdrawal_info(**kwargs):
    order_uid = kwargs['uid']
    order = Withdrawal.get(order_uid)
    state['withdrawals'][order_uid] = order
    result = {
        'uid': order.uid,
        'fiat_amount': str(order.fiat_amount),
        'btc_amount': str(order.btc_amount),
        'tx_fee_btc_amount': str(order.tx_fee_btc_amount),
        'exchange_rate': str(order.exchange_rate),
        'address': order.address,
        'status': order.status,
    }
    return result


@dispatcher.add_method
def confirm_withdrawal(**kwargs):
    order_uid = kwargs['uid']
    address = kwargs['address']
    try:
        order = state['withdrawals'][order_uid]
    except KeyError:
        raise OrderNotFound
    order.confirm(address)
    result = {
        'btc_amount': str(order.btc_amount),
        'exchange_rate': str(order.exchange_rate),
        'status': order.status,
    }
    return result


@dispatcher.add_method
def get_withdrawal_status(**kwargs):
    order_uid = kwargs['uid']
    try:
        order = state['withdrawals'][order_uid]
    except KeyError:
        raise OrderNotFound
    order.check()
    return order.status


@dispatcher.add_method
def cancel_withdrawal(**kwargs):
    order_uid = kwargs['uid']
    try:
        order = state['withdrawals'][order_uid]
    except KeyError:
        raise OrderNotFound
    result = order.cancel()
    return result


@dispatcher.add_method
def get_withdrawal_receipt(**kwargs):
    order_uid = kwargs['uid']
    try:
        order = state['withdrawals'][order_uid]
    except KeyError:
        raise OrderNotFound
    return order.receipt_url


@dispatcher.add_method
def start_bluetooth_server(**kwargs):
    payment_uid = kwargs['payment_uid']
    try:
        payment = state['payments'][payment_uid]
    except KeyError:
        raise OrderNotFound
    state['bluetooth_server'].start(payment)
    return True


@dispatcher.add_method
def stop_bluetooth_server(**kwargs):
    state['bluetooth_server'].stop()
    return True


@dispatcher.add_method
def start_nfc_server(**kwargs):
    message = kwargs['message']
    state['bsp_interface'].write_ndef(message)
    return True


@dispatcher.add_method
def stop_nfc_server(**kwargs):
    state['bsp_interface'].erase_ndef()
    return True


@dispatcher.add_method
def start_qr_scanner(**kwargs):
    state['qr_scanner'].start()
    return True


@dispatcher.add_method
def get_scanned_address(**kwargs):
    address = parse_address(state['qr_scanner'].get_data() or '')
    return address


@dispatcher.add_method
def stop_qr_scanner(**kwargs):
    state['qr_scanner'].stop()
    return True


@dispatcher.add_method
def enable_display(**kwargs):
    state['bsp_interface'].enable_display()
    return True


@dispatcher.add_method
def disable_display(**kwargs):
    state['bsp_interface'].disable_display()
    return True


@dispatcher.add_method
def beep(**kwargs):
    state['bsp_interface'].beep()
    return True


@dispatcher.add_method
def host_add_credit(**kwargs):
    amount = Decimal(kwargs['fiat_amount'])
    state['bsp_interface'].add_credit(amount)
    return True


@dispatcher.add_method
def host_get_payout_status(**kwargs):
    status = state['bsp_interface'].get_payout_status()
    return status


@dispatcher.add_method
def host_get_payout_amount(**kwargs):
    payout = state['bsp_interface'].get_payout_amount()
    return str(payout)


@dispatcher.add_method
def host_withdrawal_started(**kwargs):
    uid = kwargs['uid']
    state['bsp_interface'].withdrawal_started(uid)
    return True


@dispatcher.add_method
def host_withdrawal_completed(**kwargs):
    uid = kwargs['uid']
    amount = Decimal(kwargs['fiat_amount'])
    state['bsp_interface'].withdrawal_completed(uid, amount)
    return True


@dispatcher.add_method
def host_get_withdrawal_uid(**kwargs):
    uid = state['bsp_interface'].get_withdrawal_uid()
    return uid


@dispatcher.add_method
def host_pay_cash(**kwargs):
    amount = Decimal(kwargs['fiat_amount'])
    state['bsp_interface'].pay_cash(amount)
    return True
