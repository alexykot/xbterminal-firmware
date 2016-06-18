from jsonrpc import Dispatcher

from xbterminal.state import state

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
