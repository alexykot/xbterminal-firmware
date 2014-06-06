import logging

import ntplib

from xbterminal import defaults

logger = logging.getLogger(__name__)


def get_internet_time():
    client = ntplib.NTPClient()
    try:
        response = client.request('europe.pool.ntp.org', version=3)
    except Exception as error:
        logger.exception(error)
        return 0
    return response.tx_time
