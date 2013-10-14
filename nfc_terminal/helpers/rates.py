__author__ = 'tux'

import requests

URL = "https://api.bitcoinaverage.com/ticker/GBP"


def get_rate():
    r = requests.get(URL).json()

    last_price = r['last']
    return last_price