import unittest
from mock import patch, Mock
from tests import mocks

from xbterminal.rpc import settings
from xbterminal.helpers import api
from xbterminal.rpc.exceptions import NetworkError, ServerError


@patch.dict('xbterminal.helpers.api.state',
            remote_server='https://xbterminal.io')
class ApiUtilsTestCase(unittest.TestCase):

    def test_get_url(self):
        url = api.get_url('config', device_key='test')
        self.assertEqual(url, 'https://xbterminal.io/api/v2/devices/test/')

    @patch('xbterminal.helpers.api.requests.Session')
    def test_send_request(self, session_cls_mock):
        response_mock = Mock(status_code=200)
        session_mock = Mock(**{'send.return_value': response_mock})
        session_cls_mock.return_value = session_mock

        api.send_request('get', 'http://test_url.com')
        self.assertTrue(session_mock.send.called)
        request = session_mock.send.call_args[0][0]
        self.assertEqual(request.url, 'http://test_url.com/')
        self.assertEqual(request.headers['User-Agent'],
                         settings.EXTERNAL_CALLS_REQUEST_HEADERS['User-Agent'])
        self.assertNotIn('X-Signature', request.headers)
        self.assertEqual(session_mock.send.call_args[1]['timeout'],
                         settings.EXTERNAL_CALLS_TIMEOUT)

    @patch('xbterminal.helpers.api.requests.Session')
    @patch('xbterminal.helpers.crypto.read_secret_key',
           new=mocks.read_secret_key_mock)
    def test_send_request_signed(self, session_cls_mock):
        response_mock = Mock(status_code=200)
        session_mock = Mock(**{'send.return_value': response_mock})
        session_cls_mock.return_value = session_mock

        api.send_request('post', 'http://test_url.com',
                         data={'aaa': 111}, signed=True)
        self.assertTrue(session_mock.send.called)
        request = session_mock.send.call_args[0][0]
        self.assertEqual(request.url, 'http://test_url.com/')
        self.assertIn('X-Signature', request.headers)

    @patch('xbterminal.helpers.api.requests.Session')
    @patch('xbterminal.helpers.crypto.read_secret_key',
           new=mocks.read_secret_key_mock)
    def test_send_request_signed_no_body(self, session_cls_mock):
        response_mock = Mock(status_code=204)
        session_mock = Mock(**{'send.return_value': response_mock})
        session_cls_mock.return_value = session_mock

        api.send_request('post', 'http://test_url.com', signed=True)
        self.assertTrue(session_mock.send.called)
        request = session_mock.send.call_args[0][0]
        self.assertEqual(request.url, 'http://test_url.com/')
        self.assertIn('X-Signature', request.headers)

    @patch('xbterminal.helpers.api.requests.Session')
    def test_send_request_network_error(self, session_cls_mock):
        session_mock = Mock(**{'send.side_effect': IOError})
        session_cls_mock.return_value = session_mock

        with self.assertRaises(NetworkError):
            api.send_request('get', 'http://test_url.com')

    @patch('xbterminal.helpers.api.requests.Session')
    def test_send_request_server_error(self, session_cls_mock):
        response_mock = Mock(status_code=500)
        session_mock = Mock(**{'send.return_value': response_mock})
        session_cls_mock.return_value = session_mock

        with self.assertRaises(ServerError):
            api.send_request('get', 'http://test_url.com')
