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
