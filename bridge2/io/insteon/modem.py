"""
Decode messages from an Insteon PLM.
"""

from __future__ import absolute_import, division, print_function, unicode_literals
import logging
from insteon_protocol.command.commands import InsteonCommand
from insteon_protocol.command.im_commands import IMInsteonCommand

class ModemPDU(object):
    STD_MSG_RECEIVED = 0x50         # INSTEON Standard Message Received
    EXT_MSG_RECEIVED = 0x51         # INSTEON Extended Message Received
    X10_MSG_RECEIVED = 0x52         # X10 Received
    LINKING_COMPLETED = 0x53        # ALL-Linking Completed
    BUTTON_EVENT_REPORT = 0x54      # Button Event Report
    USER_RESET_DETECTED = 0x55      # User Reset Detected
    LINK_CLEANUP_FAILURE_RPT = 0x56 # ALL-Link Cleanup Failure Report
    LINK_REC_RESPONSE = 0x57        # ALL-Link Record Response
    LINK_CLEANUP_STATUS_RPT = 0x58  # ALL-Link Cleanup Status Report
    GET_IM_INFO = 0x60              # Get IM Info
    SEND_LINK_COMMAND = 0x61        # Send ALL-Link Command
    SEND_STD_EXT_MSG = 0x62         # Send INSTEON Standard or Extended Message
    SEND_X10_MSG = 0x63             # Send X10
    START_LINKING = 0x64            # Start ALL-Linking
    CANCEL_LINKING = 0x65           # Cancel ALL-Linking
    SET_HOST_DEV_CATEGORY = 0x66    # Set Host Device Category
    RESET_IM = 0x67                 # Reset the IM
    SET_ACK_BYTE = 0x68             # Set INSTEON ACK Message Byte
    GET_FIRST_LINK_REC = 0x69       # Get First ALL-Link Record
    GET_NEXT_LINK_REC = 0x6A        # Get Next ALL-Link Record
    SET_IM_CONFIG = 0x6B            # Set IM Configuration
    GET_LINK_REC_FOR_SENDER = 0x6C  # Get ALL-Link Record for Sender
    LED_ON = 0x6D                   # LED On
    LED_OFF = 0x6E                  # LED Off
    MANAGE_LINK_REC = 0x6F          # Manage ALL-Link Record
    SET_NAK_BYTE = 0x70             # Set INSTEON NAK Message Byte
    SET_ACK_BYTE_2 = 0x71           # Set INSTEON ACK Message Two Bytes
    RF_SLEEP = 0x72                 # RF Sleep
    GET_IM_CONFIG = 0x73            # Get IM Configuration
    
    def __init__(self, command, payload):
        self.command = command
        self.payload = payload
    
    @staticmethod
    def readfrom(src, readfn=None):
        """Read a command from an IM interface, needs to support read(number)"""
        
        # Retrieve the message from the serial device
        if readfn == None:
            readfn = src.read
        magic = ord(readfn(src, 1))
        if magic != 0x02:
            raise IOError("STX byte expected when reading PDU")
        cmd = ord(readfn(src, 1))
        ctuple = ModemPDU._receivables.get(cmd)
        if ctuple == None:
            raise IOError("An unrecognized modem PDU was received")
        l, ctor = ctuple
        payload = readfn(src, l)
        
        # Return a ModemPDU instance representing the message
        logging.debug("Read buffer {0}".format(repr(payload)))
        if ctor == None:
            ctor = ModemPDU
        return ctor(cmd, payload)

class ExtMessageModemPDU(ModemPDU):
    def __init__(self, command, payload):
        super(ExtMessageModemPDU, self).__init__(command, payload)
        self.message = InsteonCommand.decode(payload)

class StdMessageModemPDU(ModemPDU):
    def __init__(self, command, payload):
        super(StdMessageModemPDU, self).__init__(command, payload)
        self.message = InsteonCommand.decode(payload)

ModemPDU._receivables = {
    ModemPDU.STD_MSG_RECEIVED: (9, StdMessageModemPDU),
    ModemPDU.EXT_MSG_RECEIVED: (23, ExtMessageModemPDU),
    ModemPDU.X10_MSG_RECEIVED: (2, None),
    ModemPDU.LINKING_COMPLETED: (8, None),
    ModemPDU.BUTTON_EVENT_REPORT: (1, None),
    ModemPDU.USER_RESET_DETECTED: (0, None),
    ModemPDU.LINK_CLEANUP_FAILURE_RPT: (5, None),
    ModemPDU.LINK_REC_RESPONSE: (8, None),
    ModemPDU.LINK_CLEANUP_STATUS_RPT: (1, None)
}
