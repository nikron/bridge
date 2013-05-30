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
        self._execute_message(UPBGoToLevel(int(real_id), level))

    def turn_off(self, real_id):
        self.set_light_level(real_id, 0)

    def turn_on(self, real_id):
        self.set_light_level(real_id, 100)

    def _create_fd(self, filename):
        try:
            ser = serial.Serial(filename, UPBService.BAUD)
            return ser

        except:
            logging.exception("Could not create the serial connection.")
            return None

    def _execute_message(self, message):
        success, packets, _ = execute_message(self.io_fd, message)
        logging.debug("Done executing UPBMessage {0}.".format(str(message)))

        if success:
            self._update_model_with_message(message)
        logging.debug(packets)

    def _update_model_with_packet(self, packet):
        message = UPBMessage.create_from_packet(packet)
        self.update_model(str(message.source_id), message)

    def _update_model_with_message(self, message):
        self.update_model(str(message.destination_id), message)
