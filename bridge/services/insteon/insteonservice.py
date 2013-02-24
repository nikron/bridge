import logging
import time
import serial
from select import select

from bridgeservice import BridgeService
from services.insteon.command_encode import device
from services.insteon.command_encode import command

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

    def turn_on_lamp(self, message):
        deviceId = message['id']

        device = device.LampLinc()
        cmd = device.encodeCommand(command.TurnOn, deviceID)

        self.im_ser.write(cmd)

    def handle_im_communication():
        pass
