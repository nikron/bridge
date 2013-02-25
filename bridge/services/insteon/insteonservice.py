import logging
import time
import serial
from select import select

from bridgeservice import BridgeService
from services.insteon.insteon_im_protocol import command, insteon_im_protocol
from services.insteon.insteon_im_protocol import device

class InsteonIMService(BridgeService):
    def __init__(self, hub_connection, log_queue):
        super().__init__('insteonimservice', hub_connection, log_queue)
        self.im_ser = None #serial.Serial('/dev/ttyUSB0', 19200)
        self.read_list = [self.hub_connection]

    def run(self):
        while self.spinning:
            (read, write, exception) = select(self.read_list, [], [])
            if self.hub_connection in read:
                self.do_remote_request()
            if self.im_ser in read:
                self.handle_im_communication()

    def handle_im_communication(self):
        rsp = self.im_ser.read(1)

        if rsp == b'\x02':
            to_read = insteon_im_protocol.get_response_length(rsp)
            buf = self.im_ser.read(to_read)
            update = insteon_im_protocol.decode(buf)
            self.update_model(update)

        else:
            logging.error("Didn't get a start of text for first byte, commmunications messed up.")

    def update_model(self, update):
        self.remote_service_method('model', 'update', update)


    def turn_on_lamp(self, deviceId):
        device = device.LampLinc()
        cmd = device.encodeCommand(command.TurnOn, deviceId)

        self.im_ser.write(cmd)
