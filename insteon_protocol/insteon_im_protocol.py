"""
Decode messages from an Insteon PLM.
"""

import logging
import bitstring
from insteon_protocol.command.commands import InsteonCommand
from insteon_protocol.command.im_commands import IMInsteonCommand

#you can only know how many bytes to read after you read a byte
#from the device, so here is a dict that tells you how much you
# need to read
MODEM_COMMANDS = {
                    b'\x50': (9, InsteonCommand.decode), # Received Standard Message
                    b'\x51': (23, InsteonCommand.decode), # Received Extended Message
                    b'\x52': 2, # Received X10
                    b'\x53': 8, # All Link Complete
                    b'\x54': 1, # SET button action
                    b'\x55': 0, # SET reset
                    b'\x56': 5, # All Link Record Response
                    b'\x57': 8, # All Link Record Response
                    b'\x58': 1, # All Link Record Response

                    b'\x60': 7, # Get IM Info
                    b'\x61': 4, # Send All Link Command
                    b'\x62': (-1, IMInsteonCommand.decode), # Send Standard or Extended Message
                    b'\x63': 3, # Send X10
                    b'\x64': 3, # Start All Linking
                    b'\x65': 1, # Cancel All Linking
                    b'\x66': 4, # Set Host device category
                    b'\x67': 1, # Reset the IM
                    b'\x68': 2, # Set INSTEON Ack byte
                    b'\x69': 1, # Get First All Link Record
                    b'\x6A': 1, # Get Next All Link Record
                    b'\x6B': 2, # Set IM Configuration
                    b'\x6C': 1, # Get ALL-link for sender
                    b'\x6D': 2, # LED on
                    b'\x6E': 2, # LED off
                    b'\x6F': 10, # Manage ALL-link record

                    b'\x70': 2, # Set INSTEN NAK Message Byte
                    b'\x71': 3, # Set INSTEN NAK Two Message Byte
                    b'\x72': 1, # RF Sleep
                    b'\x73': 4, # Get IM Configuration
                    }


def read_command(im):
    """
    Read a command from an IM interface, needs to support :func:`read()`.
    """
    buf = None

    rsp = im.read(1)
    if rsp == b'\x02':
        im_cmd = im.read(1)

        if im_cmd == b'\x62': #62 can be either 6 or 20 bytes left to read
            control = im.read(4) #control bytes of insteon messages (includes from adress)
            flag = bitstring.BitString(control[3:4])

            if flag[3]:
                left = im.read(17) #16 bytes left for ed insteon
                buf = rsp + im_cmd + control + left
            else:
                left = im.read(3) #two bytes left for a sd insteon
                buf = rsp + im_cmd + control + left
        else:
            to_read = MODEM_COMMANDS[im_cmd][0]
            buf = im.read(to_read)
            buf = rsp + im_cmd + buf
    else:
        logging.debug("Didn't get a start of text for first byte, communications messed up.")


    logging.debug("Read buffer {0}".format(repr(buf)))
    return buf


def decode(buf):
    """
    Decode a buf into a the corresponding object.
    """
    try:
        return MODEM_COMMANDS[buf[1:2]][1](buf)
    except TypeError:
        return None
    except KeyError:
        return None
