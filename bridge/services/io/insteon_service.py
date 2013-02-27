from services.io import io_service
from insteon_protocol import command, insteon_im_protocol, device

class InsteonIMService(io_service.IOService):
    def handle_read_interface(self):
        buf = inseon_im_protocol.read_command(self.im_ser)

        if buf is not None:
            update = insteon_im_protocol.decode(buf)
            self.update_model(update) #{'id' : b'\asdfsadf\', 'status' : 100 }
