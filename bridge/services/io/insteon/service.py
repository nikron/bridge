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

class InsteonIMUpdate():
    def __init__(self, command, relative):
        self.command = command
        self.relative = relative

class InsteonIMService(IOService):
    """Methods for translating Command classes into state transitions."""

    def __init__(self, name, file_name, hub_connection):
        super().__init__( name, file_name, hub_connection)
        self.relative = {}

    def read_io(self):
        logging.debug("Reading the interface of {0}.".format(self.name))
        buf = insteon_im_protocol.read_command(self.io_fd)

        if buf is not None:
            update_cmd = insteon_im_protocol.decode(buf)

            if not issubclass(type(update_cmd), im_commands.IMInsteonCommand):
                #If it's an im command, we should probably handle it

                frm = update_cmd.from_address
                update = InsteonIMUpdate(update_cmd, self.relative.get(frm, None))
                self.update_model(hexlify(frm).decode(), update)

    def _create_fd(self, filename):
        try:
            return serial.Serial(filename, 19200)
        except serial.serialutil.SerialException:
            return None

    def write_command(self, cmd):
        if cmd.is_relative():
            self.relative[cmd.to_address] = cmd

        self.write_io(cmd.encode())

    @unhex
    def asset_info(self, real_id):
        cmd = im_commands.ProductDataRequest(real_id)

        self.write_command(cmd)

    @unhex
    def turn_off(self, real_id):
        cmd = im_commands.TurnOff(real_id)

        self.write_command(cmd)

    @unhex
    def turn_on(self, real_id):
        cmd = im_commands.TurnOnFast(real_id)

        self.write_command(cmd)
