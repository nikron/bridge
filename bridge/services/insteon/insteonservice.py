import bridgeservice
import logging
import time
import serial
from select import select

class InsteonIMService(bridgeservice.BridgeService):
    def __init__(self, hub_connection, log_queue):
        bridgeservice.BridgeService.__init__(self, 'insteonimservice', hub_connection, log_queue)
        self.im_ser = None #serial.Serial('/dev/ttyUSB0', 19200)
        self.read_list = [self.hub_connection]

    def main(self):
        while self.spinning:
            (read, write, exception) = select(self.read_list, [], [])
            if self.hub_connection in read:
                self.do_callback()
            if self.im_ser in read:
                self.handle_im_communication()

    def handle_im_communication():
        pass
