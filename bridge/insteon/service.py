"""
Insteon io service and its idiom.
"""

from bridge.services.io import IOService

from insteon import insteon_im_protocol
from insteon.command import im_commands

from binascii import hexlify, unhexlify
import logging
import serial

class InsteonIMUpdate():
    """
    Class to encapsulate information sent to the model.
    """
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
    """
    Read and write to an Insteon IM, send updates to model on reading,
    and write commands from the model.
    """

    def __init__(self, name, file_name, hub_connection):
        super().__init__( name, file_name, hub_connection)
        self.relative = {}

    def asset_info(self, real_id):
        real_id = unhexlify(real_id)
        cmd = im_commands.IDRequest(real_id)

        self.write_command(cmd)

    def asset_status(self, real_id):
        real_id = unhexlify(real_id)
        cmd = im_commands.LightStatusRequest(real_id)

        self.write_command(cmd)

    def set_light_level(self, real_id, level):
        """
        Attempt to set the level of the light.

        :param level: Level to go to must be [0, 255]
        :type level: int
        """
        real_id = unhexlify(real_id)
        cmd = im_commands.TurnOnLevel(real_id, bytes([level]))

        self.write_command(cmd)

    def read_io(self):
        """
        Read from the IO.  Note that the INSTEON protocol is stateful, so we must
        keep track of stateful commands that we send, and then deal with that
        here.
        """
        logging.debug("Reading the interface of {0}.".format(self.name))
        buf = insteon_im_protocol.read_command(self.io_fd)

        if buf is not None:
            update_cmd = insteon_im_protocol.decode(buf)

            if not issubclass(type(update_cmd), im_commands.IMInsteonCommand):
                #If it's an im command, we should probably handle it

                frm = update_cmd.from_address
                update = InsteonIMUpdate(update_cmd, self.relative.get(frm, None))
                if update.relative is not None:
                    del self.relative[frm]

                self.update_model(hexlify(frm).decode(), update)

    def turn_off(self, real_id):
        """
        Write a TurnOff command to the IM.

        :param real_id: Device to turn off.
        :type real_id: str
        """
        real_id = unhexlify(real_id)
        cmd = im_commands.TurnOff(real_id)

        self.write_command(cmd)

    def turn_on(self, real_id):
        """
        Write a TurnOn command to the IM.

        :param real_id: Device to turn on.
        :type real_id: str
        """
        real_id = unhexlify(real_id)
        cmd = im_commands.TurnOnFast(real_id)

        self.write_command(cmd)

    def write_command(self, cmd):
        """
        Write a command to the serial port.

        :param cmd: Insteon command to write.
        :type cmd: :class:`InsteonIMCommand`
        """
        if cmd.is_relative():
            obj = im_commands.IMInsteonCommand.decode(cmd.encode() + b'\x06')
            self.relative[cmd.to_address] = obj

        self.write_io(cmd.encode())

    def _create_fd(self, filename):
        try:
            return serial.Serial(filename, 19200)
        except serial.serialutil.SerialException:
            logging.debug("Could not start up serial interface.")
            return None
