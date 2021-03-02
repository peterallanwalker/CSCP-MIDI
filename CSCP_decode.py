# parses valid CSCP messages, as unpacked by CSCP_unpack

import CSCP_utils as utils


class Message:
    def __init__(self, message_bytes):

        # All messages are pre-validated by header and checksum,
        #   ACK/NAK messages are then passed through as a single int
        if type(message_bytes) == int:
            self.encoded = False
            self.byte_count = False
            self.recipient = False
            self.operation = False
            self.strip = False
            self.value = False
            if message_bytes == 4:
                self.type = 'ACK'
            elif message_bytes == 5:
                self.type = 'NAK'

        else:
            self.encoded = message_bytes
            self.byte_count = message_bytes[utils.BYTE_COUNT_BYTE]
            self.recipient = _get_recipient(message_bytes)
            self.type = _get_type(message_bytes)
            self.operation = _get_operation(message_bytes)

            if self.operation in ('read_console_info', 'read_console_name'):
                self.strip = False
            else:
                self.strip = _get_strip(message_bytes, self.operation)

            self.value = _get_value(message_bytes, self.operation)

    def __str__(self):
        return "CSCP Message - Recipient: {}, Type: {}, Operation: {}, Fader Strip: {}, Value: {}, encoded: {}".format(self.recipient, self.type, self.operation, self.strip, self.value, repr(self.encoded))


def _get_recipient(message_bytes):
    device = message_bytes[utils.DEVICE_BYTE]
    if device in utils.DEVICES:
        return utils.DEVICES[device]
    else:
        return 'unknown'


def _get_type(message_bytes):
    """ Returns message type - read or write
        First bit (MSB) of the command MSB byte denotes CSCP message type
    """
    # bin(<int>) is returning binary as a string prefixed with '0b',
    #   so index 2 is the first bit (MSB of the byte)
    type_bit = int(bin(message_bytes[utils.CMDMSB])[2])

    if type_bit == 0:
        message_type = 'read'
    else:
        message_type = 'write'

    return message_type


def _get_operation(message_bytes):
    """ Returns message operation / control type
        CMD LSB denotes operation/control type
    """
    op_byte = message_bytes[utils.CMDLSB]
    if op_byte in utils.OPERATIONS:
        return utils.OPERATIONS[op_byte]
    else:
        return 'unknown'


def _get_strip(message_bytes, operation):

    if operation == 'main_send_toggle':
        return message_bytes[utils.FDRMSB]
    elif operation == 'read_console_name':
        return False

    try:
        return _add_bytes([message_bytes[utils.FDRMSB], message_bytes[utils.FDRMSB + 1]])
    except KeyError:
        return False


def _get_value(message_bytes, operation):
    # TODO - sort this mess out!

    if operation in ('cut_toggle', 'pfl_toggle'):
        return message_bytes[utils.VALMSB]

    elif operation == 'fader_move':
        msb = message_bytes[utils.VALMSB]         # Returns decimal
        lsb = message_bytes[utils.VALMSB + 1]     # Returns decimal
        values = [msb, lsb]
        return _add_bytes(values)

    elif operation == 'read_fader_label':
        return message_bytes[7:-1].decode('utf-8')

    elif operation == 'fader_path_info':
        r = {'path_type': utils.PATH_TYPES[message_bytes[utils.CMDLSB + 3]],
             'path_width': utils.AUDIO_WIDTHS[message_bytes[utils.CMDLSB + 4]],
             'path_id': _add_bytes([message_bytes[utils.CMDLSB + 5], message_bytes[utils.CMDLSB + 6]])}

        return r

    # if its a 'read_console_info' message response from mixer,
    # it will have a "write" type and need the following handling...
    elif operation == 'read_console_info' and message_bytes[utils.CMDMSB] == list(utils.TYPE.keys())[list(utils.TYPE.values()).index('write')]:
        r = {}
        msb = message_bytes[utils.FDRMSB]
        lsb = message_bytes[utils.FDRMSB + 1]
        version = [msb, lsb]
        r['CSCP version'] = _add_bytes(version)

        msb = message_bytes[utils.FDRMSB + 2]
        lsb = message_bytes[utils.FDRMSB + 3]
        fader_qty = [msb, lsb]
        r['fader quantity'] = _add_bytes(fader_qty)

        msb = message_bytes[utils.FDRMSB + 4]
        lsb = message_bytes[utils.FDRMSB + 5]
        mains_qty = [msb, lsb]
        r['mains quantity'] = _add_bytes(mains_qty)

        r['console name'] = message_bytes[utils.FDRMSB + 12:-2].decode('utf-8')

        return r

    elif operation == 'read_console_name':
        return str(message_bytes[5:-1], 'utf-8')

    else:
        return False


def _add_bytes(values):
    """ Takes decimal values from separate bytes that represent a single value, e.g. msb & lsb,
        and returns as single decimal value
        bytes - array of decimal values
    """
    combined = bytes(values)  # convert the decimal values to a byte string
    combined = int.from_bytes(combined,
                              byteorder='big')  # convert the byte string back to single decimal number
    return combined


if __name__ == '__main__':
    test_messages = [b'\xf1\x06\x00\x80\x00\x00\x03\x02\xe8\x93',
                     b'\xf1\x06\xff\x00\x00\x00\x03\x02\xe8\x93',
                     b'\xf1\x06\x10\x80\x00\x00\x03\x02\xe8\x93',
                     ]

    message = Message(test_messages[1])

    # example of received valid data:
    message = Message(b'\xf1\x16\xff\x80\x08\x00\x15\x00`\x00\x04\x00\x00\x00\x00\x00\x00My Brio\x00\x8d')

    print('message:', message)
    print('byte count:', message.byte_count)
    print('recipient:', message.recipient)
    print('type:', message.type)
    print('operation:', message.operation)
    print('strip:', message.strip)
    print('value:', message.value)