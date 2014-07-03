"""
Helper functions
"""
import binascii
import struct


def uint8_to_bl(integer):
    """
    Convert 8-bit unsigned integer to bytes [little-endian]
    """
    return struct.pack("<B", integer)


def uint16_to_bl(integer):
    """
    Convert unsigned 16-bit integer to bytes [little-endian]
    """
    return struct.pack("<H", integer)


def uint8_list_to_bl(integer_list):
    result = 0
    for int_ in integer_list:
        result |= int_
    return uint8_to_bl(result)


def uuid_to_bl(uuid):
    """
    Convert uuid to bytes [little-endian]
    """
    bts = binascii.unhexlify(uuid.replace('-', ''))
    return bts[::-1]


def uuid_list_to_bl(uuid_list):
    result = ""
    for uuid in uuid_list:
        result += uuid_to_bl(uuid)
    return result


def str_to_b(s):
    """
    Convert string to bytes
    """
    return s


def bl_to_hex(bl):
    """
    Convert bytes [little-endian] to hex
    """
    return binascii.hexlify(bl[::-1])


def bl_to_int(bl):
    """
    Convert bytes [little-endian] to integer
    """
    return int(bl_to_hex(bl), 16)
