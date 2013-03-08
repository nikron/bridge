from bridge.services.io.service import IOService
from insteon_protocol import command, insteon_im_protocol

class InsteonIMService(IOService):
    def handle_read_interface(self):
        buf = insteon_im_protocol.read_command(self.interface)

        if buf is not None:
            update = insteon_im_protocol.decode(buf)
            self.update_model(update)
