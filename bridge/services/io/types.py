"""
Types of io services, and their idioms.  Used for configuration.
"""
from bridge.services.io.insteon.service import InsteonIMService
from bridge.services.io.insteon.idiom import InsteonIdiom
from bridge.services.io.onkyo import OnkyoReceiverService
from bridge.services.io.onkyo.idiom import OnkyoIdiom

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
        'onkyo' : (OnkyoReceiverService, OnkyoIdiom)
    }

    def __init__(self, name, protocol, file_name):
        self.name = name
        self.io_type = protocol
        self.file_name = file_name

        self.service = self.io_types[self.io_type][0]
        self.idiom = self.io_types[self.io_type][1]

    def create_service(self, hub_con):
        """
        Return initialized service.

        :param hub_con: Hub connection to init io service with.
        :type hub_con: :class:`Pipe`
        """
        return self.service(self.name, self.file_name, hub_con)

    def model_idiom(self):
        """
        Create the idiom that the model needs to communicate with the service.
        """
        return self.idiom(self.name)
