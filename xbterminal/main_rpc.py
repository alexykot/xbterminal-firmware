import logging.config
import sys
import os

from jsonrpc import JSONRPCResponseManager
import tornado.ioloop
import tornado.web

include_path = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, include_path)

from xbterminal.rpc.api import dispatcher
from xbterminal.rpc.settings import LOG_CONFIG
from xbterminal.rpc.init import init_step_1, init_step_2
from xbterminal.rpc.state import state

logger = logging.getLogger(__name__)


class JSONRPCHandler(tornado.web.RequestHandler):

    def post(self):
        logger.debug(self.request.body)
        response = JSONRPCResponseManager.handle(
            self.request.body, dispatcher)
        self.write(response.json)


class Application(tornado.web.Application):

    def __init__(self, *args, **kwargs):
        logging.config.dictConfig(LOG_CONFIG)

        super(Application, self).__init__(*args, **kwargs)
        self.add_handlers('', [(r'/', JSONRPCHandler)])

        init_step_1(state)
        init_step_2(state)


if __name__ == "__main__":
    app = Application()
    app.listen(8888, address='127.0.0.1')
    tornado.ioloop.IOLoop.current().start()
