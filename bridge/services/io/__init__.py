"""
IO services of bridge.
"""
import logging
from select import select
from abc import abstractmethod, ABCMeta

from bridge.services import BridgeService, MODEL

class IOService(BridgeService, metaclass =ABCMeta):
    """
    An implementation abstraction of :class:`BridgeService`, meant to run IO
    on a particular interface module/device.

    :param name: Name of the IO service.
    :type name: str

    :param name: Path of the file used for I/O.
    :type file_name: str

    :param hub_connection: Connection to BridgeHub.
    :type hub_connection: :class:`Pipe`
    """

    def __init__(self, name, config, hub_connection):
        super().__init__(name, config, hub_connection)
        print(config.io_services[name][1])
        self.io_fd = self._create_fd(config.io_services[name][1])

        self.read_list = [self.hub_connection]
        self.pending = []

    @abstractmethod
    def asset_info(self, real_id):
        """
        Get more info about device (by querying the IO).
        Must be implemented by each IO service.
        Should return information that enables creation of an asset.

        :param real_id: Real ID to get asset information about.
        :type real_id: object
        """
        pass

    @abstractmethod
    def asset_status(self, real_id):
        """
        Find the current status of an asset.
        Should return model updates that update the current
        state of an asset.

        :param real_id: Real ID to get state information about.
        :type real_id: object
        """
        pass


    @abstractmethod
    def read_io(self):
        """
        Read the file, each IO service must implement this.
        """
        pass

    def run(self):
        self.mask_signals()
        self.spinning = True

        if self.io_fd is None:
            self.notify_not_connected()

        else:
            self.notify_connected()

            self.read_list.append(self.io_fd)

        while self.spinning:
            (read, _, _) = select(self.read_list, [], [])
            if self.hub_connection in read:
                self.read_and_do_remote_request()
            if self.io_fd in read:
                self.read_io()

    def update_model(self, real_id, update):
        """
        Send an upate to model, it will changed to a asset transition(s) by an idiom.

        :param real_id: ID used by the the I/O.
        :type real_id: object

        :param update: Update to send to model.
        :type update: object
        """
        logging.debug("Updating model with {0}".format(update))
        self.remote_async_service_method(MODEL, 'io_update', self.name, real_id, update)

    def write_io(self, buf):
        """
        Write a buffer to the file descriptor.

        :param buf: Buffer to write.
        :type buf: bytes
        """
        logging.debug("Writing command {0}.".format(str(buf)))
        if self.io_fd:
            self.io_fd.write(buf)
        else:
            self.pending.append(buf)

    def notify_not_connected(self):
        """
        Notify the model that the this service isn't connected.
        """
        self.remote_async_service_method(MODEL, 'io_service_offline', self.name)

    def notify_connected(self):
        """
        Notify the model that the this service is connected.
        """
        self.remote_async_service_method(MODEL, 'io_service_online', self.name)

    @abstractmethod
    def _create_fd(self, file_name):
        """
        Create the file descriptor from the file name,
        each IO service should implement this.
        """
        pass
