"""
GAP & AD
"""
import conv

# https://www.bluetooth.org/en-us/specification/assigned-numbers/generic-access-profile
DATA_TYPES = [
    ('flags', 0x01, conv.uint8_list_to_bl),
    ('incomplete_uuid_16', 0x02, conv.uuid_list_to_bl),
    ('complete_uuid_16', 0x03, conv.uuid_list_to_bl),
    ('incomplete_uuid_128', 0x06, conv.uuid_list_to_bl),
    ('short_name', 0x08, conv.str_to_b),
    ('complete_name', 0x09, conv.str_to_b),
]


def encode_data(packet):
    """
    Encode advertisement data or scan data
    """
    bytes_ = ""
    for type_name, type_value, encoder in DATA_TYPES:
        if type_name in packet:
            ad_type = conv.uint8_to_bl(type_value)
            ad_data = encoder(packet[type_name])
            ad_length = conv.uint8_to_bl(len(ad_type + ad_data))
            bytes_ += ad_length + ad_type + ad_data
    return bytes_
