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

    def test_echo_error(self):
        payload = {
            'method': 'echo',
            'jsonrpc': '2.0',
            'params': {},
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
        self.assertIn('error', result)
        self.assertEqual(result['error']['message'], 'Server error')
        self.assertEqual(result['error']['code'], -32000)


class APITestCase(unittest.TestCase):

    def test_get_activation_status(self):
        state = {'remote_config': {'status': 'active'}}
        with patch.dict('xbterminal.api.state', **state):
            result = api.get_activation_status()
        self.assertEqual(result['status'], 'active')

    def test_get_activation_status_loading(self):
        with patch.dict('xbterminal.api.state'):
            result = api.get_activation_status()
        self.assertEqual(result['status'], 'loading')

    def test_get_activation_code(self):
        state = {'local_config': {'activation_code': 'test'}}
        with patch.dict('xbterminal.api.state', **state):
            result = api.get_activation_code()
        self.assertEqual(result['activation_code'], 'test')

    def test_get_activation_code_none(self):
        with patch.dict('xbterminal.api.state'):
            result = api.get_activation_code()
        self.assertIsNone(result['activation_code'])
