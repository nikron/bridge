"""
Decode messages from an Insteon PLM.
"""

from __future__ import absolute_import, division, print_function, unicode_literals
import logging
from bridge2.io.insteon.messages import InsteonMessage

#
# Modem protocol core
#

class ModemPDU(object):
    STD_INSTEON_MSG_RCVD = 0x50     # INSTEON Standard Message Received
    EXT_INSTEON_MSG_RCVD = 0x51     # INSTEON Extended Message Received
    X10_MSG_RCVD = 0x52             # X10 Received
    LINKING_COMPLETED = 0x53        # ALL-Linking Completed
    BUTTON_EVENT_REPORT = 0x54      # Button Event Report
    USER_RESET_DETECTED = 0x55      # User Reset Detected
    LINK_CLEANUP_FAILURE_RPT = 0x56 # ALL-Link Cleanup Failure Report
    LINK_REC_RESPONSE = 0x57        # ALL-Link Record Response
    LINK_CLEANUP_STATUS_RPT = 0x58  # ALL-Link Cleanup Status Report
    GET_IM_INFO = 0x60              # Get IM Info
    SEND_LINK_COMMAND = 0x61        # Send ALL-Link Command
    SEND_INSTEON_MSG = 0x62         # Send INSTEON Standard or Extended Message
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
    
    @classmethod
    def decode(cls, command, payload):
        # Look up the command type
        ctuple = ModemPDU._receivables.get(command)
        if ctuple == None:
            raise ValueError("The specified command type is not decodable")
        l, ctor = ctuple
        
        # Check the length, w/ special handling for message send responses
        assert isinstance(payload, bytes)
        if command == ModemPDU.SEND_INSTEON_MSG:
            if not len(payload) in (7, 21):
                raise ValueError("'payload' is not of the expected length")
        elif len(payload) != l:
            raise ValueError("'payload' is not of the expected length")
        if cls != ModemPDU and cls != ctor:
            raise ValueError("'command' does not match this PDU type")
            
        # Hand the PDU off to the actual decoder
        if ctor == None:
            return ModemPDU(command, payload)
        return ctor._decode(command, payload)
    
    def encode(self):
        return b"\x02" + chr(self.command) + self.payload
    
    @staticmethod
    def readfrom(src, readfn=None):
        """Read a command from an IM interface, needs to support read(number)"""
        
        # If not told otherwise, use the read function
        if readfn == None:
            readfn = src.read
            
        # Read the PDU header
        magic = ord(readfn(src, 1))
        if magic != 0x02:
            raise IOError("STX byte expected when reading PDU")
        cmd = ord(readfn(src, 1))
        ctuple = ModemPDU._receivables.get(cmd)
        if ctuple == None:
            raise IOError("An unrecognized modem PDU was received")
        
        # Read the payload
        l, ctor = ctuple
        if cmd == ModemPDU.SEND_INSTEON_MSG:
            payload = ModemPDU._readmsg(src, readfn)
        else:
            payload = readfn(src, l)
        
        # Return a ModemPDU instance representing the message
        logging.debug("Read buffer {0}".format(repr(payload)))
        return ModemPDU.decode(cmd, payload)

    @staticmethod
    def _readmsg(src, readfn):
        control = readfn(src, 4)
        flags = ord(control[3])
        if flags & 8 != 0:
            body = readfn(src, 17) #16 bytes left for ed insteon
        else:
            body = readfn(src, 3) #two bytes left for a sd insteon
        return control + body

#
# Transmissible PDUs
#

class SendInsteonMsgModemPDU(ModemPDU):
    def __init__(self, dest, message):
        assert isinstance(dest, bytes)
        assert len(dest) == 3
        cmd = ModemPDU.SEND_INSTEON_MSG
        payload = dest + message.encode()
        super(SendInsteonMsgModemPDU, self).__init__(cmd, payload)
        self.dest = dest
        self.message = message

#
# Receivable PDUs
#

class StdInsteonMessageRcvdModemPDU(ModemPDU):
    def __init__(self, src, dest, message):
        raise NotImplementedError()
        
    @classmethod
    def _decode(cls, command, payload):
        rv = cls.__new__(cls)
        super(cls, rv).__init__(command, payload)
        rv.message = InsteonMessage.decode(payload)
        return rv

class ExtInsteonMessageRcvdModemPDU(ModemPDU):
    def __init__(self, src, dest, message):
        raise NotImplementedError()
        
    @classmethod
    def _decode(cls, command, payload):
        rv = cls.__new__(cls)
        super(cls, rv).__init__(command, payload)
        rv.message = InsteonMessage.decode(payload)
        return rv

class ButtonEventReportModemPDU(ModemPDU):
    BUTTON_SET = 0
    BUTTON_2 = 1
    BUTTON_3 = 2
    EVENT_TAP = 2
    EVENT_HOLD = 3
    EVENT_RELEASE = 4
    
    def __init__(self, command, payload):
        raise NotImplementedError()
        
    @classmethod
    def _decode(cls, button, event):
        rv = cls.__new__(cls)
        super(cls, rv).__init__(command, payload)
        v = ord(payload[0])
        rv.button = v >> 4
        rv.event = v & 0xF
        return rv

class UserResetDetectedModemPDU(ModemPDU):
    def __init__(self):
        raise NotImplementedError()
        
    @classmethod
    def _decode(cls, command, payload):
        rv = cls.__new__(cls)
        super(cls, rv).__init__(command, payload)
        return rv

class LinkCleanupFailureRptModemPDU(ModemPDU):
    def __init__(self, link_group, src):
        raise NotImplementedError()
        
    @classmethod
    def _decode(cls, command, payload):
        rv = cls.__new__(cls)
        super(cls, rv).__init__(command, payload)
        rv.link_group = ord(payload[1])
        rv.src = payload[2:5]
        return rv

class LinkCleanupStatusRptModemPDU(ModemPDU):
    def __init__(self, successful):
        raise NotImplementedError()
        
    @classmethod
    def _decode(cls, command, payload):
        rv = cls.__new__(cls)
        super(cls, rv).__init__(command, payload)
        rv.successful = (ord(payload[0]) == 0x06)
        return rv

class SendInsteonMsgModemRespPDU(ModemPDU):
    def __init__(self, dest, message, successful):
        raise NotImplementedError()
        
    @classmethod
    def _decode(cls, command, payload):
        rv = cls.__new__(cls)
        super(cls, rv).__init__(command, payload)
        rv.dest = payload[0:3]
        rv.message = InsteonMessage.decode(payload[3:6])
        rv.successful = (ord(payload[6]) == 0x06)
        return rv
        
ModemPDU._receivables = {
    ModemPDU.STD_INSTEON_MSG_RCVD: (9, StdInsteonMessageRcvdModemPDU),
    ModemPDU.EXT_INSTEON_MSG_RCVD: (23, ExtInsteonMessageRcvdModemPDU),
    ModemPDU.X10_MSG_RCVD: (2, None),
    ModemPDU.LINKING_COMPLETED: (8, None),
    ModemPDU.BUTTON_EVENT_REPORT: (1, ButtonEventReportModemPDU),
    ModemPDU.USER_RESET_DETECTED: (0, UserResetDetectedModemPDU),
    ModemPDU.LINK_CLEANUP_FAILURE_RPT: (5, LinkCleanupFailureRptModemPDU),
    ModemPDU.LINK_REC_RESPONSE: (8, None),
    ModemPDU.LINK_CLEANUP_STATUS_RPT: (1, LinkCleanupStatusRptModemPDU),
    ModemPDU.GET_IM_INFO: (7, None),
    ModemPDU.SEND_LINK_COMMAND: (4, None),
    ModemPDU.SEND_INSTEON_MSG: (None, SendInsteonMsgModemRespPDU), # var. len.
    ModemPDU.SEND_X10_MSG: (3, None),
    ModemPDU.START_LINKING: (3, None),
    ModemPDU.CANCEL_LINKING: (1, None),
    ModemPDU.SET_HOST_DEV_CATEGORY: (4, None),
    ModemPDU.RESET_IM: (1, None),
    ModemPDU.SET_ACK_BYTE: (2, None),
    ModemPDU.GET_FIRST_LINK_REC: (1, None),
    ModemPDU.GET_NEXT_LINK_REC: (1, None),
    ModemPDU.SET_IM_CONFIG: (2, None),
    ModemPDU.GET_LINK_REC_FOR_SENDER: (1, None),
    ModemPDU.LED_ON: (2, None),
    ModemPDU.LED_OFF: (2, None),
    ModemPDU.MANAGE_LINK_REC: (10, None),
    ModemPDU.SET_NAK_BYTE: (2, None),
    ModemPDU.SET_ACK_BYTE_2: (3, None),
    ModemPDU.RF_SLEEP: (1, None),
    ModemPDU.GET_IM_CONFIG: (4, None)
}
