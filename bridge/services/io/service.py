"""
The base class for io services.
"""
import logging
from select import select

from bridge.service import BridgeService

#pylint: disable=R0921
class IOService(BridgeService):
    """
    An abstraction of a BridgeService, meant to run IO
    on a paticular interface.
    """

    def __init__(self, name, interface, hub_connection, log_queue):
        super().__init__(name, hub_connection, log_queue)
        self.interface = interface

        self.read_list = [self.hub_connection]

        if interface is not None:
            self.read_list.append(self.interface)

    def run(self):
        logging.debug("Starting {0}".format(self.name))
        IOService.run()
        self.spinning = True

        while self.spinning:
            (read, _, _) = select(self.read_list, [], [])
            if self.hub_connection in read:
                self.do_remote_request()
            if self.interface in read:
                print("hey")
                self.read_interface()

    def update_model(self, real_id, update):
        """Send an upate to model, it will be decoded by an idiom."""
        logging.debug("Updating model with {0}".format(repr(update)))
        self.remote_service_method('model', 'io_update', self.name, real_id, update)

    def read_interface(self):
        """Read the interface, each IO service must implmeenet this."""
        raise NotImplementedError

    def asset_info(self, real_id):
        """Get more info about device."""
        raise NotImplementedError
