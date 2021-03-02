# CSCP_utils
# Provides constants for CSCP handling & functions for calculating and validating checksum
# Copyright Peter Walker 2020.
# Feedback/Requests - peter.allan.walker@gmail.com

# See Readme.txt for info on how to use this app.
# See Project_Notes.txt for info on the implementation - how the app works.

CSCP_HEADER_START = 241  # Start Of Header 0xF1
CSCP_HEADER_LENGTH = 3   # CSCP headers consist of 3 bytes
BYTE_COUNT_BYTE = 1      # CSCP header's byte 1 is the byte count
DEVICE_BYTE = 2          # CSCP recipient device byte

CMDMSB = 3  # Command most significant byte
CMDLSB = 4  # Command least significant byte
FDRMSB = 5  # Fader most significant byte
VALMSB = 7  # Fader least significant byte

# DEV BYTE ("device") decimal values
DEVICES = {0: 'mixer', 255: 'controller'}

# CMD MSB decimal values
TYPE = {0: 'read', 128: 'write'}  # 0x00 / 0x80

# CMD LSB decimal values
OPERATIONS = {0: 'fader_move',
              1: 'cut_toggle',
              2: 'main_fader_move',
              5: 'pfl_toggle',
              7: 'read_console_name',
              8: 'read_console_info',
              11: 'read_fader_label',
              12: 'main_pfl_toggle',
              13: 'main_fader_level',
              16: 'available_auxes',
              17: 'fader_path_info',
              18: 'aux_send_toggle',
              19: 'aux_output_level_change',
              20: 'available_mains',
              21: 'main_send_toggle',
              22: 'input_routing_change',
              }

OP_BYTE_COUNTS = {'fader_move': 6,
                  'cut_toggle': 5,
                  'main_fader_move': 6,
                  'pfl_toggle': 5,
                  'read_console_name': 2,
                  'read_console_info': 2,
                  'read_fader_label': 4,
                  'main_pfl_toggle': 5,
                  'aux_send_toggle': 5,
                  'aux_output_level_change': 6,
                  # TODO - get main_send_toggle working
                  # The following wont work if number of paths to pass is < 192
                  # ... should handle BC values better generally(?)
                  'main_send_toggle': 28,

                  'input_routing_change': 5,
                  }

PATH_TYPES = {0: 'No Path',
              1: 'Input Channel',
              2: 'Group',
              3: 'VCA Master',
              4: 'VCA Master over Input Channel',
              5: 'VCA Master over Group',
              6: 'Main',
              7: 'VCA Master over Main',
              8: 'Track',
              9: 'VCA Master over Track',
              10: 'Aux Output',
              11: 'VCA Master over Aux Output',
              }

AUDIO_WIDTHS = {0: 'None',
                1: 'Mono',
                2: 'Stereo',
                6: 'Surround',
                }


def twoscomp(value):
    # Takes a binary string, returns twos compliment
    # TODO - There must be a better way of doing this!

    # Received value may be fewer than 8 bits if there are leading 0's in MSB's
    # I.E. would receive e.g. "0b1111" rather than "0b00001111"
    # ... So need to 'pad_out' any missing MSBs to get 8 bits
    missing = 10 - len(value)  # Number of missing bits (accounting for value being a string prefixed with "0b"
    r = missing * "1"  # Pad out missing 8 bit MSB 0's with 1's (inverting as part of 2's comp)

    for bit in range(2, len(value)):  # Skip the "0b" at the beginning of the binary string and loop through bits
        # invert bits
        if value[bit] == "1":
            r += "0"
        elif value[bit] == "0":
            r += "1"

    # print('DEBUG, CSCP_utils, twoscomp inverted:', result, len(result))

    # Add one to the result
    r = int(r, 2) + 1  # TODO - should be able to +1 without converting to int

    # Handle results > 8 bits TODO - again, there must be a neater way of doing this without all the conversion
    if r > 255:
        r = bin(r)  # Convert to binary
        # print('DEBUG, CSCP_utils, twoscomp +1:', result, len(result))
        r = (r[-8:])  # Keep just the last 8 LSB bits
        r = int(r, 2)  # Convert back

    return hex(r)


def bin_to_dec(value):
    return int(value, 2)


def bin_to_hex(value):
    return hex(int(value, 2))


def calc_checksum(payload):
    """ Calculates the CSCP checksum for a given message payload
        payload - an array of decimal values [cmdmsb, cmdlsb, fdrmsb, fdrlsb, valuemsb...valuelsb]
        All value bytes should be passed, accepts a single value byte for messages with payload byte count of 5
        returns checksum in hex
    """
    checksum = 0
    for item in payload:
        checksum += item

    # print('DEBUG, CSCP_utils:', checksum)
    checksum = twoscomp(bin(checksum))
    # print ('DEBUG, CSCP_utils:', checksum)
    return checksum


if __name__ == '__main__':
    testhex = 0x16d
    binstring = bin(testhex)
    print('Test value \t\thex:', bin_to_hex(binstring), 'dec:', bin_to_dec(binstring), 'binary:', binstring)
    result = twoscomp(binstring)
    print('twos compliment \thex:', bin_to_hex(result), 'dec:', bin_to_dec(result), 'binary:', result)
