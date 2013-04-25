"""
Basically the main of the bridge, starts all subprocesses and then
ensures communications and validity.
"""
import multiprocessing
from select import select

from bridge.service import CLOSE_MESSAGE
from bridge.logging_service import LoggingService, service_configure_logging

from bridge.services.io.types import IOConfig
from bridge.services.model.service import ModelService
from bridge.services.net.http_service import HTTPAPIService

from collections import namedtuple

ServiceInformation = namedtuple('ServiceInformation', ['connection', 'process'])

class BridgeHub():
    """
    Uses a BridgeConfiguration to configure and start bridge subprocesses.

    :param configuration: Configuration object used to configure services.
    :type configuration: :class:`BridgeConfiguration`
    """

    def __init__(self, configuration):
        self.logging_service = LoggingService(configuration.log_file, configuration.stderr)
        self.configuration = configuration
        self.connections = []
        self.services = {}
        self.io_idioms = {} #to pass to the model later

    def create_connection(self):
        """
        Creates a pipe, saves the end that the bridge uses.

        :return: Sockets used to communicate to services.
        :rtype: :class:`Pipe`
        """
        its_conn, ours_conn = multiprocessing.Pipe()

        self.connections.append(ours_conn)

        return its_conn, ours_conn

    def run(self):
        """
        Effective main of Bridge, starts services and starts select loop.
        """
        #start the logging process immediately
        self.logging_service.start()
        service_configure_logging(self.logging_service.queue)

        #start each service
        self.start_io_services()
        self.start_model()
        self.start_http_service()

        self.main_loop()

    def main_loop(self):
        """
        Loop over pipes to services, relay messages.
        """
        spinning = True

        #now we just pass messages between processes
        while spinning:
            try:
                (read, _, _) = select(self.connections, [], [])
                for ready in read:
                    msg = ready.recv()
                    to = msg.to
                    self.services[to].connection.send(msg)

            except KeyboardInterrupt:
                for con in self.connections:
                    con.send(CLOSE_MESSAGE)

                spinning = False

    def start_http_service(self):
        """
        Initialize and fork the http service.
        """
        its_conn, ours_conn = self.create_connection()
        service = HTTPAPIService(its_conn)
        self._add_service(ours_conn, service)

        service.start()

    def start_io_services(self):
        """
        Intilialize and fork off IO services.
        """
        for io_config_args in self.configuration.io_services:
            its_conn, ours_conn = self.create_connection()
            io_config = IOConfig(*io_config_args)
            io_service = io_config.create_service(its_conn)
            self._add_service(ours_conn, io_service)
            self.io_idioms[io_service.name] = io_config.model_idiom()

            io_service.start()

    def start_model(self):
        """
        Initialize and fork the model service.
        """
        its_conn, ours_conn = self.create_connection()
        service = ModelService(self.io_idioms, self.configuration.model_dir(), its_conn)
        self._add_service(ours_conn, service)

        service.start()

    def _add_service(self, con, service):
        """
        Register a connection and a service to its name.

        :param con: Connection used to used to send messages to a service.
        :type con: :class:`Pipe`

        :param service: Service to store
        :type service: :class:`BridgeService`
        """
        self.services[service.name] = ServiceInformation(con, service)
