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

    def __init__(self, name, file_name, hub_connection):
        super().__init__(name, hub_connection)
        self.io_fd = self.create_fd(file_name)

        self.read_list = [self.hub_connection]

        if self.io_fd is None:
            self.notify_not_connected()

        else:
            self.notify_connected()
            self.read_list.append(self.io_fd)


    def run(self):
        super().run()
        self.spinning = True

        while self.spinning:
            (read, _, _) = select(self.read_list, [], [])
            if self.hub_connection in read:
                self.read_and_do_remote_request()
            if self.io_fd in read:
                self.read_io()

    def update_model(self, real_id, update):
        """Send an upate to model, it will be decoded by an idiom."""
        logging.debug("Updating model with {0}".format(update))
        self.remote_async_service_method('model', 'io_update', self.name, real_id, update)

    def create_fd(self, file_name):
        raise NotImplementedError

    def read_io(self):
        """Read the interface, each IO service must implmeenet this."""
        raise NotImplementedError

    def asset_info(self, real_id):
        """Get more info about device."""
        raise NotImplementedError

    def notify_not_connected(self):
        self.remote_async_service_method('model', 'io_service_offline', self.name)

    def notify_connected(self):
        self.remote_async_service_method('model', 'io_service_online', self.name)
