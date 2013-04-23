"""
Decode messages from an Insteon PLM.
"""

from __future__ import absolute_import, division, print_function, unicode_literals
import binascii
import logging
import serial
from bridge2.io.insteon.messages import ExtInsteonMessage, InsteonMessage

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
        self._command = command
        self._payload = payload
    
    @property
    def command(self):
        return self._command
    
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

    @property
    def payload(self):
        return self._payload

    def __str__(self):
        return self.__unicode__().encode()
    
    def __unicode__(self):
        fmt = "{0:#02x} PDU: {1}"
        payloads = binascii.hexlify(self._payload)
        return fmt.format(self._command, payloads)

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
        self._dest = dest
        self._message = message
    
    @property
    def dest(self):
        return self._dest
        
    @property
    def message(self):
        return self._message
    
    def __unicode__(self):
        fmt = "SendInsteonMsg PDU: [{0}] {1}"
        dests = binascii.hexlify(self._dest)
        return fmt.format(dests, self._message)

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
        rv._src = payload[0:3]
        rv._dest = payload[3:6]
        rv._message = InsteonMessage.decode(payload[6:9])
        return rv
    
    @property
    def dest(self):
        return self._dest
    
    @property
    def message(self):
        return self._message
    
    @property
    def src(self):
        return self._src
        
    def __unicode__(self):
        fmt = "StdInsteonMessageRcvd PDU: [{0}->{1}] -> {2}"
        srcs = binascii.hexlify(self._src)
        dests = binascii.hexlify(self._dest)
        return fmt.format(srcs, dests, self._message)

class ExtInsteonMessageRcvdModemPDU(ModemPDU):
    def __init__(self, src, dest, message):
        raise NotImplementedError()
        
    @classmethod
    def _decode(cls, command, payload):
        rv = cls.__new__(cls)
        super(cls, rv).__init__(command, payload)
        rv._src = payload[0:3]
        rv._dest = payload[3:6]
        rv._message = ExtInsteonMessage.decode(payload[6:23])
        return rv
        
    @property
    def dest(self):
        return self._dest
    
    @property
    def message(self):
        return self._message
    
    @property
    def src(self):
        return self._src
    
    def __unicode__(self):
        fmt = "ExtInsteonMessageRcvd PDU: [{0}->{1}] -> {2}"
        srcs = binascii.hexlify(self._src)
        dests = binascii.hexlify(self._dest)
        return fmt.format(srcs, dests, self._message)

class SendInsteonMsgRespModemPDU(ModemPDU):
    def __init__(self, dest, message, successful):
        raise NotImplementedError()
    
    @classmethod
    def _decode(cls, command, payload):
        rv = cls.__new__(cls)
        super(cls, rv).__init__(command, payload)
        rv._dest = payload[0:3]
        msgdata = payload[3:-1]
        if len(msgdata) == 17:
            rv._message = ExtInsteonMessage.decode(msgdata)
        else:
            rv._message = InsteonMessage.decode(msgdata)
        rv._successful = (ord(payload[-1]) == 0x06)
        return rv
        
    @property
    def dest(self):
        return self._dest
        
    @property
    def message(self):
        return self._message
        
    @property
    def successful(self):
        return self._successful
        
    def __unicode__(self):
        fmt = "SendInsteonMsgResp PDU: [{0}] {1} -> {2}"
        dests = binascii.hexlify(self._dest)
        stat = "OK" if self._successful else "FAIL"
        return fmt.format(dests, stat, self._message)
        
_pdutable = {
    ModemPDU.STD_INSTEON_MSG_RCVD: (9, StdInsteonMessageRcvdModemPDU),
    ModemPDU.EXT_INSTEON_MSG_RCVD: (23, ExtInsteonMessageRcvdModemPDU),
    ModemPDU.X10_MSG_RCVD: (2, None),
    ModemPDU.LINKING_COMPLETED: (8, None),
    ModemPDU.BUTTON_EVENT_REPORT: (1, None),
    ModemPDU.USER_RESET_DETECTED: (0, None),
    ModemPDU.LINK_CLEANUP_FAILURE_RPT: (5, None),
    ModemPDU.LINK_REC_RESPONSE: (8, None),
    ModemPDU.LINK_CLEANUP_STATUS_RPT: (1, None),
    ModemPDU.GET_IM_INFO: (7, None),
    ModemPDU.SEND_LINK_COMMAND: (4, None),
    ModemPDU.SEND_INSTEON_MSG: (None, SendInsteonMsgRespModemPDU), # var. len.
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

#
# Direct modem interface
#

class ModemInterface(object):    
    def __init__(self, devfile):
        assert isinstance(devfile, unicode)
        self._dev = serial.Serial(devfile, 19200, timeout=0, writeTimeout=0)

    def close(self):
        """Close the underlying serial device."""
        self._dev.close()
        self._dev = None

    def _readmsg(self):
        control = self._readnb(4)
        flags = ord(control[3])
        if flags & 8 != 0:
            body = self._readnb(17) #16 bytes left for ed insteon
        else:
            body = self._readnb(3) #two bytes left for a sd insteon
        return control + body
        
    def _readnb(self, n):
        # Use select to yield until the device is ready, then write
        data = ""
        nread = 0
        while nread < n:
            gevent.select.select([self._dev], [], [])
            data2 = self._dev.read(n)
            nread += len(data2)
            data += data2
        return data

    def recv(self):
        """Read a ModemPDU from the serial interface."""
        # Do a sanity check
        if self._dev == None:
            raise IOError("The device has already been closed")
        
        # Read the PDU header
        magic = ord(self._readnb(1))
        if magic != 0x02:
            raise IOError("STX byte expected when reading PDU")
        cmd = ord(self._readnb(1))
        ctuple = _pdutable.get(cmd)
        if ctuple == None:
            raise IOError("An unrecognized modem PDU was received")
        
        # Read the payload
        if cmd == ModemPDU.SEND_INSTEON_MSG:
            payload = self._readmsg()
        else:
            payload = self._readnb(ctuple[0])
        
        # Return a ModemPDU instance representing the message
        logging.debug("Read buffer {0}".format(repr(payload)))
        return ModemPDU.decode(cmd, payload)

    def send(self, pdu):
        """Transmit a ModemPDU on the serial interface."""
        # Do a sanity check
        assert isinstance(pdu, ModemPDU)
        if self._dev == None:
            raise IOError("The device has already been closed")
            
        # Transmit the data
        self._writenb(pdu.encode())

    def _writenb(self, data):
        # Use select to yield until the device is ready, then write
        n = len(data)
        nwritten = 0
        while nwritten < n:
            gevent.select.select([], [self._dev], [])
            nwritten += self._dev.write(data[nwritten:])
        return n
