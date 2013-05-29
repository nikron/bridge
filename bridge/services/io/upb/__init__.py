from bridge.services.io import IOService
from upb import UPBMessage, UPBGoToLevel
from upb.pim import read, execute_message, PIMMessage

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
            self._update_model_with_packet(message.packet)

    def set_light_level(self, real_id, level):
        _, packets, _ = execute_message(self.io_fd, UPBGoToLevel(real_id, level))
        for packet in packets:
            self._update_model_with_packet(packet)

    def turn_off(self, real_id):
        self.set_light_level(self, 0)

    def turn_on(self, real_id):
        self.set_light_level(self, 100)

    def _create_fd(self, filename):
        try:
            ser = serial.Serial(filename, UPBService.BAUD)
            return ser

        except:
            logging.exception("Could not create the serial connection.")
            return None

    def _update_model_with_packet(self, packet):
        upb_msg = UPBMessage.create_from_packet(packet)
        self.update_model(str(upb_msg.source_id), upb_msg)
