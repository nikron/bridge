import logging
import serial
import bitstring
from select import select

from bridgeservice import BridgeService
from insteon_protocol import command, insteon_im_protocol, device

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
            
            im_cmd = self.im_ser.read(1)
            if b == b'\x62':
                control = self.im_ser.read(4)
                bs = bitstring.BitString(c[3])

                if bs[7] == True:
                    left = self.im_ser.read(16)    
                    buf = im_cmd + control + left
                else:
                    left = self.im_ser.read(2)    
                    buf = im_cmd + control + left
            else: 
                to_read = insteon_im_protocol.get_response_length(b)
                buf = self.im_ser.read(to_read)
                buf = im_cmd + buf

            update = insteon_im_protocol.decode(buf)
            self.update_model(update) #{'id' : b'\asdfsadf\', 'status' : 100 }

        else:
            logging.error("Didn't get a start of text for first byte, communications messed up.")

    def update_model(self, update):
        self.remote_service_method('model', 'update', update)


    def turn_on_lamp(self, deviceId):
        device = device.LampLinc()
        cmd = device.encodeCommand(command.TurnOn, deviceId)

        self.im_ser.write(cmd)
