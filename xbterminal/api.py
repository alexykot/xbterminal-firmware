from jsonrpc import Dispatcher

from xbterminal.state import state
from xbterminal.stages.payment import Payment

dispatcher = Dispatcher()


@dispatcher.add_method
def echo(**kwargs):
    return kwargs['message']


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
def create_payment_order(**kwargs):
    order = Payment.create_order(state['device_key'],
                                 kwargs['fiat_amount'],
                                 state['bluetooth_server'].mac_address)
    state['payments'][order.uid] = order
    data = {
        'uid': order.uid,
        'btc_amount': str(order.btc_amount),
        'exchange_rate': str(order.exchange_rate),
        'payment_uri': order.payment_uri,
    }
    return data


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
