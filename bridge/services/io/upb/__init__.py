from bridge.services.io import IOService
from upb import UPBMessage
from upb.pim import read, PIMMessage

import logging
import serial

class UPBService(IOService):
    BAUD = 4800

    def asset_status(self, real_id):
        pass

    def asset_info(self, real_id):
        pass

    def read_io(self):
        message = read(self.io_fd)
        if message.type == PIMMessage.UPBMESSAGE:
            upb_msg = UPBMessage.create_from_packet(message.packet)
            self.update_model(str(upb_msg.source_id), upb_msg)

    def _create_fd(self, filename):
        try:
            ser = serial.Serial(filename, UPBService.BAUD)
            return ser

        except:
            logging.exception("Could not create the serial connection.")
            return None
