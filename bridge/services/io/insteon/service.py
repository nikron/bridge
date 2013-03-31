"""
Service to handle an Insteon IM.
"""
import logging

from bridge.services.io.service import IOService
from insteon_protocol import insteon_im_protocol
from insteon_protocol.command import im_commands
from binascii import hexlify, unhexlify

import serial

def unhex(func):
    """Decorator to unhexlify real id arguement."""
    return lambda self, real_id: func(self, unhexlify(real_id))

class InsteonIMService(IOService):
    """Methods for translating Command classes into state transitions."""

    def read_io(self):
        logging.debug("Reading the interface of {0}.".format(self.name))
        buf = insteon_im_protocol.read_command(self.io_fd)

        if buf is not None:
            update = insteon_im_protocol.decode(buf)

            if not issubclass(type(update), im_commands.IMInsteonCommand):
                #If it's an im command, we should probably handle it
                self.update_model(hexlify(update.from_address).decode(), update)

    def create_fd(self, filename):
        try:
            return serial.Serial(filename, 19200)
        except serial.serialutil.SerialException:
            return None


    def asset_info(self, real_id):
        cmd = im_commands.ProductDataRequest(real_id).encode()
        logging.debug("Writing command {0}.".format(repr(cmd)))
        self.io_fd.write(cmd)

    @unhex
    def turn_off(self, real_id):
        cmd = im_commands.TurnOff(real_id).encode()
        logging.debug("Writing command {0}.".format(repr(cmd)))
        self.io_fd.write(cmd)

    @unhex
    def turn_on(self, real_id):
        cmd = im_commands.TurnOnFast(real_id).encode()
        logging.debug("Writing command {0}.".format(repr(cmd)))
        self.io_fd.write(cmd)
