from bridge.services.io import IOService
from upb import UPBMessage, UPBGoToLevel
from upb.pim import read, execute_message, PIMMessage
from upb.device_info import UPBDeviceInfo
import upb.registers

import logging
import serial

class UPBService(IOService):
    BAUD = 4800

    def asset_status(self, real_id):
        pass

    def asset_info(self, real_id):
        device_info = UPBDeviceInfo(int(real_id))
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
        self._execute_message(UPBGoToLevel(int(real_id), level), True)

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

    def _execute_message(self, message, relay):
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
        self.update_model(_upb_id_to_real_id(message.network_id, message.destination_id), message)

def _real_id_to_upb_id(real_id):
    ids = real_id.split('.')
    return int(ids[0]), int(ids[1])

def _upb_id_to_real_id(network_id, destination_id):
    return network_id + '.' + destination_id

def _check_real_id(real_id):
    if type(real_id) is not str:
        return False
    try:
        net, dest = _real_id_to_upb_id(real_id)
        if 0 <= net < 256 and 0 <= dest < 256:
            return True
        else:
            return False

    except (ValueError, IndexError):
        return False
