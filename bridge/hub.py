"""
Basically the main of the bridge, starts all subprocesses and then
ensures communications and validity.
"""
import multiprocessing
from multiprocessing.connection import Listener
from select import select

from bridge.services import CLOSE_MESSAGE
from bridge.logging_service import LoggingService, service_configure_logging

from bridge.services.io.types import IOConfig
from bridge.services.model.service import ModelService
from bridge.services.net.http_service import HTTPAPIService
from bridge.services.event import EventService

from collections import namedtuple

ServiceInformation = namedtuple('ServiceInformation', ['connection', 'process'])
address = ("localhost", 10000)


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
        self.start_event()
        self.start_api()

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
                    if ready is self.api_listener:
                        self.handle_api_connection(ready)
                    msg = ready.recv()
                    to = msg.to
                    self.services[to].connection.send(msg)

            except KeyboardInterrupt:
                for con in self.connections:
                    con.send(CLOSE_MESSAGE)

                spinning = False

    def handle_api_connection(connection):
        self.api_connections.append(connection)
        self.connections.append(connection)

    def start_api(self):
        self.api_listener = Listener(address)
        self.connections.append(self.api_listener)
        self.api_connections = []

    def start_event(self):
        its_conn, ours_conn = self.create_connection()
        service = EventService(self.configuration, its_conn)
        self._add_service(ours_conn, service)

        service.start()

    def start_io_services(self):
        """
        Intilialize and fork off IO services.
        """
        for name in self.configuration.io_services:
            its_conn, ours_conn = self.create_connection()
            io_config = IOConfig(self.configuration, name)
            io_service = io_config.create_service(its_conn)
            self._add_service(ours_conn, io_service)

            io_service.start()

    def start_http_service(self):
        """
        Initialize and fork the http service.
        """
        its_conn, ours_conn = self.create_connection()
        service = HTTPAPIService(self.configuration, its_conn)
        self._add_service(ours_conn, service)

        service.start()

    def start_model(self):
        """
        Initialize and fork the model service.
        """
        its_conn, ours_conn = self.create_connection()
        service = ModelService(self.configuration, its_conn)
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
