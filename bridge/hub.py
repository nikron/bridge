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

class BridgeHub():
    """
    Accepts a BridgeConfig to then start and manage processes and a threaded
    log service.  Expects to gain control of process when run() is called.
    """

    def __init__(self, configuration):
        """Requires BridgeConfig to set various options."""
        self.logging_service = LoggingService()
        self.configuration = configuration
        self.connections = []
        self.services = {}

        #to pass to the model later
        self.io_idioms = []

    def create_connection(self):
        """For services to communicate, they needs a pipe."""
        (its, ours) = multiprocessing.Pipe()
        self.connections.append(ours)
        return its

    def add_service(self, conn, service):
        self.services[service.name] = (conn, service)

    def start_model(self):
        """Start the model service. (Actually forks off process)"""
        con = self.create_connection()

        #need to pass in the io services it is going to connect to
        #and the the storage driver name
        service = ModelService(self.io_idioms, self.configuration.model_file,
                self.configuration.model_driver, con, self.logging_service.queue)

        self.add_service(con, service)

        service.start()

    def start_io_services(self):
        """Fork off IO services."""
        for io_config_args in self.configuration.io_services:
            conn = self.create_connection()

            io_config = IOConfig(*io_config_args)
            io_service =  io_config.create_service(conn, self.logging_service.queue)

            self.add_service(conn, io_service)

            self.io_idioms.append(io_config.model_idiom())

            io_service.start()

    def run(self):
        #start the logging process immediately
        self.logging_service.start()
        service_configure_logging(self.logging_service.queue)

        #start each service
        self.start_io_services()
        self.start_model()

        self.main_loop()

    #now we just pass messages between processes
    def main_loop(self):
        """Loop over pipes to services, relay messages."""
        spinning = True

        while spinning:
            try:
                (read, write, exception) = select(self.connections, [], [])
                for ready in read:
                    msg = ready.recv()
                    to = msg['to']
                    self.services[to][0].send(msg)

            except KeyboardInterrupt:
                for con in self.connections:
                    con.send(CLOSE_MESSAGE)

                spinning = False

        #this errors for some reason
        for service in self.services.values():
            service[1].join()
