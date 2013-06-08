from bridge.services.io import IOService
from bridge.upb import real_id_to_upb_id, upb_id_to_real_id
from upb import UPBMessage, UPBGoToLevel
from upb.pim import read, execute_message, PIMMessage
from upb.device_info import UPBDeviceInfo

import logging
import serial

class UPBService(IOService):
    BAUD = 4800

    def asset_status(self, real_id):
        pass

    def asset_info(self, real_id):
        device_info = UPBDeviceInfo(*real_id_to_upb_id(real_id))
        device_info.retrieve_information(self.io_fd)
        if device_info is not None:
            self.update_model(real_id, device_info)
        else:
            logging.debug("Could not retrieve info from {0}.".format(real_id))

    def read_io(self):
        message = read(self.io_fd)
        if message.type == PIMMessage.UPBMESSAGE:
            self._update_model_with_packet(message.packet)

    def set_light_level(self, real_id, level):
        self._execute_message(real_id, UPBGoToLevel(level), True)

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

    def _execute_message(self, real_id, message, relay):
        message.network_id, message.destination_id = real_id_to_upb_id(real_id)
        success, packets, _ = execute_message(self.io_fd, message)
        logging.debug("Done executing UPBMessage {0}.".format(str(message)))

        if success and relay:
            self._update_model_with_message(message)

        #for packet in packets:
        #    self._update_model_with_packet(packet)

    def _update_model_with_packet(self, packet):
        message = UPBMessage.create_from_packet(packet)
        self._update_model_with_message(message)

    def _update_model_with_message(self, message):
        if message.link: return
        if message.is_report_message():
            self.update_model(upb_id_to_real_id(message.network_id, message.source_id), message)
        else:
            self.update_model(upb_id_to_real_id(message.network_id, message.destination_id), message)
