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

        #registering the callbacks (all the commands that can be sent over device)
        self.register_callback('lamp on', self.turn_on_lamp)

    def main(self):
        while self.spinning:
            (read, write, exception) = select(self.read_list, [], [])
            if self.hub_connection in read:
                self.do_callback()
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
        mupdate = {'to' : 'modelservice', 'action' : 'update', 'update' : update)
        self.hub_connection.send(mupdate)

    def turn_on_lamp(self, message):
        deviceId = message['id']

        device = device.LampLinc()
        cmd = device.encodeCommand(command.TurnOn, deviceID)

        self.im_ser.write(cmd)

