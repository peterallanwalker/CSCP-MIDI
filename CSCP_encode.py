# CSCP_encode
# Provides a CSCP Message class
# Instantiates using human readable values
# Creates attribute Message.encoded - a CSCP encoded byte string with checksum, ready to send to a mixer

# Copyright Peter Walker 2020.
# Feedback/Requests - peter.allan.walker@gmail.com

# See Readme.txt for info on how to use this app.
# See Project_Notes.txt for info on the implementation - how the app works.

import struct  # used to convert decimal values > 255 into 2 hex bytes
import CSCP_utils as utils

# TODO - CSCP_decode provides a Message class possibly identical to this one, it's just initialised differently,
#  so should combine them into a single class


class Message:

    def __init__(self, operation, strip=None, value=None, msg_type='write', recipient='mixer'):
        self.recipient = recipient
        self.type = msg_type
        self.operation = operation
        self.strip = strip
        self.value = value
        self.encoded = self._encode()
        self.byte_count = utils.OP_BYTE_COUNTS[self.operation]

    def __str__(self):
        return "CSCP Message - Recipient: {}, Type: {}, Operation: {}, Fader Strip: {}, Value: {}, encoded: {}".format(self.recipient, self.type, self.operation, self.strip, self.value, repr(self.encoded))

    def _encode(self):
        """ Takes CSCP data in Message object format
            Returns complete byte string ready to send to mixer
            # NOTE, this version only handles strip fader, pfl/solo & cut/mute messages
        """
        # Look up CSCP header value constants from CSCP_utils.py
        soh = utils.CSCP_HEADER_START  # CSCP Start Of Header byte value
        bc = utils.OP_BYTE_COUNTS[self.operation]  # Byte count of message based on message type/operation
        # Device type / message recipient (Mixer vs controller)
        dev = list(utils.DEVICES.keys())[
            list(utils.DEVICES.values()).index(self.recipient)]  # Dictionary lookup key by value

        # Command bytes (denotes message type, e.g. "fader_move")
        # Following uses a neat way to get dictionary lookup key by value,
        # got it from Stack-Exchange or similar, lost the link :(
        # ...think this is what's meant by 'list comprehension'... TODO - learn list comprehension!
        cmdmsb = list(utils.TYPE.keys())[list(utils.TYPE.values()).index(self.type)]
        cmdlsb = list(utils.OPERATIONS.keys())[
            list(utils.OPERATIONS.values()).index(self.operation)]

        header = [soh, bc, dev]
        payload = [cmdmsb, cmdlsb]

        # Convert single decimal value to two bytes (still decimal)
        # Note, the order of assignment being returned from struct.pack is lsb, msb!
        fdrlsb, fdrmsb = struct.pack('<H', self.strip)
        payload += [fdrmsb, fdrlsb]

        # Cannot just check true/false as 0 is valid value that returns False
        if self.value or self.value == 0:
            values = []
            if bc == 5:
                values.append(self.value)

            elif bc == 6:
                # Convert value to two bytes (still decimal)
                vallsb, valmsb = struct.pack('<H', self.value)
                values = [valmsb, vallsb]

            if values:
                for value in values:
                    payload.append(value)

        checksum = int(utils.calc_checksum(payload), 16)
        message = header + payload
        message.append(checksum)
        message = bytes(message)

        return message


def read_back(lookup='read_console_name'):
    """ Generates a CSCP message byte string that requests data back from mixer.
        This is being called by CSCP_connection to "ping" the mixer.
        Because this only provides the bytes and not a full message object with
        the bytes being the .encoded attribute, CSCP_connection.send()
        takes bytes, not a message object. This is OK, but a little annoying that
        in CSCP-MIDI I call MIDI_connection.send(message) but for CSCP I'm calling
        CSCP_connection.send(message.encoded)
        # TODO - consider changing this function to return a full Message
        # TODO -   (will require adaptation of the above Message Class)
        # TODO -   or perhaps provide an additional CSCP_connection.send()
    """
    # "DEV" byte. Sourced from dictionary lookup key by value
    recipient_device = list(utils.DEVICES.keys())[
        list(utils.DEVICES.values()).index('mixer')]
    # "CMD MSB" byte. Sourced from dictionary lookup key by value
    message_type = list(utils.TYPE.keys())[list(utils.TYPE.values()).index('read')]
    # "CMD LSB" byte. Sourced from Dictionary lookup key by value
    operation = list(utils.OPERATIONS.keys())[
        list(utils.OPERATIONS.values()).index(lookup)]
    # CMD MSB & CMD LSB. No data required for this message type
    payload = [message_type, operation]

    checksum = int(utils.calc_checksum(payload), 16)
    byte_count = calc_byte_count(payload)
    header = [utils.CSCP_HEADER_START, byte_count, recipient_device]

    message = header + payload
    message.append(checksum)
    message = bytes(message)

    return bytes(message)


def calc_byte_count(payload):
    # Surprisingly simple
    return len(payload)


if __name__ == '__main__':
    print(20 * '#' + ' CSCP_encode_1_3 ' + 20 * '#')

    test = ('fader_move', 3, 744)
    print("Test input:", test)
    test_message = Message(test[0], test[1], test[2])
    print("CSCP Message Object:\n", test_message)
