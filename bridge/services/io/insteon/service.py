
import logging

from bridge.services.io.service import IOService
from insteon_protocol import command, insteon_im_protocol
from insteon_protocol.command import commands

class InsteonIMService(IOService):
    def read_interface(self):
        buf = insteon_im_protocol.read_command(self.interface)

        if buf is not None:
            update = insteon_im_protocol.decode(buf)
            logging.debug("Updating model with {0}.".format(repr(update)))
            self.update_model(update)

    def asset_info(self, real_id):
        cmd = commands.ProductDataRequest(real_id).encode()
        logging.debug("Writing command {0}.".format(repr(cmd)))
        self.interface.write(cmd)
