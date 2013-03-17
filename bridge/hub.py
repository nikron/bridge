"""
Hub process of bridge, used to start all services(calendar, io, net, and model).
Then for processes to communicate, does a simple select over pipes.
In the future this process needs to handle io errors and be able to take
io services up and down.
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
    Accepts a BridgeConfig to then start and manage processes and a threaded
    log service.  Expects to gain control of process when run() is called.
    """


    def __init__(self, configuration):
        """Requires BridgeConfig to set various options."""
        self.logging_service = LoggingService(configuration.log_file, configuration.stderr)
        self.configuration = configuration
        self.connections = []
        self.services = {}

        #to pass to the model later
        self.io_idioms = {}

    def create_connection(self):
        """For services to communicate, they needs a pipe."""
        (its, ours) = multiprocessing.Pipe()

        self.connections.append(ours)

        return (its, ours)

    def add_service(self, con, service):
        """Register a connection and a service to its name."""
        self.services[service.name] = ServiceInformation(con, service)

    def start_model(self):
        """Start the model service. (Actually forks off process)"""
        (its, ours) = self.create_connection()

        #need to pass in the io services it is going to connect to
        #and the the storage driver name
        service = ModelService(self.io_idioms, self.configuration.model_file, self.configuration.model_driver, its, self.logging_service.queue)

        self.add_service(ours, service)

        service.start()

    def start_http_service(self):
        (its, ours) = self.create_connection()
        service = HTTPAPIService(its, self.logging_service.queue)
        self.add_service(ours, service)

        service.start()

    def start_io_services(self):
        """Fork off IO services."""
        for io_config_args in self.configuration.io_services:
            (its, ours) = self.create_connection()

            io_config = IOConfig(*io_config_args)
            io_service =  io_config.create_service(its, self.logging_service.queue)

            self.add_service(ours, io_service)

            self.io_idioms[io_service.name] = io_config.model_idiom()

            io_service.start()

    def run(self):
        """Effectively `main` method of bridge."""

        #start the logging process immediately
        self.logging_service.start()
        service_configure_logging(self.logging_service.queue)

        #start each service
        self.start_io_services()
        self.start_model()
        self.start_http_service()

        self.main_loop()

    def main_loop(self):
        """Loop over pipes to services, relay messages."""
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

        for service in self.services.values():
            service.process.join()
