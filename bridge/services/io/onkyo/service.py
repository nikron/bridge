from bridge.services.io.service import IOService
import eisp

import socket
import logging

class OnkyoReceiverService(IOService):
    PORT = 60128

    def asset_status(self, real_id):
        if real_id == "1":
            self.io_fd.send(eisp.VolumeQuery.encode())

    def read_io(self):
        logging.debug("Reading the interface of {0}.".format(self.name))
        info = eisp.read_info(self.io_fd)
        self.update_model("1", info)

    def _create_fd(self, filename):
        try:
            return socket.create_connection((filename, self.PORT))
        except:
            logging.debug("Could create socket to receiver.")
            return None
