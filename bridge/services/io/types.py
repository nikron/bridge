import serial
import logging
from bridge.services.io.insteon import InsteonIMService
from bridge.services.io.insteon_idiom import InsteonIdiom


class IOConfig():
    io_types = {
        'insteon' : (InsteonIMService, InsteonIdiom)
    }
    def __init__(self, name, protocol, con, con_arg):
        self.name = name
        self.io_type = protocol
        self.con = con
        self.con_arg = con_arg
        
        self.service = self.io_types[self.io_type][0]
        self.idiom = self.io_types[self.io_type][1]

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
        io_con = self.create_connection()

        return self.service(self.name, io_con, hub_con, log) 

    #information the model needs for this process
    def model_idiom(self):
        return self.idiom()
