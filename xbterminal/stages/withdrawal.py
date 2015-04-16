import re


def get_bitcoin_address(message):
    match = re.match(r'(bitcoin:)?([a-zA-Z0-9]{26,35})(\?|$)', message)
    if match:
        return match.group(2)
