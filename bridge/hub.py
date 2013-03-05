import multiprocessing
from select import select

from bridge.service import CLOSE_MESSAGE, DEBUG_MESSAGE
from bridge.logging_service import LoggingService, service_configure_logging

from bridge.services.io.types import IOConfig
from bridge.services.model.service import ModelService

class BridgeHub():
    def __init__(self, configuration, *args, **kwargs):
        self.logging_service = LoggingService()
        self.configuration = configuration
        self.connections = []
        self.services = {}

        #to pass to the model later
        self.io_idioms = []

    def create_connection(self):
        (its, ours) = multiprocessing.Pipe()
        self.connections.append(ours)
        return its

    def add_service(self, conn, service):
        self.services[service.name] = (conn, service)
        
    def start_model(self):
        conn = self.create_connection()
        
        #need to pass in the io services it is going to connect to
        #and the the storage driver name
        service = ModelService(self.io_idioms, self.configuration.model_file,
            self.configuration.model_driver, conn, self.logging_service.queue)

        self.add_service(conn, service)

    def start_io_services(self):
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
        #for service in self.services.values():
        #    service[1].join()
