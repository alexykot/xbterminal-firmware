import datetime
import time

import requests


def get_internet_time():
    json_time_url = "http://json-time.appspot.com/time.json"
    fmt = "%a, %d %b %Y %H:%M:%S +0000"  # %z is not supported
    try:
        response = requests.get(json_time_url, timeout=2)
        data = response.json()
        now = datetime.datetime.strptime(data['datetime'], fmt)
    except Exception:
        return 0
    return time.mktime(now.timetuple())
