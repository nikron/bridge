"""
Service to handle an Insteon IM.
"""
import logging

from bridge.services.io.service import IOService
from insteon_protocol import insteon_im_protocol
from insteon_protocol.command import im_commands
from binascii import hexlify, unhexlify

import serial

class InsteonIMUpdate():
    def __init__(self, command, relative):
        if relative is not None:
            self.command = relative
            self.relative = command
        else:
            self.command = command
            self.relative = relative

    def __str__(self):
        return "<relative: {0}, command: {1}>".format(self.relative, self.command)

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
            logging.debug("Could not start up serial interface.")
            return None

    def write_command(self, cmd):
        if cmd.is_relative():
            obj = im_commands.IMInsteonCommand.decode(cmd.encode() + b'\x06')
            self.relative[cmd.to_address] = obj

        self.write_io(cmd.encode())

    def asset_info(self, real_id):
        real_id = unhexlify(real_id)

        cmd = im_commands.ProductDataRequest(real_id)

        self.write_command(cmd)

    def turn_off(self, real_id):
        real_id = unhexlify(real_id)
        cmd = im_commands.TurnOff(real_id)

        self.write_command(cmd)

    def turn_on(self, real_id):
        real_id = unhexlify(real_id)

        cmd = im_commands.TurnOnFast(real_id)

        self.write_command(cmd)

    def asset_status(self, real_id):
        real_id = unhexlify(real_id)

        cmd = im_commands.LightStatusRequest(real_id)

        self.write_command(cmd)
