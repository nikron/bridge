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

    def __init__(self, name, protocol, file_name):
        self.name = name
        self.io_type = protocol
        self.file_name = file_name

        self.service = self.io_types[self.io_type][0]
        self.idiom = self.io_types[self.io_type][1]

    def create_service(self, hub_con):
        """Return initialized service."""

        return self.service(self.name, self.file_name, hub_con)

    def model_idiom(self):
        """
        Create the idiom that the model needs to communicate with the service.
        """
        return self.idiom(self.name)
