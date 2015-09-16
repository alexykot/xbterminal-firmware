import requests

import xbterminal
from xbterminal.defaults import (
    REMOTE_API_ENDPOINTS,
    EXTERNAL_CALLS_TIMEOUT,
    EXTERNAL_CALLS_REQUEST_HEADERS)
from xbterminal.helpers import crypto


def get_url(endpoint_name, **kwargs):
    url = (xbterminal.runtime['remote_server'] +
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
        signature = crypto.create_signature(prepared_req.body)
        prepared_req.headers['X-Signature'] = signature
    # Send
    session = requests.Session()
    response = session.send(prepared_req,
                            timeout=EXTERNAL_CALLS_TIMEOUT)
    return response
