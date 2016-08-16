import logging
import requests

from xbterminal.rpc.settings import (
    REMOTE_API_ENDPOINTS,
    EXTERNAL_CALLS_TIMEOUT,
    EXTERNAL_CALLS_REQUEST_HEADERS)
from xbterminal.rpc.utils import crypto
from xbterminal.rpc.exceptions import NetworkError, ServerError
from xbterminal.rpc.state import state

logger = logging.getLogger(__name__)

VALID_STATUS_CODES = [200, 201, 204]


def get_url(endpoint_name, **kwargs):
    url = (state['remote_server'] +
           REMOTE_API_ENDPOINTS[endpoint_name])
    if not kwargs:
        return url
    else:
        return url.format(**kwargs)


def send_request(method, url, data=None, headers=None, signed=False):
    """
    Prepare and send API request
    Returns:
        response
    """
    headers = headers or {}
    headers.update(EXTERNAL_CALLS_REQUEST_HEADERS)
    # Create request
    req = requests.Request(method.upper(),
                           url,
                           data=data,
                           headers=headers)
    prepared_req = req.prepare()
    if signed:
        signature = crypto.create_signature(prepared_req.body or '')
        prepared_req.headers['X-Signature'] = signature

    # Send
    session = requests.Session()
    try:
        response = session.send(prepared_req,
                                timeout=EXTERNAL_CALLS_TIMEOUT)
    except Exception as error:
        logger.exception(error)
        raise NetworkError

    if response.status_code not in VALID_STATUS_CODES:
        logger.error(response.content)
        raise ServerError

    return response
