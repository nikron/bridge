"""
Service to handle an Insteon IM.
"""
import logging

from bridge.services.io.service import IOService
from insteon_protocol import insteon_im_protocol
from insteon_protocol.command import im_commands

class InsteonIMService(IOService):
    """Methods for translating Command classes into state transitions."""

    def read_interface(self):
        buf = insteon_im_protocol.read_command(self.interface)

        if buf is not None:
            update = insteon_im_protocol.decode(buf)

            if not issubclass(type(update), im_commands.IMInsteonCommand): 
                #If it's an im command, we should probably handle it
                logging.debug("Updating model with {0}.".format(repr(update)))
                self.update_model(update.from_address, update)

    def asset_info(self, real_id):
        cmd = im_commands.ProductDataRequest(real_id).encode()
        logging.debug("Writing command {0}.".format(repr(cmd)))
        self.interface.write(cmd)
