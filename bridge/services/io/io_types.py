import serial
import logging
from .insteon_service import InsteonIMService

class IOConfig():
    def __init__(self, name, protocol, con, con_arg):
        self.name = name
        self.io_type = protocol
        self.con = con
        self.con_arg = con_arg

    def create_connection(self):
        connections = { 
                'serial' : serial.Serial 
         }

        try:
            con = connections[self.con](self.con_arg)
            return con
        except:
            return None

    def create_service(self, hub_con, log):
        io_types = {
            'insteon' : InsteonIMService
        }

        io_con = self.create_connection()

        return io_types[self.io_type](self.name, io_con, hub_con, log) 

    #information the model needs for this process
    def model_information(self):
        pass
