import json
import unittest
from mock import patch

from tornado.testing import AsyncHTTPTestCase

from xbterminal.main_rpc import Application
from xbterminal import api


class ApplicationTestCase(unittest.TestCase):

    @patch('xbterminal.main_rpc.logging.config.dictConfig')
    @patch('xbterminal.main_rpc.init_step_1')
    @patch('xbterminal.main_rpc.init_step_2')
    def test_init(self, init_2_mock, init_1_mock, log_conf_mock):
        Application()
        self.assertTrue(log_conf_mock.called)
        self.assertTrue(init_1_mock.called)
        self.assertTrue(init_2_mock.called)


class JSONRPCServerTestCase(AsyncHTTPTestCase):

    def get_app(self):
        with patch('xbterminal.main_rpc.logging.config.dictConfig'), \
                patch('xbterminal.main_rpc.init_step_1'), \
                patch('xbterminal.main_rpc.init_step_2'):
            return Application()

    def test_echo(self):
        payload = {
            'method': 'echo',
            'jsonrpc': '2.0',
            'params': {'message': 'test'},
            'id': 0,
        }
        headers = {'Content-Type': 'application/json'}
        response = self.fetch(
            '/',
            method='POST',
            body=json.dumps(payload),
            headers=headers)

        self.assertEqual(response.code, 200)
        result = json.loads(response.body)
        self.assertEqual(result['result'], 'test')


class APITestCase(unittest.TestCase):

    def test_get_activation_status(self):
        state = {'remote_config': {'status': 'active'}}
        with patch.dict('xbterminal.api.state', **state):
            result = api.get_activation_status()
        self.assertEqual(result['status'], 'active')
