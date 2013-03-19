"""
Types of io services, and their idioms.  Used for configuration.
"""
import serial
import logging
from bridge.services.io.insteon import InsteonIMService
from bridge.services.io.insteon.idiom import InsteonIdiom

class IOConfig():
    """
    The model recieves one of these for every running IO service, so that
    it knows how to communicate with it.
    """

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

    def create_serial(self):
        """Create a serial connection."""
        args = self.con_arg.split()
        if len(args) == 2:

            con = serial.Serial(args[0], int(args[1]))

            return con

        else:
            return None

    def create_connection(self):
        """Return the connection/interface used by the service."""
        connections = {
                'serial' : self.create_serial
         }

        try:
            con = connections[self.con]()

            logging.debug("Created connection {0}.".format(repr(con)))

            return con

        except:
            logging.error("Could not create connection {0} with arg {1}".format(repr(self.con), repr(self.con_arg)))

            return None

    def create_service(self, hub_con, log):
        """Return initialized service."""
        io_con = self.create_connection()

        return self.service(self.name, io_con, hub_con, log) 

    def model_idiom(self):
        """
        Create the idiom that the model needs to communicate with the service.
        """
        return self.idiom(self.name)
