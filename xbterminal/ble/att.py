import binascii
import logging
import math
import socket

import conv

L2CAP_MTU = 23

# https://android.googlesource.com/platform/external/bluetooth/bluez/+/master/attrib/att.h
# GATT Profile Attribute types
GATT_PRIM_SVC_UUID = 0x2800
GATT_SND_SVC_UUID = 0x2801
GATT_INCLUDE_UUID = 0x2802
GATT_CHARAC_UUID = 0x2803

# Attribute Protocol Opcodes
ATT_OP_ERROR = 0x01
ATT_OP_MTU_REQ = 0x02
ATT_OP_MTU_RESP = 0x03
ATT_OP_FIND_INFO_REQ = 0x04
ATT_OP_FIND_INFO_RESP = 0x05
ATT_OP_FIND_BY_TYPE_REQ = 0x06
ATT_OP_FIND_BY_TYPE_RESP = 0x07
ATT_OP_READ_BY_TYPE_REQ = 0x08
ATT_OP_READ_BY_TYPE_RESP = 0x09
ATT_OP_READ_REQ = 0x0A
ATT_OP_READ_RESP = 0x0B
ATT_OP_READ_BLOB_REQ = 0x0C
ATT_OP_READ_BLOB_RESP = 0x0D
ATT_OP_READ_MULTI_REQ = 0x0E
ATT_OP_READ_MULTI_RESP = 0x0F
ATT_OP_READ_BY_GROUP_REQ = 0x10
ATT_OP_READ_BY_GROUP_RESP = 0x11
ATT_OP_WRITE_REQ = 0x12
ATT_OP_WRITE_RESP = 0x13
ATT_OP_WRITE_CMD = 0x52
ATT_OP_PREP_WRITE_REQ = 0x16
ATT_OP_PREP_WRITE_RESP = 0x17
ATT_OP_EXEC_WRITE_REQ = 0x18
ATT_OP_EXEC_WRITE_RESP = 0x19
ATT_OP_HANDLE_NOTIFY = 0x1B
ATT_OP_HANDLE_IND = 0x1D
ATT_OP_HANDLE_CNF = 0x1E
ATT_OP_SIGNED_WRITE_CMD = 0xD2

# Error codes for Error response PDUservice.generic_access
ATT_ECODE_INVALID_HANDLE = 0x01
ATT_ECODE_READ_NOT_PERM = 0x02
ATT_ECODE_WRITE_NOT_PERM = 0x03
ATT_ECODE_INVALID_PDU = 0x04
ATT_ECODE_AUTHENTICATION = 0x05
ATT_ECODE_REQ_NOT_SUPP = 0x06
ATT_ECODE_INVALID_OFFSET = 0x07
ATT_ECODE_AUTHORIZATION = 0x08
ATT_ECODE_PREP_QUEUE_FULL = 0x09
ATT_ECODE_ATTR_NOT_FOUND = 0x0A
ATT_ECODE_ATTR_NOT_LONG = 0x0B
ATT_ECODE_INSUFF_ENCR_KEY_SIZE = 0x0C
ATT_ECODE_INVAL_ATTR_VALUE_LEN = 0x0D
ATT_ECODE_UNLIKELY = 0x0E
ATT_ECODE_INSUFF_ENC = 0x0F
ATT_ECODE_UNSUPP_GRP_TYPE = 0x10
ATT_ECODE_INSUFF_RESOURCES = 0x11

logger = logging.getLogger(__name__)


def handle_request(request_hex, gatt_db):
    """
    Accepts:
        request_hex: hex string
        gatt_db: GATT database
    Returns:
        response: hex string
    """
    request = binascii.unhexlify(request_hex)
    request_type = conv.bl_to_int(request[0])
    if request_type == ATT_OP_MTU_REQ:
        response = handle_mtu_request(request)
    elif request_type == ATT_OP_FIND_INFO_REQ:
        response = handle_find_info_request(request)
    elif request_type == ATT_OP_FIND_BY_TYPE_REQ:
        response = handle_find_by_type_request(request)
    elif request_type == ATT_OP_READ_BY_TYPE_REQ:
        response = handle_read_by_type_request(request)
    elif request_type == ATT_OP_READ_REQ:
        response = handle_read_request(request)
    elif request_type == ATT_OP_READ_BY_GROUP_REQ:
        response = handle_read_by_group_request(request, gatt_db)
    elif request_type == ATT_OP_WRITE_REQ:
        response = handle_write_request(request)
    else:
        response = error_response(request_type,
                                  0x0000,
                                  ATT_ECODE_REQ_NOT_SUPP)
    return binascii.hexlify(response) + '\n'


def error_response(op_code, handle, error_code):
    """
    Generate error reponse
    """
    logger.warning("error, code {0}".format(error_code))
    response = (conv.uint8_to_bl(ATT_OP_ERROR) +
                conv.uint8_to_bl(op_code) +
                conv.uint16_to_bl(handle) +
                conv.uint8_to_bl(error_code))
    return response


def handle_mtu_request(request):
    logger.debug("mtu request")
    return ""


def handle_find_info_request(request):
    logger.debug("find info request")
    return ""


def handle_find_by_type_request(request):
    logger.debug("find by type request")
    return ""


def handle_read_by_type_request(request):
    logger.debug("read by type request")
    return ""


def handle_read_request(request):
    logger.debug("read request")
    return ""


def handle_read_by_group_request(request, gatt_db):
    # Parse request
    start_handle = conv.bl_to_int(request[1:3])
    end_handle = conv.bl_to_int(request[3:5])
    group_type = conv.bl_to_int(request[5:])
    logger.debug("read by group, {0} - {1}, {2}".\
        format(start_handle, end_handle, group_type))
    # Generate response
    if group_type == GATT_PRIM_SVC_UUID:
        # Primary service
        services = []
        for handle in range(start_handle, end_handle + 1):
            attribute = gatt_db.get(handle)
            if not attribute:
                break
            if attribute['type'] == 'service':
                services.append(attribute)
        if services:
            uuid_length = len(services[0]['uuid'])
            length_per_service = 4 + uuid_length / 2
            max_services = math.floor((L2CAP_MTU - 2) / length_per_service)
            response = (conv.uint8_to_bl(ATT_OP_READ_BY_GROUP_RESP) +
                        conv.uint8_to_bl(length_per_service))
            for idx, service in enumerate(services):
                if (
                    idx + 1 > max_services
                    or len(service['uuid']) != uuid_length
                ):
                    break
                response += (conv.uint16_to_bl(service['start_handle']) +
                             conv.uint16_to_bl(service['end_handle']) +
                             conv.uuid_to_bl(service['uuid']))
        else:
            # Services not found
            response = error_response(ATT_OP_READ_BY_GROUP_REQ,
                                      start_handle,
                                      ATT_ECODE_ATTR_NOT_FOUND)
    else:
        # Unsupported type
        response = error_response(ATT_OP_READ_BY_GROUP_REQ,
                                  start_handle,
                                  ATT_ECODE_UNSUPP_GRP_TYPE)
    logger.debug('read by group rsp, {0}'.format(response.encode('hex')))
    return response


def handle_write_request(request):
    logger.debug("write request")
    return ""


# https://developer.bluetooth.org/gatt/services/Pages/ServiceViewer.aspx?u=org.bluetooth.service.generic_access.xml
# Bluetooth core spec., version 4.1, vol. 3, part G
GAP_SERVICE_UUID = '1800'
GAP_CHR_DEVICE_NAME_UUID = '2A00'
GAP_CHR_APPEARANCE_UUID = '2A01'
GAP_CHR_APPEARANCE_GENERIC_COMPUTER = 0x0080

CLIENT_CHR_CONFIG_UUID = '2902'

PROPERTIES = {
    'read': 0x02,
    'write_without_response': 0x04,
    'write': 0x08,
    'notify': 0x10,
}


def set_services(services):
    gatt_db = {}
    all_services = [
        {'uuid': GAP_SERVICE_UUID,
         'characteristics': [
            {'uuid': GAP_CHR_DEVICE_NAME_UUID,
             'properties': ['read'],
             'secure': [],
             'value': socket.gethostname(),
             'descriptors': [],
            },
            {'uuid': GAP_CHR_APPEARANCE_UUID,
             'properties': ['read'],
             'secure': [],
             'value': conv.uint16_to_bl(GAP_CHR_APPEARANCE_GENERIC_COMPUTER),
             'descriptors': [],
            }
         ]
        }
    ]
    all_services += services
    handle = 0
    for service in all_services:
        handle += 1
        service_handle = handle
        gatt_db[service_handle] = {
            'type': 'service',
            'uuid': service['uuid'],
            'attribute': service,
            'start_handle': service_handle,
        }
        for char in service['characteristics']:
            properties = 0x00
            secure = 0x00
            for prop in char['properties']:
                properties |= PROPERTIES[prop]
                if prop in char['secure']:
                    secure |= PROPERTIES[prop]
            handle += 1
            char_handle = handle
            handle += 1
            char_value_handle = handle
            gatt_db[char_handle] = {
                'type': 'characteristic',
                'uuid': char['uuid'],
                'properties': properties,
                'secure': secure,
                'attribute': char,
                'start_handle': char_handle,
                'value_handle': char_value_handle,
            }
            gatt_db[char_value_handle] = {
                'type': 'characteristic_value',
                'handle': char_value_handle,
                'value': char['value'],
            }
            if properties & 0x10:
                # Add client characteristic configuration descriptor
                handle += 1
                char_conf_descriptor_handle = handle
                gatt_db[char_conf_descriptor_handle] = {
                    'type': 'descriptor',
                    'handle': char_conf_descriptor_handle,
                    'uuid': CLIENT_CHR_CONFIG_UUID,
                    'attribute': characteristic,
                    'properties': PROPERTIES['read'] | PROPERTIES['write'],
                    'secure': PROPERTIES['read'] | PROPERTIES['write'] if secure & 0x10 else 0,
                    'value': conv.uint16_to_bl(0x0000),
                }
            for descriptor in char['descriptors']:
                handle += 1
                descriptor_handle = handle
                self._handles[descriptor_handle] = {
                    'type': 'descriptor',
                    'handle': descriptor_handle,
                    'uuid': descriptor['uuid'],
                    'attribute': descriptor,
                    'properties': CHR_PROPERTIES['read'],
                    'secure': 0x00,
                    'value': descriptor['value'],
                }
        gatt_db[service_handle]['end_handle'] = handle
    return gatt_db
