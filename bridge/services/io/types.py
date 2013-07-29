"""
Types of io services, and their idioms.  Used for configuration.
"""
from bridge.insteon.service import InsteonIMService
from bridge.insteon.idiom import InsteonIdiom
from bridge.onkyo.service import OnkyoReceiverService
from bridge.onkyo.idiom import OnkyoIdiom
from bridge.upb.service import UPBService
from bridge.upb.idiom import UPBIdiom

class IOConfig():
    """
    Find and init an IO service and idiom associated with a protocl/ IO type.

    :param name: IO service name.
    :type name: str

    :param protocol: Protocol to find service/idiom combo.
    :type protocol: str

    :param file_name: Path the IO service should control.
    :type file_name: str
    """

    io_types = {
        'insteon' : (InsteonIMService, InsteonIdiom),
        'onkyo' : (OnkyoReceiverService, OnkyoIdiom),
        'upb' : (UPBService, UPBIdiom)
    }

    def __init__(self, config, name):
        self.name = name
        self.config = config
        self.io_type = config.io_services[name][0]

        self.service = self.io_types[self.io_type][0]
        self.idiom = self.io_types[self.io_type][1]

    def create_service(self, hub_con):
        """
        Return initialized service.

        :param hub_con: Hub connection to init io service with.
        :type hub_con: :class:`Pipe`
        """
        return self.service(self.name, self.config, hub_con)

    @classmethod
    def model_idiom(cls, protocol, name):
        """
        Create the idiom that the model needs to communicate with the service.
        """
        return cls.io_types[protocol][1](name)
