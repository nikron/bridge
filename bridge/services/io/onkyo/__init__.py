"""
Handle Onkyo SR-609 receivers.
"""

from bridge.services.io import IOService
import eisp

import socket
import logging

class OnkyoReceiverService(IOService):
    PORT = 60128

    def asset_status(self, real_id):
        if real_id == "1":
            self.io_fd.send(eisp.VOLUME_QUERY)

    def read_io(self):
        logging.debug("Reading the interface of {0}.".format(self.name))
        message = eisp.read_message(self.io_fd)
        self.update_model('1', message.decipher())

    def set_volume(self, real_id, volume):
        self.io_fd.send(eisp.EISPMessage(eisp.VOLUME_LEVEL_COMMAND(volume)).encode())

    def _create_fd(self, filename):
        try:
            sock =  socket.create_connection((filename, self.PORT))
            return sock
        except:
            print('wtf')
            logging.exception("Could create socket to receiver.")
            return None
