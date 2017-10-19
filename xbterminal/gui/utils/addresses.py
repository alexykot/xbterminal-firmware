"""
Adapted from:
https://github.com/nederhoed/python-bitcoinaddress/blob/master/bitcoinaddress/validation.py
"""

from hashlib import sha256

digits58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


def _bytes_to_long(bytestring, byteorder):
    """Convert a bytestring to a long
    For use in python version prior to 3.2
    """
    result = []
    if byteorder == 'little':
        result = (v << i * 8 for (i, v) in enumerate(bytestring))
    else:
        result = (v << i * 8 for (i, v) in enumerate(reversed(bytestring)))
    return sum(result)


def _long_to_bytes(n, length, byteorder):
    """Convert a long to a bytestring
    For use in python version prior to 3.2
    Source:
    http://bugs.python.org/issue16580#msg177208
    """
    if byteorder == 'little':
        indexes = range(length)
    else:
        indexes = reversed(range(length))
    return bytearray((n >> i * 8) & 0xff for i in indexes)


def decode_base58(address, length):
    """Decode a base58 encoded address
    This form of base58 decoding is bitcoind specific. Be careful outside of
    bitcoind context.
    """
    n = 0
    for char in address:
        try:
            n = n * 58 + digits58.index(char)
        except:
            msg = u"Character not part of Bitcoin's base58: '%s'"
            raise ValueError(msg % (char,))
    try:
        return n.to_bytes(length, 'big')
    except AttributeError:
        # Python version < 3.2
        return _long_to_bytes(n, length, 'big')


def encode_base58(bytestring):
    """Encode a bytestring to a base58 encoded string
    """
    # Count zero's
    zeros = 0
    for i in range(len(bytestring)):
        if bytestring[i] == 0:
            zeros += 1
        else:
            break
    try:
        n = int.from_bytes(bytestring, 'big')
    except AttributeError:
        # Python version < 3.2
        n = _bytes_to_long(bytestring, 'big')
    result = ''
    (n, rest) = divmod(n, 58)
    while n or rest:
        result += digits58[rest]
        (n, rest) = divmod(n, 58)
    return zeros * '1' + result[::-1]  # reverse string


MAGICBYTES = {
    'BTC': (b'\0', b'\5'),
    'TBTC': (b'\x6f', b'\xc4'),
    'DASH': (b'\x4c', b'\x10'),
    'TDASH': (b'\x8c', b'\x13'),
}


def is_valid_address(address, coin_name):
    # Address prefixes
    # https://github.com/richardkiss/pycoin/blob/master/pycoin/networks/all.py
    magicbyte = MAGICBYTES[coin_name]
    clen = len(address)
    if clen < 27 or clen > 35:
        return False
    try:
        bcbytes = decode_base58(address, 25)
    except ValueError:
        return False
    for mb in magicbyte:
        if bcbytes.startswith(mb):
            break
    else:
        return False
    # Compare checksum
    checksum = sha256(sha256(bcbytes[:-4]).digest()).digest()[:4]
    if bcbytes[-4:] != checksum:
        return False
    # Encoded bytestring should be equal to the original address,
    # for example '14oLvT2' has a valid checksum, but is not a valid btc
    # address
    return address == encode_base58(bcbytes)
